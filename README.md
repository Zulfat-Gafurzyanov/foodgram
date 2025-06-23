# Foodgram
- продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.
Технологии:
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud, Continuous Integration, Continuous Deployment

## Основные доступные endpoints:
GET /api/recipes/ - список рецептов
GET /api/recipes/{id}/ - детали рецепта
POST /api/recipes/ - создание рецепта
GET /api/tags/ - список тегов
GET /api/ingredients/ - список ингредиентов
POST /api/auth/token/login/ - получение токена
GET /api/users/me/ - профиль текущего пользователя


## Запуск проекта:

### Клонируйте проект:
git clone https://github.com/ruzhova/foodgram-project-react.git

### Подготовьте сервер:
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/

### Установите docker и docker-compose:
sudo apt install docker.io 
sudo apt install docker-compose

### Соберите контейнер и выполните миграции:
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate

### Создайте суперюзера и соберите статику:
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input