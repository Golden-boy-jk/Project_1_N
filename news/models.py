from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_ratings = sum(post.rating * 3 for post in self.post_set.all())
        comment_ratings = sum(comment.rating for comment in self.user.comment_set.all())
        post_comment_ratings = sum(comment.rating for post in self.post_set.all() for comment in post.comments.all())
        self.rating = post_ratings + comment_ratings + post_comment_ratings
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    subscribers = models.ManyToManyField(User, related_name="subscribed_categories", blank=True)

    def subscribe(self, user):
        """Подписывает пользователя на категорию."""
        self.subscribers.add(user)

    def unsubscribe(self, user):
        """Отписывает пользователя от категории."""
        self.subscribers.remove(user)

    def notify_subscribers(self, post):
        """Уведомляет подписчиков о новой статье."""
        for subscriber in self.subscribers.all():
            subject = f"Новая статья в категории {self.name}"
            message = render_to_string('email/new_post_email.html', {'user': subscriber, 'post': post, 'category': self})
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=False,
            )

    def __str__(self):
        return self.name

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name="posts")
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.pk)])

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
        return f'{self.text[:124]}...' if len(self.text) > 124 else self.text


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_categories")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_posts")

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
def notify_subscribers_on_new_post(sender, instance, created, **kwargs):
    """Отправляет уведомления подписчикам при публикации новой статьи"""
    if created:
        for category in instance.categories.all():
            category.notify_subscribers(instance)
