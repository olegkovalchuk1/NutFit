from django.urls import path

from recipes.views import list_recipes, recipe_detail, sync_recipes

urlpatterns = [
    path("sync-recipes/", sync_recipes, name="sync_recipes"),
    path("recipes/", list_recipes, name="list_recipes"),
    path("recipes/<int:recipe_id>/", recipe_detail, name="recipe_detail"),
]
