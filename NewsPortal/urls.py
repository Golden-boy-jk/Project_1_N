from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from news.views import ArticleViewSet, NewsViewSet, home

# DRF API router
router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news")
router.register(r"articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("admin/", admin.site.urls),
    # news-приложение (HTML + API)
    path("", include("news.urls", namespace="news")),

    # аккаунты (allauth + наше accounts)
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("accounts/", include("allauth.urls")),

    path("news/", include("news.urls")),  # обычные Django-шаблоны
    path("api/", include(router.urls)),  # DRF API эндпоинты
    path("home/", home, name="home"),  # теперь импорт корректный
]
