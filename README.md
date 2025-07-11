# Foodgram
- продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

## Основные функции:

- Регистрация и аутентификация пользователей
- Публикация рецептов с возможностью добавления изображений
- Добавление рецептов в избранное
- Подписка на других пользователей
- Формирование списка покупок
- Поиск рецептов по тегам и ингредиентам

## Структура проекта:

- backend/ — содержит исходный код серверной части приложения.
- foodgram/ — основное приложение Django.
- recipes/ — приложение для работы с рецептами.
- users/ — приложение для управления пользователями.
- api/ — реализация API на основе Django REST Framework.
- frontend/ — исходный код клиентской части (если есть).
- api/docs/ — документация по проекту.

## Основные доступные endpoints:
- GET /api/recipes/ - список рецептов
- GET /api/recipes/{id}/ - детали рецепта
- POST /api/recipes/ - создание рецепта
- GET /api/tags/ - список тегов
- GET /api/ingredients/ - список ингредиентов
- POST /api/auth/token/login/ - получение токена
- GET /api/users/me/ - профиль текущего пользователя

## Развёртывание:

Для развертывания проекта используйте Docker. Убедитесь, что у вас установлены Docker и Docker Compose. Выполните следующие команды:
- docker compose up --build
- docker compose exec backend python manage.py migrate
- docker compose exec backend python manage.py collectstatic
- docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
- docker compose exec backend python manage.py csv_upload

Стек: Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL
