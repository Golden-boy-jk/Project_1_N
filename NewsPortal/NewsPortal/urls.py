from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('home/', include('django.contrib.flatpages.urls')),
    path('accounts/', include('allauth.urls')),  # Подключаем allauth
    path('accounts/', include('accounts.urls')),  # Подключаем кастомные маршруты accounts после allauth
    path('', lambda request: redirect('/home/')),
]


