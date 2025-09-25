from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from news.api_urls import router as news_router
from news.views import ArticleViewSet, NewsViewSet

router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news")
router.register(r"articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("news/", include("news.urls")),
    path("api/", include(news_router.urls)),
]
