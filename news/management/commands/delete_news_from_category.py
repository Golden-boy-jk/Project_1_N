from django.core.management.base import BaseCommand

from news.models import Category, Post


class Command(BaseCommand):
    help = "Удаляет все новости из указанной категории с подтверждением"

    def add_arguments(self, parser):
        # Добавляем аргумент для указания категории
        parser.add_argument(
            "category_name", type=str, help="Название категории для удаления новостей"
        )

    def handle(self, *args, **options):
        category_name = options["category_name"]

        # Проверяем, существует ли категория с таким названием
        try:
            category = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Категория "{category_name}" не найдена')
            )
            return

        # Выводим все новости в этой категории
        posts = Post.objects.filter(categories__in=[category])
        if not posts.exists():
            self.stdout.write(
                self.style.SUCCESS(f'Нет новостей в категории "{category_name}"')
            )
            return

        # Подтверждаем удаление
        self.stdout.write(
            self.style.WARNING(
                f'Вы уверены, что хотите удалить все новости из категории "{category_name}"?'
            )
        )
        confirm = input('Введите "yes" для подтверждения: ')

        if confirm.lower() == "yes":
            # Удаляем новости
            posts.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Все новости из категории "{category_name}" были удалены'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Удаление отменено"))
