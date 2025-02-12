from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author")
    rating = models.IntegerField(default=0)


    def update_rating(self):
        post_ratings = sum(post.rating * 3 for post in self.post_set.all())
        comment_ratings = sum(comment.rating for comment in self.user.comment_set.all())
        post_comment_ratings = sum(comment.rating for post in self.post_set.all() for comment in post.comment_set.all())
        self.rating = post_ratings + comment_ratings + post_comment_ratings
        self.save()

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

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

    class Meta:
        permissions = [
            ("can_edit_post", "Can edit post"),
            ("can_create_post", "Can create post"),
        ]

    def __str__(self):
        return self.title

    def is_article(self):
        return self.type == self.ARTICLE

    def is_news(self):
        return self.type == self.NEWS

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

