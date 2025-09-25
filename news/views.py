from __future__ import annotations

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .forms import TimezoneForm
from .models import Category, Post
from .serializers import PostSerializer

# ────────────────────────────────────────────────────────────────────────────────
# Домашняя / общие страницы
# ────────────────────────────────────────────────────────────────────────────────


@cache_page(60)
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


# ────────────────────────────────────────────────────────────────────────────────
# Категории
# ────────────────────────────────────────────────────────────────────────────────


@cache_page(600)
def category_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Страница одной категории."""
    category = get_object_or_404(
        Category.objects.prefetch_related("subscribers"), pk=pk
    )
    return render(request, "categories/detail.html", {"category": category})


@cache_page(600)
def category_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all().order_by("name")
    return render(request, "categories/list.html", {"categories": categories})


@login_required
def subscribe_category(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk)
    category.subscribe(request.user)
    messages.success(
        request, _("Вы подписались на категорию «%(name)s».") % {"name": category.name}
    )
    return redirect("category_detail", pk=category.pk)


@login_required
def unsubscribe_category(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk)
    category.unsubscribe(request.user)
    messages.info(
        request, _("Вы отписались от категории «%(name)s».") % {"name": category.name}
    )
    return redirect("category_detail", pk=category.pk)


# ────────────────────────────────────────────────────────────────────────────────
# Аутентификация / выход
# ────────────────────────────────────────────────────────────────────────────────


def custom_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return render(request, "news/logout.html")


# ────────────────────────────────────────────────────────────────────────────────
# Новости (список / поиск / детали)
# ────────────────────────────────────────────────────────────────────────────────


def _post_base_qs() -> QuerySet[Post]:
    """Базовый queryset для Post с жадными загрузками."""
    return (
        Post.objects.select_related("author__user")
        .prefetch_related("categories")
        .order_by("-created_at")
    )


@cache_page(300)
def news_list(request: HttpRequest) -> HttpResponse:
    qs = _post_base_qs()
    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "news/list.html", {"page_obj": page_obj})


def news_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(_post_base_qs(), pk=pk)
    return render(request, "news/detail.html", {"post": post})


def _parse_iso_date(value: str) -> datetime | None:
    """Безопасный парсер ISO-даты для фильтра `created_at__gte`."""
    if not value:
        return None
    try:
        # поддержим YYYY-MM-DD и полные ISO-строки
        return datetime.fromisoformat(value)  # tz-aware тоже ок — Django нормализует
    except ValueError:
        return None


@cache_page(120)
def news_search(request: HttpRequest) -> HttpResponse:
    """
    Поиск с простыми фильтрами. Дату валидируем безопасно.
    Шаблон: templates/news/search.html
    """
    query = request.GET.get("q", "").strip()
    author_name = request.GET.get("author", "").strip()
    date_after_raw = request.GET.get("date_after", "").strip()
    post_type = request.GET.get("type", "").strip().upper()

    filters = Q()
    if query:
        filters &= Q(title__icontains=query) | Q(text__icontains=query)
    if author_name:
        filters &= Q(author__user__username__icontains=author_name)

    date_after = _parse_iso_date(date_after_raw)
    if date_after:
        filters &= Q(created_at__gte=date_after)
    elif date_after_raw:
        messages.warning(request, _("Неверный формат даты. Используйте YYYY-MM-DD."))

    if post_type in {"NW", "AR"}:
        filters &= Q(type=post_type)

    qs = _post_base_qs().filter(filters)
    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "q": query,
        "author": author_name,
        "date_after": date_after_raw,
        "type": post_type,
    }
    return render(request, "news/search.html", context)


# ────────────────────────────────────────────────────────────────────────────────
# CRUD постов
# ────────────────────────────────────────────────────────────────────────────────


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    fields = ["title", "text", "categories"]
    template_name = "news/form.html"
    success_url = reverse_lazy("news_list")
    permission_required = "news.add_post"

    # ожидаем extra_context={"type": "NW"} или {"type": "AR"} в urls.py
    def form_valid(self, form):
        user = self.request.user

        if not user.groups.filter(name="authors").exists():
            messages.error(self.request, _("У вас нет прав на создание поста."))
            return redirect("home")

        if hasattr(user, "author"):
            form.instance.author = user.author
        else:
            messages.error(self.request, _("У вашего пользователя нет профиля автора."))
            return redirect("home")

        post_type = None
        if getattr(self, "extra_context", None):
            post_type = self.extra_context.get("type")
        if post_type in {"NW", "AR"}:
            form.instance.type = post_type

        response = super().form_valid(form)
        messages.success(self.request, _("Пост успешно создан."))
        return response


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "text", "categories"]
    template_name = "news/form.html"
    success_url = reverse_lazy("news_list")
    permission_required = "news.change_post"

    def get_queryset(self) -> QuerySet[Post]:
        """
        Ограничим редактирование постами текущего автора.
        Если нужно, чтобы модераторы могли всё — расширь проверку по группам/правам.
        """
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, "author"):
            return qs.filter(author=user.author)
        return qs.none()

    def form_valid(self, form):
        if not self.request.user.groups.filter(name="authors").exists():
            messages.error(self.request, _("У вас нет прав на редактирование поста."))
            return redirect("home")
        messages.success(self.request, _("Пост обновлён."))
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "news/confirm_delete.html"
    success_url = reverse_lazy("news_list")
    permission_required = "news.delete_post"

    def get_queryset(self) -> QuerySet[Post]:
        user = self.request.user
        qs = super().get_queryset()
        if hasattr(user, "author"):
            return qs.filter(author=user.author)
        return qs.none()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Пост удалён."))
        return super().delete(request, *args, **kwargs)


# ────────────────────────────────────────────────────────────────────────────────
# Вспомогательные представления
# ────────────────────────────────────────────────────────────────────────────────


class PostDetailView(DetailView):
    model = Post
    template_name = "news/detail.html"
    context_object_name = "post"


def post_list(request: HttpRequest) -> HttpResponse:
    """
    Список постов с фильтрацией по категории через query-param `?category=...`.
    """
    category_name = request.GET.get("category", "").strip()
    qs = _post_base_qs()
    if category_name:
        qs = qs.filter(categories__name__icontains=category_name)

    categories = Category.objects.all().order_by("name")
    return render(
        request,
        "news/post_list.html",
        {"posts": qs, "categories": categories, "selected_category": category_name},
    )


def set_language(request: HttpRequest) -> HttpResponse:
    """Смена языка (dev-вариант без i18n_patterns)."""
    lang_code = request.GET.get("lang", "ru")
    activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def set_timezone(request: HttpRequest) -> HttpResponse:
    """
    Смена таймзоны. Если у тебя таймзона лежит в CustomUser, замени обращение к profile.
    """
    if request.method == "POST":
        form = TimezoneForm(request.POST)
        if form.is_valid():
            tz = form.cleaned_data["timezone"]
            if hasattr(request.user, "profile"):
                request.user.profile.timezone = tz
                request.user.profile.save(update_fields=["timezone"])
                messages.success(request, _("Часовой пояс обновлён."))
            else:
                messages.error(request, _("Профиль пользователя не найден."))
            return redirect("home")
    else:
        initial_tz = getattr(
            getattr(request.user, "profile", None), "timezone", "Europe/Moscow"
        )
        form = TimezoneForm(initial={"timezone": initial_tz})

    return render(request, "settings/set_timezone.html", {"form": form})


# ────────────────────────────────────────────────────────────────────────────────
# DRF ViewSets
# ────────────────────────────────────────────────────────────────────────────────


class NewsViewSet(viewsets.ModelViewSet):
    """Только посты типа 'Новость'."""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[Post]:
        return _post_base_qs().filter(type="NW")


class ArticleViewSet(viewsets.ModelViewSet):
    """Только посты типа 'Статья'."""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[Post]:
        return _post_base_qs().filter(type="AR")


class PostViewSet(viewsets.ModelViewSet):
    """Все посты."""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[Post]:
        return _post_base_qs()
