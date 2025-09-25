import logging
from datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Category, Post

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """Отправка еженедельной рассылки пользователям, подписанным на категории"""
    today = timezone.now()
    one_week_ago = today - timedelta(days=7)

    # Получаем все категории с подписчиками
    categories = Category.objects.all()

    for category in categories:
        # Получаем статьи за последнюю неделю
        recent_posts = Post.objects.filter(
            categories=category, created_at__gte=one_week_ago
        )

        if recent_posts.exists():
            # Получаем список подписчиков этой категории
            subscribers = category.subscribers.all()

            # Составляем письмо для каждого подписчика
            for subscriber in subscribers:
                send_email_to_subscriber(subscriber, category, recent_posts)


def send_email_to_subscriber(subscriber, category, recent_posts):
    """Функция для отправки письма подписчику"""
    # Создаем URL для каждой статьи
    current_site = Site.objects.get_current()
    post_urls = [
        f"http://{current_site.domain}/news/{post.id}/" for post in recent_posts
    ]

    subject = f"Новые статьи в категории {category.name} за последнюю неделю"
    html_content = render_to_string(
        "emails/weekly_newsletter.html",
        {
            "category": category,
            "posts": recent_posts,
            "post_urls": post_urls,
        },
    )

    send_mail(
        subject,
        "",
        "from@example.com",  # Укажите ваш email отправителя
        [subscriber.email],
        html_message=html_content,
    )


def delete_old_job_executions(max_age=604_800):
    """Удаление старых задач, которые уже не актуальны"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Запускает apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Добавляем задачу для рассылки новостей
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждое воскресенье в полночь
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача: 'send_weekly_newsletter'.")

        # Добавляем задачу для удаления старых задач
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждый понедельник в полночь
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Добавлена задача для удаления старых задач: 'delete_old_job_executions'."
        )

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик остановлен успешно!")
