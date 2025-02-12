from django.urls import path
from .views import become_author, profile

urlpatterns = [
    path('become_author/', become_author, name='become_author'),
    path('profile/', profile, name='profile'),
]
