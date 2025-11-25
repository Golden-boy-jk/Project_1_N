from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class ProfileViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass12345",
        )

    def test_profile_requires_login(self) -> None:
        """Неавторизованного пользователя редиректит на страницу логина."""
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_profile_authorized_user_ok(self) -> None:
        """Авторизованный пользователь успешно открывает профиль."""
        self.client.login(username="testuser", password="pass12345")
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Привет, testuser")
