from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    UserAccauntViewSet
)

router = DefaultRouter()

router.register('users', UserAccauntViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
