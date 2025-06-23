import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredients


# Запуск команды: python manage.py load_csv
class Command(BaseCommand):
    help = 'Импортирует данные из CSV-файла для модели Ingredients'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'Файл {file_path} не найден.'))
            return

        count = 0
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)
                obj, created = Ingredients.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                count += 1
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создан объект: {obj}'))
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Обновлен объект: {obj}'))
        self.stdout.write(
            self.style.SUCCESS(f'Импортировано {count} записей.'))
