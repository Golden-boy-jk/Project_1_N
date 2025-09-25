from django.urls import path

from . import views
from .views import (
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    category_detail,
    home,
    news_detail,
    news_list,
    news_search,
)

urlpatterns = [
    # Языки
    path("set_language/", views.set_language, name="set_language"),
    # Основные страницы
    path("", news_list, name="news_list"),
    path("home/", home, name="home"),
    path("search/", news_search, name="news_search"),
    # Посты
    path("post/<int:pk>/", news_detail, name="news_detail"),
    path("post/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    # Создание постов
    path(
        "create/", PostCreateView.as_view(), name="post_create"
    ),  # общий (можно убрать)
    path(
        "news/create/",
        PostCreateView.as_view(extra_context={"type": "NW"}),
        name="news_create",
    ),
    path(
        "articles/create/",
        PostCreateView.as_view(extra_context={"type": "AR"}),
        name="article_create",
    ),
    # Категории
    path("categories/", views.category_list, name="category_list"),
    path("category/<int:pk>/", category_detail, name="category_detail"),
    path(
        "category/<int:pk>/subscribe/",
        views.subscribe_category,
        name="subscribe_category",
    ),
    path(
        "category/<int:pk>/unsubscribe/",
        views.unsubscribe_category,
        name="unsubscribe_category",
    ),
]
