import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Post
from .tasks import send_new_post_notifications

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance: Post, created, **kwargs):
    # инвалидируем кеш карточки
    cache_key = f"article_{instance.pk}"
    from django.core.cache import cache

    cache.delete(cache_key)

    if created:
        logger.debug("Планируем рассылку уведомлений для post_id=%s", instance.pk)
        # асинхронно рассылаем (Celery)
        send_new_post_notifications.delay(instance.pk)


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance: Post, **kwargs):
    cache_key = f"article_{instance.pk}"
    from django.core.cache import cache

    cache.delete(cache_key)
