from django.urls import path

from . import views

# from django.conf.urls.i18n import i18n_patterns
from .views import (
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    category_detail,
    home,
    news_detail,
    news_list,
    news_search,
)

urlpatterns = [
    path("set_language/", views.set_language, name="set_language"),
    path("", news_list, name="news_list"),
    path("<int:pk>/", news_detail, name="news_detail"),
    path("search/", news_search, name="news_search"),
    path("home/", home, name="home"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("news/create/", PostCreateView.as_view(), name="news_create"),
    path("articles/create/", PostCreateView.as_view(), name="article_create"),
    path("<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    # Страница категории и подписка
    path(
        "categories/", views.category_list, name="category_list"
    ),  # Страница со всеми категориями
    path(
        "category/<int:category_id>/", category_detail, name="category_detail"
    ),  # Страница категории
    path(
        "subscribe/<int:category_id>/",
        views.subscribe_category,
        name="subscribe_category",
    ),  # Подписка
    path(
        "unsubscribe/<int:category_id>/",
        views.unsubscribe_category,
        name="unsubscribe_category",
    ),  # Отписка
]

# urlpatterns += i18n_patterns(
#     path('set_language/', views.set_language, name='set_language'),
# )
