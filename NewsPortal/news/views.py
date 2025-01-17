from django.shortcuts import render, get_object_or_404
from .models import Post



def home(request):
    return render(request, 'home.html')

def news_list(request):
    news = Post.objects.all().order_by('-created_at')  # Убираем фильтр по type
    return render(request, 'news_list.html', {'news': news})

def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news_detail.html', {'post': post})







