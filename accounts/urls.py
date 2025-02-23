from django.urls import path
from .views import become_author, profile, activate_account


urlpatterns = [
    path('become_author/', become_author, name='become_author'),
    path('profile/', profile, name='profile'),
    path("activate/<str:signed_value>/", activate_account, name="activate_account"),
]
