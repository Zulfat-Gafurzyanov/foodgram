from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import include, path

from recipes.views import IngredientsViewSet


router = DefaultRouter()
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
