# news/urls.py
from django.urls import path

from .views import (
    home,
    news_list,
    news_detail,
    news_search,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    category_list,
    category_detail,
    subscribe_category,
    unsubscribe_category,
    custom_logout,
    post_list,
    set_language,
    set_timezone,
)

app_name = "news"

urlpatterns = [
    path("", home, name="home"),
    path("posts/", news_list, name="news_list"),
    path("posts/search/", news_search, name="news_search"),
    path("posts/<int:pk>/", news_detail, name="news_detail"),

    path("posts/create/news/", PostCreateView.as_view(extra_context={"type": "NW"}), name="post_create_news"),
    path("posts/create/article/", PostCreateView.as_view(extra_context={"type": "AR"}), name="post_create_article"),
    path("posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),

    path("categories/", category_list, name="category_list"),
    path("categories/<int:pk>/", category_detail, name="category_detail"),
    path("categories/<int:pk>/subscribe/", subscribe_category, name="category_subscribe"),
    path("categories/<int:pk>/unsubscribe/", unsubscribe_category, name="category_unsubscribe"),

    path("logout/", custom_logout, name="logout"),
    path("posts/by-category/", post_list, name="post_list"),
    path("set-language/", set_language, name="set_language"),
    path("set-timezone/", set_timezone, name="set_timezone"),
]
