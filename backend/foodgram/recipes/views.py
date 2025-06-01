from rest_framework import viewsets

from .models import Ingredients
from .serializers import IngredientsSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения списка ингредиентов.

    Предоставляет доступ только для чтения всех объектов модели Ingredients.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
