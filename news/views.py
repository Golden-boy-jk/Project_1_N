from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from .models import Post, Category
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

def send_new_post_email(post):
    """Отправка письма всем подписчикам категории"""
    category = post.categories.first()  # Получаем первую категорию поста
    subscribers = category.subscribers.values_list('email', flat=True)  # Получаем email подписчиков

    if not subscribers:
        return

    post_url = f"http://127.0.0.1:8000{reverse('news_detail', args=[post.id])}"
    subject = f"Новая статья в категории {category.name}: {post.title}"
    text_content = f"Прочитайте новый пост: {post.title}\n{post_url}"
    html_content = render_to_string('email/new_post_email.html', {'post': post, 'post_url': post_url})

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, subscribers)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 2. Функция для главной страницы
def home(request):
    return render(request, 'home.html')


# 3. Функция для отображения страницы категории
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)  # Находим категорию по ID
    return render(request, 'category_detail.html', {'category': category})  # Рендерим шаблон категории


# 4. Функция для отображения списка всех категорий
def category_list(request):
    categories = Category.objects.all()  # Получаем все категории
    return render(request, 'categories/category_list.html', {'categories': categories})  # Рендерим шаблон


# 5. Функция для выхода пользователя
def custom_logout(request):
    logout(request)  # Выход пользователя
    return render(request, 'news/logout.html')


# 6. Функция для отображения списка новостей с пагинацией
def news_list(request):
    news = Post.objects.all().order_by('-created_at')  # Получаем все новости
    paginator = Paginator(news, 5)  # Создаем пагинатор
    page_number = request.GET.get('page')  # Получаем текущую страницу

    try:
        page_obj = paginator.get_page(page_number)  # Получаем страницы
    except EmptyPage:
        messages.error(request, "Страница не найдена.")  # Если страница не найдена
        page_obj = paginator.get_page(1)  # Показываем первую страницу

    return render(request, 'news_list.html', {'page_obj': page_obj})  # Рендерим список новостей


# 7. Функция для отображения подробностей статьи
def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)  # Находим пост по ID
    return render(request, 'news_detail.html', {'post': post})  # Рендерим шаблон с подробностями


# 8. Функция для поиска новостей
def news_search(request):
    query = request.GET.get('q', '')  # Получаем поисковый запрос
    author_name = request.GET.get('author', '')  # Получаем имя автора
    date_after = request.GET.get('date_after', '')  # Получаем дату после которой искать
    post_type = request.GET.get('type', '')  # Получаем тип поста

    filters = Q()  # Инициализируем фильтры
    if query:
        filters &= Q(title__icontains=query)  # Фильтруем по заголовку
    if author_name:
        filters &= Q(author__user__username__icontains=author_name)  # Фильтруем по автору
    if date_after:
        filters &= Q(created_at__gte=date_after)  # Фильтруем по дате
    if post_type:
        filters &= Q(type=post_type)  # Фильтруем по типу

    news = Post.objects.filter(filters).order_by('-created_at')  # Получаем новости по фильтрам
    paginator = Paginator(news, 5)  # Пагинация
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_search.html', {'page_obj': page_obj})  # Рендерим результаты поиска


# 9. Классы для создания, редактирования и удаления постов
class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    permission_required = 'news.can_create_post'

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='authors').exists():
            messages.error(self.request, "У вас нет прав на создание поста.")
            post_url = self.request.build_absolute_uri(reverse('news_detail', args=[self.object.pk]))
            context = self.get_context_data()
            context['post_url'] = post_url
            return redirect('home')

        form.instance.author = self.request.user.author
        post = form.save()
        send_new_post_email(post)  # Отправляем email после создания поста
        return super().form_valid(form)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='authors').exists():
            messages.error(self.request, "У вас нет прав на редактирование поста.")
            return redirect('home')
        return super().form_valid(form)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')


# 10. Функции для подписки и отписки от категории
@login_required
def subscribe_category(request, category_id):
    """Подписываем пользователя на рассылку новостей категории"""
    category = get_object_or_404(Category, id=category_id)  # Находим категорию
    category.subscribe(request.user)  # Добавляем пользователя в подписчики категории
    return redirect('category_detail', category_id=category.id)  # Перенаправляем на страницу категории

@login_required
def unsubscribe_category(request, category_id):
    """Отписываем пользователя от рассылки новостей категории"""
    category = get_object_or_404(Category, id=category_id)  # Находим категорию
    category.unsubscribe(request.user)  # Убираем пользователя из подписчиков категории
    return redirect('category_detail', category_id=category.id)  # Перенаправляем на страницу категории


# 11. Сигналы для уведомлений
@receiver(post_save, sender=Post)
def notify_subscribers_on_new_post(sender, instance, created, **kwargs):
    """Отправляет уведомления подписчикам при публикации новой статьи"""
    if created:
        for category in instance.categories.all():
            category.notify_subscribers(instance)  # Уведомление для каждого подписчика категории


# 12. Функция для того, чтобы стать автором
@login_required
def become_author(request):
    """Функция для того, чтобы стать автором"""
    if not request.user.groups.filter(name='authors').exists():
        group = Group.objects.get(name='authors')  # Получаем группу 'authors'
        request.user.groups.add(group)  # Добавляем пользователя в группу 'authors'
        messages.success(request, "Теперь вы автор!")
    else:
        messages.info(request, "Вы уже стали автором!")

    return redirect('profile')  # Перенаправляем на профиль пользователя


# 13. Подробности поста
class PostDetailView(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'
