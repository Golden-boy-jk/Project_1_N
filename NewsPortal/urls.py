# NewsPortal/urls.py
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from news.views import NewsViewSet, ArticleViewSet, PostViewSet

router = DefaultRouter()
router.register(r"api/news", NewsViewSet, basename="api-news")
router.register(r"api/articles", ArticleViewSet, basename="api-articles")
router.register(r"api/posts", PostViewSet, basename="api-posts")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("news.urls", namespace="news")),  # <--- ВАЖНО
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("", include(router.urls)),
]
