from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    1. Если метод  безопасный, то доступ разрешен сразу.
    2. Если метод небезопасный, то доступ предоставляется, если объект
    был создан самим пользователем, выполнившим запрос.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
