from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post, UserProfile
from .tasks import send_new_post_notifications  # Убедись, что импорт правильный!


@receiver(post_save, sender=Post)
def notify_subscribers_on_new_post(sender, instance, created, **kwargs):
    if created:
        print(f"DEBUG: Отправка задачи с post_id={instance.id}")  # Проверка ID
        send_new_post_notifications.delay(instance.id)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
