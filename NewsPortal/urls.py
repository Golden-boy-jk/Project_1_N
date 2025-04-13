from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.i18n import set_language
from django.conf.urls.i18n import i18n_patterns

from rest_framework.routers import DefaultRouter
from news.views import NewsViewSet, ArticleViewSet

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'articles', ArticleViewSet, basename='articles')


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("news/", include("news.urls")),
    path("accounts/", include("allauth.urls")),  # Подключаем allauth
    path(
        "accounts/", include("accounts.urls")
    ),  # Подключаем кастомные маршруты accounts после allauth
    path("", lambda request: redirect("/home/")),
    path("api/", include("news.urls")),
    path("api/", include(router.urls)),
]
urlpatterns += i18n_patterns(
    path("set_language/", set_language, name="set_language"),
    # сюда можно добавить другие маршруты, которые зависят от языка
)
