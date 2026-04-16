from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from recipes.models import Recipe
from recipes.services.recipe_service import fetch_and_save_recipes


def _serialize_recipe(recipe):
    return {
        "id": recipe.id,
        "api_id": recipe.api_id,
        "name": recipe.name,
        "category": recipe.category,
        "instructions": recipe.instructions,
        "image_url": recipe.image_url,
        "calories": recipe.calories,
        "ingredients": [
            {
                "name": ri.ingredient.name,
                "grams": ri.grams,
                "calories_per_100g": ri.ingredient.calories_per_100g,
            }
            for ri in recipe.recipe_ingredients.all()
        ],
    }


@require_GET
def sync_recipes(request):
    query = request.GET.get("q", "chicken")
    saved = fetch_and_save_recipes(query=query)
    return JsonResponse({"status": "ok", "saved": saved, "query": query})


@require_GET
def list_recipes(request):
    query = (request.GET.get("q") or "").strip()

    try:
        limit = int(request.GET.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50

    limit = max(1, min(limit, 200))

    queryset = Recipe.objects.order_by("name").prefetch_related(
        "recipe_ingredients__ingredient"
    )
    if query:
        queryset = queryset.filter(name__icontains=query)

    total = queryset.count()
    recipes = [_serialize_recipe(recipe) for recipe in queryset[:limit]]
    return JsonResponse({"count": total, "limit": limit, "results": recipes})


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related("recipe_ingredients__ingredient"),
        pk=recipe_id,
    )
    return JsonResponse(_serialize_recipe(recipe))
