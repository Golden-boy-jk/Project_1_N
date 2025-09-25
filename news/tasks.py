# news/tasks.py
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Category, Post


@shared_task
def send_weekly_newsletter() -> str:
    """Еженедельная рассылка: для каждого подписчика — только его категории."""
    today = timezone.now()
    last_week = today - timedelta(weeks=1)

    # Посты за неделю + категории одним махом
    latest_posts = (
        Post.objects.filter(created_at__gte=last_week)
        .select_related("author__user")
        .prefetch_related("categories")
        .order_by("-created_at")
    )

    if not latest_posts.exists():
        print("Нет новостей для рассылки.")
        return "No posts"

    # Уникальные e-mail подписчиков всех задействованных категорий
    categories = Category.objects.filter(posts__in=latest_posts).distinct()
    subscribers = categories.values_list("subscribers__email", flat=True).distinct()
    recipient_emails: list[str] = [email for email in subscribers if email]

    if not recipient_emails:
        print("Нет подписчиков для рассылки.")
        return "No subscribers"

    site_url = getattr(settings, "SITE_URL", "https://example.com").rstrip("/")

    # Чтобы не дергать БД в цикле по пользователям, построим индекс:
    # категория -> [posts]
    posts_by_category = {}
    for post in latest_posts:
        for cat in post.categories.all():
            posts_by_category.setdefault(cat.id, []).append(post)

    # И получим мапу email->набор id категорий, на которые подписан этот email
    # (делаем один запрос по промежуточной таблице M2M)
    # Считываем подписки для только тех e-mail, что у нас есть.
    subs_qs = categories.values_list("id", "subscribers__email").exclude(
        subscribers__email__isnull=True
    )
    email_to_cat_ids = {}
    for cat_id, email in subs_qs:
        email_to_cat_ids.setdefault(email, set()).add(cat_id)

    sent = 0
    subject = "Последние новости недели"

    for email in recipient_emails:
        cat_ids = email_to_cat_ids.get(email, set())
        # Соберем посты, которые относятся к категориям этого email
        user_posts = []
        for cid in cat_ids:
            user_posts.extend(posts_by_category.get(cid, []))

        if not user_posts:
            continue

        # Уникализируем и отсортируем по дате (на всякий случай)
        user_posts = sorted(
            {p.id: p for p in user_posts}.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )

        context = {
            "site_url": site_url,
            "posts": user_posts,
        }

        # Используем шаблоны, если они есть; иначе — fallback на простую сборку
        try:
            plain_message = render_to_string("email/weekly_newsletter.txt", context)
            html_message = render_to_string("email/weekly_newsletter.html", context)
        except Exception:
            # Fallback: простой текст/HTML
            plain_lines = [
                "Здравствуйте!",
                "Вот последние новости за прошедшую неделю:",
                "",
            ]
            html_lines = [
                "<h2>Здравствуйте!</h2>",
                "<p>Вот последние новости за прошедшую неделю:</p>",
                "<ul>",
            ]
            for post in user_posts:
                url = f"{site_url}{post.get_absolute_url()}"
                plain_lines.append(f"{post.title}: {url}")
                html_lines.append(f"<li><a href='{url}'>{post.title}</a></li>")
            html_lines.append("</ul><p>С уважением,<br>Команда NewsPortal</p>")
            plain_message = "\n".join(plain_lines)
            html_message = "\n".join(html_lines)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message,
            )
            sent += 1
        except Exception as e:
            print(f"Ошибка при отправке письма {email}: {e}")

    print(f"Weekly newsletter sent! Recipients: {sent}")
    return "Success" if sent else "No recipients"


@shared_task
def send_new_post_notifications(post_id: int) -> str:
    """Уведомления по одному новому посту: рассылаем всем подписчикам его категорий (уникально)."""
    try:
        post = (
            Post.objects.select_related("author__user")
            .prefetch_related("categories")
            .get(pk=post_id)
        )
    except Post.DoesNotExist:
        print(f"Ошибка: Пост с ID {post_id} не найден.")
        return "Post not found"

    site_url = getattr(settings, "SITE_URL", "https://example.com").rstrip("/")

    # Уникальные email подписчиков всех категорий поста
    subscribers = post.categories.values_list(
        "subscribers__email", flat=True
    ).distinct()
    recipient_emails: list[str] = [email for email in subscribers if email]

    if not recipient_emails:
        return "No subscribers"

    context = {
        "post": post,
        "site_url": site_url,
    }

    subject = f"Новая публикация: {post.title}"

    try:
        plain_message = render_to_string("email/new_post_email.txt", context)
        html_message = render_to_string("email/new_post_email.html", context)
    except Exception:
        url = f"{site_url}{post.get_absolute_url()}"
        plain_message = f"Новая публикация: {post.title}\n{url}\n"
        html_message = f"<h3>Новая публикация: {post.title}</h3><p><a href='{url}'>Открыть новость</a></p>"

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=recipient_emails,
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as e:
        print(f"Ошибка при массовой отправке писем: {e}")
        # На учебном проекте можно не делить на батчи; если нужно — легко добавить.

    print(
        f"New post notifications sent! post_id={post_id}, recipients={len(recipient_emails)}"
    )
    return "Success"
