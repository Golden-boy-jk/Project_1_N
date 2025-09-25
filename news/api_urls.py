# news/api_urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, NewsViewSet

app_name = "news_api"

router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news")
router.register(r"articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("", include(router.urls)),
]
