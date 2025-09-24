from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django import forms
import pytz
from django.db.models import Sum, F


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """Быстрая агрегация рейтинга без N+1."""
        posts_aggr = self.posts.aggregate(total=Sum(F("rating") * 3))["total"] or 0
        my_comments_aggr = (
            self.user.comments.aggregate(total=Sum("rating"))["total"] or 0
        )
        under_my_posts_aggr = (
            self.user.comment_set.model.objects.filter(post__author=self).aggregate(
                total=Sum("rating")
            )["total"]
            or 0
        )
        self.rating = posts_aggr + my_comments_aggr + under_my_posts_aggr
        self.save(update_fields=["rating"])


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    subscribers = models.ManyToManyField(
        User, related_name="subscribed_categories", blank=True
    )

    def subscribe(self, user):
        """Подписывает пользователя на категорию."""
        self.subscribers.add(user)

    def unsubscribe(self, user):
        """Отписывает пользователя от категории."""
        self.subscribers.remove(user)

    def notify_subscribers(self, post):
        """Отправка уведомления подписчикам категории о новом посте."""
        subject = f"Новая публикация в категории {self.name}: {post.title}"
        context = {
            "post": post,
            "category": self,
            "site_url": getattr(settings, "SITE_URL", ""),
        }

        # plain-тело (нужен файл news/templates/email/new_post_email.txt)
        message = render_to_string("email/new_post_email.txt", context)
        html_message = render_to_string("email/new_post_email.html", context)

        for subscriber in self.subscribers.all():
            if not subscriber.email:
                continue
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[subscriber.email],
                fail_silently=False,
                html_message=html_message,
            )

    def __str__(self):
        return self.name


class Post(models.Model):
    ARTICLE = "AR"
    NEWS = "NW"
    POST_TYPES = [
        (ARTICLE, "Статья"),
        (NEWS, "Новость"),
    ]

    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(
        Category, through="PostCategory", related_name="posts"
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("news_detail", args=[str(self.pk)])

    class Meta:
        permissions = [
            ("can_edit_post", "Can edit post"),
            ("can_create_post", "Can create post"),
        ]

    def __str__(self):
        return self.title

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.text[:124]}..." if len(self.text) > 124 else self.text


class PostCategory(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_posts"
    )

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"


@receiver(post_save, sender=Post)
def send_new_post_notifications(sender, instance, created, **kwargs):
    """Отправка уведомлений при создании + инвалидация кеша на любое сохранение."""
    cache.delete(f"article_{instance.pk}")
    if created:
        for category in instance.categories.all():
            category.notify_subscribers(instance)


@receiver(post_delete, sender=Post)
def clear_article_cache(sender, instance, **kwargs):
    cache.delete(f"article_{instance.pk}")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    timezone = models.CharField(max_length=32, default="Europe/Moscow")

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


class TimezoneForm(forms.Form):
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones])
