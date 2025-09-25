from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Sum
from django.urls import reverse

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """Быстрая агрегация рейтинга (без N+1 и без странных обходов)."""
        # Сумма рейтингов постов автора x3
        posts_aggr = (self.posts.aggregate(total=Sum("rating"))["total"] or 0) * 3

        # Сумма рейтингов его собственных комментариев
        my_comments_aggr = (
            self.user.comments.aggregate(total=Sum("rating"))["total"] or 0
        )

        # Сумма рейтингов всех комментариев под его постами (любыми пользователями)
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


class Category(models.Model):
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
        "Category", through="PostCategory", related_name="posts"
    )
    title = models.CharField(max_length=255, db_index=True)
    text = models.TextField()
    rating = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        permissions = [
            ("can_edit_post", "Can edit post"),
            ("can_create_post", "Can create post"),
        ]
        indexes = [
            models.Index(fields=["type", "created_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail", args=[str(self.pk)])

    # Без гонок: F-выражения вместо чтения/записи
    def like(self):
        Post.objects.filter(pk=self.pk).update(rating=F("rating") + 1)
        self.refresh_from_db(fields=["rating"])

    def dislike(self):
        Post.objects.filter(pk=self.pk).update(rating=F("rating") - 1)
        self.refresh_from_db(fields=["rating"])

    def preview(self, length: int = 124):
        return (self.text[:length] + "...") if len(self.text) > length else self.text


class PostCategory(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_posts"
    )

    class Meta:
        unique_together = (("post", "category"),)  # не даём задвоить связь
        verbose_name = "Связь пост–категория"
        verbose_name_plural = "Связи пост–категория"

    def __str__(self):
        return f"{self.post.title} — {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    timezone = models.CharField(max_length=64, default="Europe/Moscow")

    def __str__(self):
        return f"Профиль пользователя {self.user}"
