from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    UserViewSet
)


router = DefaultRouter()

router.register('users', UserViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
