from django.contrib import admin

from .models import Category, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "type",
        "created_at",
        "rating",
        "get_categories",
    )  # Добавляем категории
    list_filter = ("type", "created_at", "categories")  # Добавляем фильтр по категориям
    search_fields = ("title", "text")
    ordering = ("-created_at",)

    def get_categories(self, obj):
        """Выводит список категорий в админке"""
        return ", ".join([cat.name for cat in obj.categories.all()])

    get_categories.short_description = "Категории"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
