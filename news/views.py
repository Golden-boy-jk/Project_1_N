from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from rest_framework import permissions, viewsets

from .forms import TimezoneForm
from .models import Category, Post
from .serializers import PostSerializer
from .tasks import send_new_post_notifications  # Celery-задача (асинхронно)

# ────────────────────────────────────────────────────────────────────────────────
# Домашняя/общие страницы
# ────────────────────────────────────────────────────────────────────────────────


@cache_page(60)
def home(request):
    return render(request, "home.html")


# ────────────────────────────────────────────────────────────────────────────────
# Категории
# ────────────────────────────────────────────────────────────────────────────────


@cache_page(600)
def category_detail(request, pk: int):
    """Страница одной категории (pk унифицируем с urls.py)."""
    category = get_object_or_404(Category, pk=pk)
    return render(request, "category_detail.html", {"category": category})


@cache_page(600)
def category_list(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "categories/category_list.html", {"categories": categories})


@login_required
def subscribe_category(request, pk: int):
    category = get_object_or_404(Category, pk=pk)
    category.subscribe(request.user)
    messages.success(
        request, _("Вы подписались на категорию «%(name)s».") % {"name": category.name}
    )
    return redirect("category_detail", pk=category.pk)


@login_required
def unsubscribe_category(request, pk: int):
    category = get_object_or_404(Category, pk=pk)
    category.unsubscribe(request.user)
    messages.info(
        request, _("Вы отписались от категории «%(name)s».") % {"name": category.name}
    )
    return redirect("category_detail", pk=category.pk)


# ────────────────────────────────────────────────────────────────────────────────
# Аутентификация/выход
# ────────────────────────────────────────────────────────────────────────────────


def custom_logout(request):
    logout(request)
    return render(request, "news/logout.html")


# ────────────────────────────────────────────────────────────────────────────────
# Новости (список/поиск/детали)
# ────────────────────────────────────────────────────────────────────────────────


@cache_page(300)
def news_list(request):
    qs = (
        Post.objects.select_related("author__user")
        .prefetch_related("categories")
        .order_by("-created_at")
    )
    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "news_list.html", {"page_obj": page_obj})


def news_detail(request, pk: int):
    post = get_object_or_404(
        Post.objects.select_related("author__user").prefetch_related("categories"),
        pk=pk,
    )
    return render(request, "news_detail.html", {"post": post})


@cache_page(120)
def news_search(request):
    """Поиск с простыми фильтрами; дату лучше валидировать в форме, но для DEV оставим так."""
    query = request.GET.get("q", "")
    author_name = request.GET.get("author", "")
    date_after = request.GET.get("date_after", "")
    post_type = request.GET.get("type", "")

    filters = Q()
    if query:
        filters &= Q(title__icontains=query) | Q(text__icontains=query)
    if author_name:
        filters &= Q(author__user__username__icontains=author_name)
    if date_after:
        filters &= Q(created_at__gte=date_after)
    if post_type:
        filters &= Q(type=post_type)

    qs = (
        Post.objects.filter(filters)
        .select_related("author__user")
        .prefetch_related("categories")
        .order_by("-created_at")
    )
    paginator = Paginator(qs, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "news/news_search.html", {"page_obj": page_obj})


# ────────────────────────────────────────────────────────────────────────────────
# CRUD постов
# ────────────────────────────────────────────────────────────────────────────────


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    fields = ["title", "text", "categories"]
    template_name = "news/news_form.html"
    success_url = reverse_lazy("news_list")
    # Можно оставить кастомный пермисс или использовать стандартный add_post
    permission_required = "news.can_create_post"

    def form_valid(self, form):
        # Проверка, что пользователь — автор
        if not self.request.user.groups.filter(name="authors").exists():
            messages.error(self.request, _("У вас нет прав на создание поста."))
            return redirect("home")

        # Назначаем автора
        if hasattr(self.request.user, "author"):
            form.instance.author = self.request.user.author
        else:
            messages.error(self.request, _("У вашего пользователя нет профиля автора."))
            return redirect("home")

        # Тип поста берём из extra_context (см. urls.py) или по умолчанию оставляем ARTICLE
        post_type = None
        if hasattr(self, "extra_context") and self.extra_context:
            post_type = self.extra_context.get("type")
        if post_type in {"NW", "AR"}:
            form.instance.type = post_type

        response = super().form_valid(form)

        # Асинхронные уведомления подписчикам
        send_new_post_notifications.delay(self.object.pk)

        messages.success(self.request, _("Пост успешно создан."))
        return response


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "text", "categories"]
    template_name = "news/news_form.html"
    success_url = reverse_lazy("news_list")
    permission_required = "news.change_post"

    def form_valid(self, form):
        if not self.request.user.groups.filter(name="authors").exists():
            messages.error(self.request, _("У вас нет прав на редактирование поста."))
            return redirect("home")
        messages.success(self.request, _("Пост обновлён."))
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "news/news_confirm_delete.html"
    success_url = reverse_lazy("news_list")
    permission_required = "news.delete_post"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Пост удалён."))
        return super().delete(request, *args, **kwargs)


# ────────────────────────────────────────────────────────────────────────────────
# Вспомогательные представления
# ────────────────────────────────────────────────────────────────────────────────


class PostDetailView(DetailView):
    model = Post
    template_name = "news/post_detail.html"
    context_object_name = "post"


def post_list(request):
    """Пример списка с фильтрацией по категории (правильное имя связи: categories)."""
    category_name = request.GET.get("category")
    qs = Post.objects.all()
    if category_name:
        qs = qs.filter(categories__name=category_name)

    categories = Category.objects.all().order_by("name")
    return render(
        request,
        "yourapp/post_list.html",  # если есть такой шаблон; иначе замени путь
        {"posts": qs, "categories": categories},
    )


def set_language(request):
    """Простая смена языка без i18n_patterns (dev-вариант)."""
    lang_code = request.GET.get("lang", "ru")
    activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return redirect(request.META.get("HTTP_REFERER", "/"))


def set_timezone(request):
    """Смена таймзоны в профиле пользователя (учебный dev-вариант)."""
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
        initial = {
            "timezone": getattr(
                getattr(request.user, "profile", None), "timezone", "Europe/Moscow"
            )
        }
        form = TimezoneForm(initial=initial)

    return render(request, "set_timezone.html", {"form": form})


# ────────────────────────────────────────────────────────────────────────────────
# DRF
# ────────────────────────────────────────────────────────────────────────────────


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class NewsViewSet(viewsets.ModelViewSet):
    """Только посты типа 'Новость'."""

    queryset = (
        Post.objects.filter(type="NW")
        .select_related("author__user")
        .prefetch_related("categories")
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleViewSet(viewsets.ModelViewSet):
    """Только посты типа 'Статья'."""

    queryset = (
        Post.objects.filter(type="AR")
        .select_related("author__user")
        .prefetch_related("categories")
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all().select_related("author__user").prefetch_related("categories")
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
