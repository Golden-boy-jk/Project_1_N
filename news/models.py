from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Sum
from django.urls import reverse
from django.utils.text import Truncator

User = get_user_model()


# --- Базовая абстрактная модель ---------------------------------------------


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# --- Author ------------------------------------------------------------------


class Author(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """Оптимизированная агрегация рейтинга автора."""

        posts_aggr = (self.posts.aggregate(total=Sum("rating"))["total"] or 0) * 3
        my_comments_aggr = (
            self.user.comments.aggregate(total=Sum("rating"))["total"] or 0
        )
        under_my_posts_aggr = (
            Comment.objects.filter(post__author=self).aggregate(total=Sum("rating"))[
                "total"
            ]
            or 0
        )

        self.rating = posts_aggr + my_comments_aggr + under_my_posts_aggr
        self.save(update_fields=["rating"])

    def __str__(self):
        return f"Автор {self.user}"


# --- Category ----------------------------------------------------------------


class Category(TimeStampedModel):
    name = models.CharField(max_length=128, unique=True)
    subscribers = models.ManyToManyField(
        User, related_name="subscribed_categories", blank=True
    )

    def subscribe(self, user: User):
        self.subscribers.add(user)

    def unsubscribe(self, user: User):
        self.subscribers.remove(user)

    def __str__(self):
        return self.name


# --- Post --------------------------------------------------------------------


class PostType(models.TextChoices):
    ARTICLE = "AR", "Статья"
    NEWS = "NW", "Новость"


class Post(TimeStampedModel):
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    type = models.CharField(
        max_length=2, choices=PostType.choices, default=PostType.ARTICLE, db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    text = models.TextField()
    rating = models.IntegerField(default=0, db_index=True)

    categories = models.ManyToManyField(
        "Category", through="PostCategory", related_name="posts"
    )

    class Meta:
        ordering = ("-created_at",)
        permissions = [
            ("can_edit_post", "Can edit post"),
            ("can_create_post", "Can create post"),
        ]
        indexes = [
            models.Index(fields=["type", "created_at"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail", args=[str(self.pk)])

    # Без гонок — F-выражения
    def like(self):
        Post.objects.filter(pk=self.pk).update(rating=F("rating") + 1)
        self.refresh_from_db(fields=["rating"])

    def dislike(self):
        Post.objects.filter(pk=self.pk).update(rating=F("rating") - 1)
        self.refresh_from_db(fields=["rating"])

    @property
    def preview(self):
        return Truncator(self.text).chars(150)


# --- PostCategory ------------------------------------------------------------


class PostCategory(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_posts"
    )

    class Meta:
        unique_together = (("post", "category"),)
        verbose_name = "Связь пост–категория"
        verbose_name_plural = "Связи пост–категория"

    def __str__(self):
        return f"{self.post.title} — {self.category.name}"


# --- Comment -----------------------------------------------------------------


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    rating = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Комментарий от {self.user} к «{self.post}»"

    def like(self):
        Comment.objects.filter(pk=self.pk).update(rating=F("rating") + 1)
        self.refresh_from_db(fields=["rating"])

    def dislike(self):
        Comment.objects.filter(pk=self.pk).update(rating=F("rating") - 1)
        self.refresh_from_db(fields=["rating"])


# --- UserProfile -------------------------------------------------------------


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    timezone = models.CharField(max_length=64, default="Europe/Moscow")

    def __str__(self):
        return f"Профиль пользователя {self.user}"
