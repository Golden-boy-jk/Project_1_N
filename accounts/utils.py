from django.conf import settings
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.contrib.auth import get_user_model

signer = TimestampSigner()
User = get_user_model()


def generate_activation_link(user: User) -> str:
    """Сформировать временную ссылку для активации аккаунта пользователя.

    Ссылка строится на основе SITE_URL и именованного урла
    `activate_account`, чтобы не держать путь в строке.
    """
    signed_value = signer.sign(user.id)
    path = reverse("activate_account", args=[signed_value])
    return f"{settings.SITE_URL}{path}"
