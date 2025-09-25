from django.contrib import admin
from django.db.models import Prefetch

from .models import Category, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "type",
        "created_at",
        "rating",
        "get_categories",
    )
    list_filter = ("type", "created_at", "categories")
    search_fields = ("title", "text")
    ordering = ("-created_at",)
    list_per_page = 25  # пагинация в админке

    def get_queryset(self, request):
        """Оптимизируем запросы для категорий (убираем N+1)"""
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch("categories", queryset=Category.objects.only("id", "name"))
        )

    def get_categories(self, obj):
        """Выводит список категорий в админке"""
        return ", ".join(obj.categories.values_list("name", flat=True))

    get_categories.short_description = "Категории"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
