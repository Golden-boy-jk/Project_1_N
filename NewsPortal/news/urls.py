from django.urls import path
from .views import (news_list, news_detail, news_search, home,
                    NewsCreateView, NewsUpdateView, NewsDeleteView,
                    ArticleCreateView, ArticleUpdateView, ArticleDeleteView)

urlpatterns = [
    path('', news_list, name='news_list'),
    path('<int:pk>/', news_detail, name='news_detail'),
    path('search/', news_search, name='news_search'),  # Убедись, что этот путь есть
    path('home/', home, name='home'),

    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
]
