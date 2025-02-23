from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_at', 'rating')  # Корректно отображаем поля в списке
    list_filter = ('type', 'created_at')  # Добавьте фильтры, если нужно
    search_fields = ('title', 'text')  # Определите поля для поиска в админке
    ordering = ('-created_at',)  # Порядок сортировки
