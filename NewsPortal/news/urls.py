from django.urls import path
from .views import news_list, news_detail
from . import views

urlpatterns = [
    path('', news_list, name='news_list'),
    path('news/', views.news_list, name='news'),
    path('home/', views.home, name='home'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),  # Страница полной информации
]


