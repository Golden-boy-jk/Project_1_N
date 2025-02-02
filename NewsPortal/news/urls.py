from django.urls import path
from .views import (news_list, news_detail, news_search, home,
                    PostCreateView, PostDeleteView, PostUpdateView)  # Используем одно представление для создания постов

urlpatterns = [
    path('', news_list, name='news_list'),
    path('<int:pk>/', news_detail, name='news_detail'),
    path('search/', news_search, name='news_search'),  # Убедись, что этот путь есть
    path('home/', home, name='home'),

    path('create/', PostCreateView.as_view(), name='post_create'),  # Для создания новостей и статей
    path('news/create/', PostCreateView.as_view(), name='news_create'),
    path('articles/create/', PostCreateView.as_view(), name='article_create'),

    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]
