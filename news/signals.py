from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from news.tasks import send_new_post_notifications  # Убедись, что импорт правильный!

@receiver(post_save, sender=Post)
def notify_subscribers_on_new_post(sender, instance, created, **kwargs):
    if created:
        print(f"DEBUG: Отправка задачи с post_id={instance.id}")  # Проверка ID
        send_new_post_notifications.delay(instance.id)

