from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ArticleViewSet,
    NewsViewSet,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostUpdateView,
    PostViewSet,
    category_detail,
    category_list,
    custom_logout,
    home,
    news_detail,
    news_list,
    news_search,
    post_list,
    set_language,
    set_timezone,
    subscribe_category,
    unsubscribe_category,
)

app_name = "news"

# --- DRF router --------------------------------------------------------------

router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news-api")
router.register(r"articles", ArticleViewSet, basename="articles-api")
router.register(r"posts", PostViewSet, basename="posts-api")

# --- HTML-urls ---------------------------------------------------------------

urlpatterns = [
    # Домашняя
    path("", home, name="home"),

    # Лента и детали
    path("news/", news_list, name="news_list"),
    path("news/<int:pk>/", news_detail, name="news_detail"),
    path("news/search/", news_search, name="news_search"),
    path("posts/", post_list, name="post_list"),

    # CRUD постов (через CBV)
    path("posts/create/", PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),

    # Категории
    path("categories/", category_list, name="category_list"),
    path("categories/<int:pk>/", category_detail, name="category_detail"),
    path("categories/<int:pk>/subscribe/", subscribe_category, name="subscribe_category"),
    path(
        "categories/<int:pk>/unsubscribe/",
        unsubscribe_category,
        name="unsubscribe_category",
    ),

    # Настройки
    path("set-language/", set_language, name="set_language"),
    path("set-timezone/", set_timezone, name="set_timezone"),

    # Выход
    path("logout/", custom_logout, name="logout"),

    # DRF API
    path("api/v1/", include(router.urls)),
]
