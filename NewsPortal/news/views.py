from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Post


def home(request):
    return render(request, 'home.html')

def news_list(request):
    news = Post.objects.all().order_by('-created_at')  # Убираем фильтр по type
    paginator = Paginator(news, 10)  # Показывать по 5 записей на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news_list.html', {'page_obj': page_obj})

def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news_detail.html', {'post': post})

def news_search(request):
    query = request.GET.get('q', '')
    author = request.GET.get('author', '')
    date_after = request.GET.get('date_after', '')

    print(f"query: {query}, author: {author}, date_after: {date_after}")

    filters = Q()
    if query:
        filters &= Q(title__icontains=query)
    if author:
        filters &= Q(author__id=author)
    if date_after:
        filters &= Q(created_at__gte=date_after)

    news = Post.objects.filter(filters).order_by('-created_at')
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_search.html', {'page_obj': page_obj})

class NewsCreateView(CreateView):
    model = Post
    fields = ['title', 'text', 'author']  # поля
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.type = 'news'  # Указываем, что это новость
        return super().form_valid(form)


class NewsUpdateView(UpdateView):
    model = Post
    fields = ['title', 'text', 'author']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')


class ArticleCreateView(CreateView):
    model = Post
    fields = ['title', 'text', 'author']
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        form.instance.type = 'article'  # Указываем, что это статья
        return super().form_valid(form)


class ArticleUpdateView(UpdateView):
    model = Post
    fields = ['title', 'text', 'author']
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('news_list')


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('news_list')






