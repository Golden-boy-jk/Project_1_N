from django.urls import path

from .views import activate_account, become_author, profile

urlpatterns = [
    path("become_author/", become_author, name="become_author"),
    path("profile/", profile, name="profile"),
    path("activate/<str:signed_value>/", activate_account, name="activate_account"),
]
