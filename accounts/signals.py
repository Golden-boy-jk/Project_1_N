from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Post, Author  # Убедитесь, что Author импортирован
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .utils import generate_activation_link
from django.urls import reverse


@receiver(post_save, sender=User)
def user_signals(sender, instance, created, **kwargs):
    """Обрабатывает создание нового пользователя: добавление в группу, создание профиля и отправка письма"""
    if created:
        # Добавляем в группу 'common'
        common_group, _ = Group.objects.get_or_create(name="common")
        instance.groups.add(common_group)

        # Создаём профиль автора, если его нет
        if not hasattr(instance, "author"):
            Author.objects.create(user=instance)

        # Отправляем приветственное письмо, если указан email
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
def add_permissions_to_authors_group(sender, **kwargs):
    """Добавляет права группе 'authors' после миграции"""
    authors_group, _ = Group.objects.get_or_create(name="authors")
    post_content_type = ContentType.objects.get_for_model(Post)

    permissions = [
        ("can_create_post", "Can create post"),
        ("can_edit_post", "Can edit post"),
    ]

    for codename, name in permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename, name=name, content_type=post_content_type
        )
        authors_group.permissions.add(permission)


def send_new_post_notification(post, recipient):
    """Отправляет email-уведомление подписчикам о новой статье"""
    post_url = settings.SITE_URL + reverse("news_detail", args=[post.pk])

    subject = f"Новая статья в категории {post.categories.first().name}"
    context = {
        "user": recipient,
        "post": post,
        "post_url": post_url,
    }

    html_message = render_to_string("email/new_post_email.html", context)
    plain_message = (
        f"Здравствуйте, {recipient.username}!\n\n"
        f'В категории "{post.categories.first().name}" появилась новая статья: "{post.title}".\n'
        f"Читать статью: {post_url}\n\n"
        f"С уважением, команда NewsPortal"
    )

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient.email],
        fail_silently=False,
        html_message=html_message,
    )
