'''Запустите Django shell:'''

python manage.py shell

'''1. Создание пользователей'''
from django.contrib.auth.models import User
from news.models import Author, Category, Post, Comment

user1 = User.objects.create_user('user1', password='password1')
user2 = User.objects.create_user('user2', password='password2')

author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

'''2. Добавление категорий'''
cat1 = Category.objects.create(name='Sports')
cat2 = Category.objects.create(name='Politics')
cat3 = Category.objects.create(name='Education')
cat4 = Category.objects.create(name='Technology')


'''3. Создание статей и новостей'''
post1 = Post.objects.create(author=author1, type=Post.ARTICLE, title='First Article', text='Content of the first article.')
post2 = Post.objects.create(author=author1, type=Post.ARTICLE, title='Second Article', text='Content of the second article.')
post3 = Post.objects.create(author=author2, type=Post.NEWS, title='Breaking News', text='Content of the news.')

post1.categories.add(cat1, cat2)
post2.categories.add(cat3)
post3.categories.add(cat4)


'''4. Создание комментариев'''
comment1 = Comment.objects.create(post=post1, user=user2, text='Great article!')
comment2 = Comment.objects.create(post=post1, user=user1, text='Thank you!')
comment3 = Comment.objects.create(post=post2, user=user2, text='Interesting perspective.')
comment4 = Comment.objects.create(post=post3, user=user1, text='Breaking news indeed!')


'''5. Корректировка рейтингов'''
post1.like()
post1.like()
post2.dislike()
comment1.like()
comment3.like()
comment4.dislike()


'''6. Обновление рейтингов пользователей'''
author1.update_rating()
author2.update_rating()


'''7. Лучший пользователь'''
best_author = Author.objects.order_by('-rating').first()
print(f'Best author: {best_author.user.username}, Rating: {best_author.rating}')


'''8. Лучшая статья'''
best_post = Post.objects.order_by('-rating').first()
print(f'Date: {best_post.created_at}, Author: {best_post.author.user.username}, '
      f'Rating: {best_post.rating}, Title: {best_post.title}, Preview: {best_post.preview()}')

'''9. Комментарии к лучшей статье'''
for comment in best_post.comment_set.all():
    print(f'Date: {comment.created_at}, User: {comment.user.username}, '
          f'Rating: {comment.rating}, Text: {comment.text}')

'''Если ты хочешь посмотреть все комментарии и ты прекращал сессию'''

'''НЕ ЗАБУДЬ!!! Импортируй модель Comment'''
from your_app_name.models import Comment

if Comment.objects.exists():
    for comment in Comment.objects.all():
        print(f"Date: {comment.created_at}, User: {comment.user.username}, "
              f"Rating: {comment.rating}, Text: {comment.text}")
else:
    print("No comments found.")
