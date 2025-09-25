from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from news.views import ArticleViewSet, NewsViewSet

router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news")
router.register(r"articles", ArticleViewSet, basename="articles")

urlpatterns = [
    # системные
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    # allauth (ВОТ ЭТО НУЖНО!)
    path("accounts/", include("allauth.urls")),
    # веб-страницы приложения news
    path("news/", include("news.urls")),
    path("articles/", include("news.urls_articles")),
    path("profiles/", include("news.urls_profiles")),
    path("subscriptions/", include("news.urls_subscriptions")),
    path("search/", include("news.urls_search")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/news/", include("news.api_urls_news")),
    path("api/articles/", include("news.api_urls_articles")),
    # главная — на список новостей
    path("", RedirectView.as_view(url="/news/", permanent=False), name="home"),
]
