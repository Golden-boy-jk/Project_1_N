from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from datetime import datetime
from .models import Post
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin


def home(request):
    return render(request, 'home.html')

def custom_logout(request):
    logout(request)
    # Выводим страницу logout с вашим кастомным шаблоном
    return render(request, 'news/logout.html')

def news_list(request):
    news = Post.objects.all().order_by('-created_at')
    paginator = Paginator(news, 5)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        messages.error(request, "Страница не найдена.")
        page_obj = paginator.get_page(1)

    return render(request, 'news_list.html', {'page_obj': page_obj})

def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news_detail.html', {'post': post})

def news_search(request):
    query = request.GET.get('q', '')
    author_name = request.GET.get('author', '')
    date_after = request.GET.get('date_after', '')
    post_type = request.GET.get('type', '')  # Фильтрация по типу

    filters = Q()
    if query:
        filters &= Q(title__icontains=query)
    if author_name:
        filters &= Q(author__user__username__icontains=author_name)
    if date_after:
        filters &= Q(created_at__gte=date_after)
    if post_type:
        filters &= Q(type=post_type)  # Фильтрация по типу поста (AR или NW)

    news = Post.objects.filter(filters).order_by('-created_at')
    paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_search.html', {'page_obj': page_obj})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('news.add_post', raise_exception=True),
                  name='dispatch')  # Проверка прав на создание
class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'text', 'author']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    permission_required = 'news.add_post'  # Разрешение на создание поста

    def form_valid(self, form):
        # Если нужно, можно оставить проверку принадлежности к группе authors
        if not self.request.user.groups.filter(name='authors').exists():
            messages.error(self.request, "У вас нет прав на создание поста.")
            return redirect('home')  # Перенаправление на домашнюю страницу

        form.instance.type = self.get_post_type_from_url()  # Устанавливаем тип поста из URL
        return super().form_valid(form)

    def get_post_type_from_url(self):
        if 'articles' in self.request.path:
            return Post.ARTICLE
        elif 'news' in self.request.path:
            return Post.NEWS
        else:
            messages.error(self.request, "Тип поста не указан. Пожалуйста, выберите правильный тип!")
            raise Http404("Тип поста не указан")


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('news.change_post', raise_exception=True), name='dispatch')  # Проверка прав на редактирование
class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'author', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'

    def form_valid(self, form):

        if not self.request.user.groups.filter(name='authors').exists():
            messages.error(self.request, "У вас нет прав на редактирование поста.")
            return redirect('home')  # Перенаправление на домашнюю страницу
        form.instance.type = self.get_post_type_from_url()  # Используем метод для получения типа поста
        return super().form_valid(form)

    def get_post_type_from_url(self):
        if 'articles' in self.request.path:
            return Post.ARTICLE
        elif 'news' in self.request.path:
            return Post.NEWS
        else:
            raise Http404("Тип поста не указан")


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('news.delete_post', raise_exception=True), name='dispatch')  # Проверка прав на удаление
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'
