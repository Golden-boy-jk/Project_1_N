from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class ProfileViewTests(TestCase):
    def test_profile_requires_login(self):
        client = Client()
        response = client.get(reverse("accounts:profile"))
        # Ожидаем редирект на логин
        self.assertEqual(response.status_code, 302)
