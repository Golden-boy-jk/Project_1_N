from django.conf import settings
from django.core.signing import TimestampSigner

signer = TimestampSigner()


def generate_activation_link(user):
    """Генерирует временную ссылку для активации аккаунта"""
    signed_value = signer.sign(user.id)
    return f"{settings.SITE_URL}/accounts/activate/{signed_value}/"
