from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import redirect, render

signer = TimestampSigner()


@login_required
def profile(request):
    """Профиль пользователя с признаком 'является ли автором'."""
    is_author = request.user.groups.filter(name="authors").exists()
    return render(request, "accounts/profile.html", {"is_author": is_author})


@login_required
def become_author(request):
    """Добавляет текущего пользователя в группу 'authors'.

    Выполняется только по POST, чтобы случайный переход по ссылке
    не менял права.
    """
    if request.method != "POST":
        return redirect("profile")

    authors_group, _ = Group.objects.get_or_create(name="authors")
    if not request.user.groups.filter(name="authors").exists():
        request.user.groups.add(authors_group)
        messages.success(request, "Вы стали автором!")
    else:
        messages.info(request, "Вы уже являетесь автором.")

    return redirect("profile")


def activate_account(request, signed_value: str):
    """Активация аккаунта по временной ссылке.

    Ссылка действительна ограниченное время (по умолчанию 1 час).
    """
    try:
        user_id = signer.unsign(signed_value, max_age=3600)
        user = User.objects.get(id=user_id)

        if user.is_active:
            messages.warning(request, "Ваш аккаунт уже активирован!")
            return redirect("account_login")

        user.is_active = True
        user.save()
        messages.success(request, "Ваш аккаунт успешно активирован!")
        return redirect("account_login")

    except SignatureExpired:
        messages.error(request, "Срок действия ссылки истёк!")
    except (BadSignature, User.DoesNotExist):
        messages.error(request, "Неверная ссылка!")

    return redirect("account_login")
