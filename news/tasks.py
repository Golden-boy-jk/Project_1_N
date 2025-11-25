from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import Category, Post


@shared_task
def send_new_post_notification_email(post_id: int, user_id: int) -> None:
    """
    Отправить письмо подписчику о новой статье (одному пользователю).
    Запускается пачкой для всех подписчиков.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        post = Post.objects.get(pk=post_id)
        user = User.objects.get(pk=user_id)
    except (Post.DoesNotExist, User.DoesNotExist):
        return

    post_url = settings.SITE_URL + reverse("news:news_detail", args=[post.pk])
    category = post.categories.first()

    subject = f"Новая публикация в категории {category.name if category else 'Новости'}"

    context = {
        "user": user,
        "post": post,
        "post_url": post_url,
        "category": category,
    }

    html_message = render_to_string("email/new_post_email.html", context)
    plain_message = (
        f"Здравствуйте, {user.username}!\n\n"
        f'Новая публикация: "{post.title}".\n'
        f"Читать: {post_url}\n\n"
        "С уважением, команда NewsPortal"
    )

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )


@shared_task
def send_weekly_digest() -> None:
    """
    Еженедельный дайджест по всем категориям.
    Выбирает посты за последние 7 дней и шлёт подписчикам.
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    recent_posts = (
        Post.objects.filter(created_at__gte=week_ago)
        .select_related("author__user")
        .prefetch_related("categories")
    )

    if not recent_posts.exists():
        return

    # Для простоты: идём по категориям, шлём подписчикам
    for category in Category.objects.prefetch_related("subscribers").all():
        posts_in_cat = recent_posts.filter(categories=category)
        if not posts_in_cat.exists():
            continue

        subscribers = category.subscribers.all()
        if not subscribers:
            continue

        for user in subscribers:
            if not user.email:
                continue

            post_lines = []
            for post in posts_in_cat:
                url = settings.SITE_URL + reverse("news:news_detail", args=[post.pk])
                post_lines.append(f"- {post.title} — {url}")

            subject = f"Дайджест недели по категории {category.name}"
            body = (
                f"Здравствуйте, {user.username}!\n\n"
                f"Новые публикации в категории «{category.name}» за неделю:\n\n"
                + "\n".join(post_lines)
                + "\n\nС уважением, NewsPortal"
            )

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
