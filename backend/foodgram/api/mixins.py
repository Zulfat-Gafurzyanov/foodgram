from rest_framework import status
from rest_framework.response import Response


class RecipeCreateDeleteMixin:
    """Миксин реализует логику для добавления и удаления рецептов."""
    def perform_action(
        self, request, pk, model, serializer_class, error_message
    ):
        recipe = self.get_object()
        user = request.user
        queryset = model.objects.filter(user=user, recipe=recipe)
        exists = queryset.exists()

        if request.method == "POST":
            if exists:
                return Response(
                    {"errors": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = serializer_class(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            if not exists:
                return Response(
                    {"errors": 'Рецепт не найден.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)