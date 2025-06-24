from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet
)

router = DefaultRouter()

router.register('users', CustomUserViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
