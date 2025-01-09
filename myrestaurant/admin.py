from django.contrib import admin

# Register your models here.
from .models import MenuItem, Ingredient, RecipeRequirement, Purchase

[admin.site.register(model) for model in [MenuItem, Ingredient, RecipeRequirement, Purchase]]