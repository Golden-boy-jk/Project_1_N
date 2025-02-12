from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Post  # Убедитесь, что правильно импортировали модель Post


@receiver(post_save, sender=User)
def add_to_common_group(sender, instance, created, **kwargs):
    if created:  # Проверяем, что пользователь только что был создан
        common_group, _ = Group.objects.get_or_create(name="common")  # Создаем или находим группу
        instance.groups.add(common_group)  # Добавляем пользователя в группу


@receiver(post_migrate)
def add_permissions_to_authors_group(sender, **kwargs):
    # Находим или создаём группу authors
    authors_group, _ = Group.objects.get_or_create(name="authors")

    # Получаем разрешения для модели Post
    post_content_type = ContentType.objects.get_for_model(Post)

    # Получаем или создаём разрешения
    create_permission, _ = Permission.objects.get_or_create(
        codename="can_create_post",
        name="Can create post",
        content_type=post_content_type
    )
    edit_permission, _ = Permission.objects.get_or_create(
        codename="can_edit_post",
        name="Can edit post",
        content_type=post_content_type
    )

    # Добавляем разрешения в группу authors
    authors_group.permissions.add(create_permission, edit_permission)
