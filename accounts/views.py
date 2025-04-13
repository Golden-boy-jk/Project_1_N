from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


def become_author(request):
    """Добавляет пользователя в группу 'authors'"""
    authors_group, _ = Group.objects.get_or_create(name="authors")
    if not request.user.groups.filter(name="authors").exists():
        request.user.groups.add(authors_group)
    return redirect("profile")  # Перенаправление на профиль


signer = TimestampSigner()


def activate_account(request, signed_value):
    """Активация аккаунта по временной ссылке"""
    try:
        # Расшифровка с проверкой на максимальный срок действия (например, 1 час)
        user_id = signer.unsign(
            signed_value, max_age=3600
        )  # max_age в секундах (1 час)
        user = User.objects.get(id=user_id)

        # Проверка, активирован ли уже аккаунт
        if user.is_active:
            messages.warning(request, "Ваш аккаунт уже активирован!")
            return redirect("account_login")

        # Активация аккаунта
        user.is_active = True
        user.save()
        messages.success(request, "Ваш аккаунт успешно активирован!")
        return redirect("account_login")  # Перенаправляем на страницу входа

    except SignatureExpired:
        messages.error(request, "Срок действия ссылки истёк!")
    except (BadSignature, User.DoesNotExist):
        messages.error(request, "Неверная ссылка!")

    return redirect("account_login")
