from django.contrib import admin

from .models import Ingredients, Tags, ShoppingCart

admin.site.register(Ingredients)
admin.site.register(Tags)
admin.site.register(ShoppingCart)
