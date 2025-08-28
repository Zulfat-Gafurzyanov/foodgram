# 🍽️ Foodgram - Продуктовый Помощник

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.1-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-blue.svg)
![Docker](https://img.shields.io/badge/docker-blue.svg)

Foodgram — это онлайн-сервис и API для управления рецептами. Пользователи могут публиковать рецепты, добавлять их в избранное, подписываться на авторов и формировать список покупок для выбранных блюд.

## ✨ Основные возможности

- 👤 **Управление пользователями**: регистрация, авторизация, профили с аватарами
- 📝 **Рецепты**: создание, редактирование, поиск по тегам и ингредиентам
- ⭐ **Избранное**: сохранение понравившихся рецептов
- 👥 **Подписки**: отслеживание активности любимых авторов
- 🛒 **Список покупок**: автоматическое формирование списка ингредиентов
- 🏷️ **Теги**: категоризация рецептов (завтрак, обед, ужин и др.)
- 📱 **API**: полнофункциональный REST API с документацией

## 🛠️ Технологический стек

### Backend
- **Python 3.12** - основной язык программирования
- **Django 5.2.1** - веб-фреймворк
- **Django REST Framework 3.16.0** - для создания API
- **PostgreSQL** - основная база данных
- **Djoser** - аутентификация и управление пользователями
- **Pillow** - обработка изображений

### DevOps
- **Docker** & **Docker Compose** - контейнеризация
- **Gunicorn** - WSGI-сервер
- **Nginx** - веб-сервер и reverse proxy

### Библиотеки
- **django-filter** - фильтрация данных
- **drf-extra-fields** - дополнительные поля для DRF
- **python-dotenv** - управление переменными окружения

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd foodgram
   ```

2. **Создайте файл окружения:**
   ```bash
   cp .env.example .env
   ```
   
   Отредактируйте `.env` файл:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=your-password
   DB_HOST=db
   DB_PORT=5432
   DOMAIN=your-domain.com
   HOST_IP=your-server-ip
   ```

3. **Запустите проект:**
   ```bash
   docker compose up --build
   ```

4. **Выполните миграции и загрузите начальные данные:**
   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --noinput
   docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
   docker compose exec backend python manage.py load_csv
   ```

5. **Создайте суперпользователя (опционально):**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

Сервис будет доступен по адресу: `http://localhost` или вашему домену.

## 📚 API Документация

### Основные эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/api/recipes/` | Список рецептов |
| `POST` | `/api/recipes/` | Создание рецепта |
| `GET` | `/api/recipes/{id}/` | Детали рецепта |
| `PUT/PATCH` | `/api/recipes/{id}/` | Обновление рецепта |
| `DELETE` | `/api/recipes/{id}/` | Удаление рецепта |
| `GET` | `/api/recipes/{id}/get-link/` | Короткая ссылка на рецепт |
| `POST/DELETE` | `/api/recipes/{id}/favorite/` | Добавить/убрать из избранного |
| `POST/DELETE` | `/api/recipes/{id}/shopping_cart/` | Добавить/убрать из списка покупок |
| `GET` | `/api/recipes/download_shopping_cart/` | Скачать список покупок |

### Пользователи и подписки

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/api/users/` | Список пользователей |
| `POST` | `/api/users/` | Регистрация |
| `GET` | `/api/users/{id}/` | Профиль пользователя |
| `GET` | `/api/users/me/` | Текущий пользователь |
| `PUT/DELETE` | `/api/users/me/avatar/` | Управление аватаром |
| `POST/DELETE` | `/api/users/{id}/subscribe/` | Подписка/отписка |
| `GET` | `/api/users/subscriptions/` | Мои подписки |

### Справочники

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/api/ingredients/` | Список ингредиентов |
| `GET` | `/api/ingredients/{id}/` | Детали ингредиента |
| `GET` | `/api/tags/` | Список тегов |
| `GET` | `/api/tags/{id}/` | Детали тега |

### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/auth/token/login/` | Получение токена |
| `POST` | `/api/auth/token/logout/` | Удаление токена |

## 🔧 Разработка

### Локальная разработка

1. **Создайте виртуальное окружение:**
   ```bash
   cd backend/foodgram
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте базу данных:**
   ```bash
   python manage.py migrate
   python manage.py load_csv
   ```

4. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
   ```

### Полезные команды

```bash
# Загрузка ингредиентов из CSV
docker compose exec backend python manage.py load_csv

# Создание суперпользователя
docker compose exec backend python manage.py createsuperuser

# Сбор статических файлов
docker compose exec backend python manage.py collectstatic

# Просмотр логов
docker compose logs backend

# Остановка контейнеров
docker compose down

# Перестроение контейнеров
docker compose up --build
```

## 📋 Фильтрация и поиск

### Рецепты
- **По тегам**: `?tags=breakfast,lunch`
- **По автору**: `?author=1`
- **Избранные**: `?is_favorited=1`
- **В списке покупок**: `?is_in_shopping_cart=1`

### Ингредиенты
- **По названию**: `?name=помидор`

## 🔐 Безопасность

- Аутентификация через токены
- Валидация всех входных данных
- Защита от CSRF атак
- Ограничения на размер загружаемых файлов

*Сделано с ❤️ для любителей готовить*
