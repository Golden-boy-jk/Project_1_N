from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from news.tasks import send_new_post_notification_email

from news.models import Author, Post  # noqa: F401
from .utils import generate_activation_link

User = get_user_model()


@receiver(post_save, sender=User)
def user_signals(sender: type[User], instance: User, created: bool, **kwargs: Any) -> None:
    """Обрабатывает создание нового пользователя.

    - добавляем в группу `common`;
    - создаём профиль автора, если его ещё нет;
    - отправляем письмо с активацией (если указан email).
    """
    if not created:
        return

    common_group, _ = Group.objects.get_or_create(name="common")
    instance.groups.add(common_group)

    if not hasattr(instance, "author"):
        Author.objects.create(user=instance)

    if instance.email:
        subject = "Добро пожаловать в NewsPortal!"
        activation_link = generate_activation_link(instance)

        html_message = render_to_string(
            "email/welcome_email.html",
            {"user": instance, "activation_link": activation_link},
        )
        plain_message = (
            f"Перейдите по ссылке для активации аккаунта: {activation_link}"
        )

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            html_message=html_message,
        )


@receiver(post_migrate)
def add_permissions_to_authors_group(sender: Any, **kwargs: Any) -> None:
    """Добавляет права группе `authors` после применения миграций `news`.

    Чтобы не дёргать ContentType на каждое приложение, проверяем app_label.
    """
    app_config = kwargs.get("app_config")
    if not app_config or app_config.label != "news":
        return

    authors_group, _ = Group.objects.get_or_create(name="authors")
    post_content_type = ContentType.objects.get_for_model(Post)

    permissions = [
        ("can_create_post", "Can create post"),
        ("can_edit_post", "Can edit post"),
    ]

    for codename, name in permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=post_content_type,
        )
        authors_group.permissions.add(permission)


def send_new_post_notification(post, recipient):
    """
    Отправляет email-уведомление подписчику о новой статье (асинхронно через Celery).
    """
    if not recipient.email:
        return
    send_new_post_notification_email.delay(post.id, recipient.id)

    html_message = render_to_string("email/new_post_email.html", context)
    plain_message = (
        f"Здравствуйте, {recipient.username}!\n\n"
        f'В категории "{post.categories.first().name}" появилась новая статья: '
        f'"{post.title}".\n'
        f"Читать статью: {post_url}\n\n"
        "С уважением, команда NewsPortal"
    )

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient.email],
        fail_silently=False,
        html_message=html_message,
    )
