from celery import shared_task
from news.models import Post
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_weekly_newsletter():
    """Отправляет еженедельную рассылку с последними новостями."""
    today = timezone.now()
    last_week = today - timedelta(weeks=1)

    # Получаем посты за последнюю неделю
    latest_posts = Post.objects.filter(pub_date__gte=last_week).order_by('-pub_date')

    if not latest_posts:
        print("Нет новостей для рассылки.")
        return "No posts"

    # Получаем всех подписчиков категорий
    subscribers = set()
    for post in latest_posts:
        for category in post.categories.all():
            subscribers.update(category.subscribers.all())

    if not subscribers:
        print("Нет подписчиков для рассылки.")
        return "No subscribers"

    # Формируем заголовок письма
    subject = "Последние новости недели"

    # Отправляем письма подписчикам
    for subscriber in subscribers:
        user_news = [post for post in latest_posts if any(cat in post.categories.all() for cat in subscriber.subscriptions.all())]

        if not user_news:
            continue  # Если нет новых постов в категориях пользователя, пропускаем

        html_message = f"""
            <h2>Здравствуйте, {subscriber.username}!</h2>
            <p>Вот последние новости за прошедшую неделю:</p>
            <ul>
        """
        plain_message = f"Здравствуйте, {subscriber.username}!\n\nВот последние новости за прошедшую неделю:\n\n"

        for post in user_news:
            post_url = f"{settings.SITE_URL}{post.get_absolute_url()}"
            html_message += f"<li><a href='{post_url}'>{post.title}</a></li>"
            plain_message += f"{post.title}: {post_url}\n"

        html_message += "</ul><p>С уважением,<br>Команда NewsPortal</p>"

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
            html_message=html_message
        )

    print("Weekly newsletter sent!")
    return "Success"

@shared_task
def send_new_post_notifications(post_id):
    print(f"DEBUG: Получен post_id={post_id}")  # Проверка
    try:
        post = Post.objects.get(id=post_id)
    except ObjectDoesNotExist:
        print(f"Ошибка: Пост с ID {post_id} не найден.")
        return "Post not found"

    for category in post.categories.all():
        category.notify_subscribers(post)
    print(f"Уведомления о новом посте {post_id} отправлены!")
    return "Success"
