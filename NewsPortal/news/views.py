from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from datetime import datetime

from .models import Post

def home(request):
    return render(request, 'home.html')

def news_list(request):
    news = Post.objects.all().order_by('-created_at')
    paginator = Paginator(news, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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

class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'text', 'author']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.type = self.get_post_type_from_url()
        return super().form_valid(form)

    def get_post_type_from_url(self):
        if 'articles' in self.request.path:
            return Post.ARTICLE
        elif 'news' in self.request.path:
            return Post.NEWS
        else:
            raise Http404("Тип поста не указан")

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj

class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'text', 'author', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.type = self.get_post_type_from_url()  # Используем метод для получения типа поста
        return super().form_valid(form)

    def get_post_type_from_url(self):
        if 'articles' in self.request.path:
            return Post.ARTICLE
        elif 'news' in self.request.path:
            return Post.NEWS
        else:
            raise Http404("Тип поста не указан")
