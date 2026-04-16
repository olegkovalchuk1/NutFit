import json
import logging
import re
from fractions import Fraction
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.db import transaction

from recipes.models import Ingredient, Recipe, RecipeIngredient

logger = logging.getLogger(__name__)


CALORIES_DICT = {
    "anchovy": 210,
    "apple": 52,
    "asparagus": 20,
    "avocado": 160,
    "bacon": 541,
    "banana": 89,
    "barley": 123,
    "basil": 23,
    "bay leaf": 313,
    "beans": 127,
    "beef": 250,
    "beet": 43,
    "bell pepper": 31,
    "black beans": 132,
    "blueberry": 57,
    "bread": 265,
    "broccoli": 34,
    "brown rice": 111,
    "brussels sprouts": 43,
    "bulgur": 83,
    "butter": 717,
    "cabbage": 25,
    "capers": 23,
    "carrot": 41,
    "cashew": 553,
    "cauliflower": 25,
    "celery": 16,
    "cheese": 402,
    "chia seed": 486,
    "chickpea": 164,
    "chicken": 165,
    "chicken stock": 15,
    "chili": 40,
    "chili powder": 282,
    "cinnamon": 247,
    "coconut milk": 230,
    "corn": 96,
    "couscous": 112,
    "cream": 340,
    "cream cheese": 342,
    "cucumber": 15,
    "cumin": 375,
    "curry powder": 325,
    "dates": 282,
    "dill": 43,
    "duck": 337,
    "egg": 155,
    "eggplant": 25,
    "feta": 264,
    "fish": 206,
    "flax seed": 534,
    "flour": 364,
    "garlic": 149,
    "ginger": 80,
    "goat cheese": 364,
    "grape": 69,
    "green beans": 31,
    "ham": 145,
    "honey": 304,
    "kale": 49,
    "kiwi": 61,
    "lamb": 294,
    "leek": 61,
    "lentils": 116,
    "lemon": 29,
    "lettuce": 15,
    "lime": 30,
    "mayonnaise": 680,
    "milk": 60,
    "millet": 119,
    "mint": 44,
    "mushroom": 22,
    "mustard": 66,
    "noodles": 138,
    "nutmeg": 525,
    "oats": 389,
    "oil": 884,
    "olive": 115,
    "olive oil": 884,
    "onion": 40,
    "orange": 47,
    "oregano": 265,
    "parmesan": 431,
    "parsley": 36,
    "pasta": 131,
    "peanut": 567,
    "peanut butter": 588,
    "pear": 57,
    "peas": 81,
    "pepper": 31,
    "pineapple": 50,
    "pistachio": 562,
    "pork": 242,
    "potato": 77,
    "pumpkin": 26,
    "quinoa": 120,
    "radish": 16,
    "raisins": 299,
    "rice": 130,
    "rosemary": 131,
    "salmon": 208,
    "salt": 0,
    "sausage": 301,
    "sesame seed": 573,
    "shrimp": 99,
    "sour cream": 193,
    "soy sauce": 53,
    "spinach": 23,
    "sugar": 387,
    "sunflower seed": 584,
    "sweet potato": 86,
    "thyme": 101,
    "tofu": 76,
    "tomato": 18,
    "tuna": 132,
    "turkey": 189,
    "vanilla": 288,
    "walnut": 654,
    "watermelon": 30,
    "white rice": 130,
    "wine": 85,
    "yogurt": 59,
    "zucchini": 17,
}

MEASURE_TO_GRAMS = {
    "cup": 240,
    "cups": 240,
    "tbsp": 15,
    "tablespoon": 15,
    "tablespoons": 15,
    "tsp": 5,
    "teaspoon": 5,
    "teaspoons": 5,
    "pinch": 1,
    "pinches": 1,
    "dash": 1,
    "slice": 25,
    "slices": 25,
    "clove": 5,
    "cloves": 5,
    "piece": 100,
    "pieces": 100,
    "fillet": 170,
    "fillets": 170,
    "can": 400,
    "cans": 400,
    "oz": 28,
    "ounce": 28,
    "ounces": 28,
    "lb": 454,
    "pound": 454,
    "pounds": 454,
    "g": 1,
    "gram": 1,
    "grams": 1,
    "kg": 1000,
    "ml": 1,
    "l": 1000,
    "liter": 1000,
    "liters": 1000,
}

_FRACTION_REPLACEMENTS = {
    "\u00bd": "1/2",
    "\u2153": "1/3",
    "\u2154": "2/3",
    "\u00bc": "1/4",
    "\u00be": "3/4",
}

_ALIASES = {
    "all purpose flour": "flour",
    "all-purpose flour": "flour",
    "baby spinach": "spinach",
    "beef mince": "beef",
    "beef stock": "beef",
    "bell pepper": "pepper",
    "black pepper": "pepper",
    "brown rice": "rice",
    "brown sugar": "sugar",
    "caster sugar": "sugar",
    "chicken breast": "chicken",
    "chicken breasts": "chicken",
    "chicken thigh": "chicken",
    "chicken thighs": "chicken",
    "chicken stock": "chicken stock",
    "chilli powder": "chili powder",
    "cilantro": "parsley",
    "coriander leaves": "parsley",
    "double cream": "cream",
    "egg yolk": "egg",
    "egg yolks": "egg",
    "eggs": "egg",
    "extra virgin olive oil": "olive oil",
    "garlic clove": "garlic",
    "garlic cloves": "garlic",
    "green pepper": "pepper",
    "ground beef": "beef",
    "heavy cream": "cream",
    "icing sugar": "sugar",
    "kidney beans": "beans",
    "lemon juice": "lemon",
    "lime juice": "lime",
    "minced beef": "beef",
    "olive oil": "oil",
    "onions": "onion",
    "plain flour": "flour",
    "potatoes": "potato",
    "red onion": "onion",
    "red pepper": "pepper",
    "sea salt": "salt",
    "self raising flour": "flour",
    "self-raising flour": "flour",
    "spring onion": "onion",
    "spring onions": "onion",
    "tomatoes": "tomato",
    "vegetable oil": "oil",
    "white sugar": "sugar",
    "whole milk": "milk",
}


def _to_float(value):
    token = value.strip()
    if not token:
        return None
    if re.fullmatch(r"\d+(\.\d+)?", token):
        return float(token)
    if re.fullmatch(r"\d+-\d+", token):
        return float(token.split("-")[0])
    if re.fullmatch(r"\d+/\d+", token):
        return float(Fraction(token))
    return None


def _normalize_text(value):
    normalized = value.lower().strip()
    for unicode_frac, plain in _FRACTION_REPLACEMENTS.items():
        normalized = normalized.replace(unicode_frac, plain)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _normalize_ingredient(ingredient):
    if not ingredient:
        return ""

    ingredient = re.sub(r"[^a-zA-Z\s]", " ", ingredient.lower())
    ingredient = re.sub(r"\s+", " ", ingredient).strip()

    if ingredient in _ALIASES:
        return _ALIASES[ingredient]

    for alias, base_name in _ALIASES.items():
        if alias in ingredient:
            return base_name

    if ingredient.endswith("es") and ingredient[:-2] in CALORIES_DICT:
        return ingredient[:-2]
    if ingredient.endswith("s") and ingredient[:-1] in CALORIES_DICT:
        return ingredient[:-1]
    return ingredient


def _merge_ingredients(ingredients_list):
    merged = {}
    for item in ingredients_list:
        ingredient = _normalize_ingredient((item.get("ingredient") or "").strip())
        grams = float(item.get("grams") or 0)
        if not ingredient or grams <= 0:
            continue
        merged[ingredient] = merged.get(ingredient, 0.0) + grams
    return [{"ingredient": key, "grams": round(value, 2)} for key, value in merged.items()]


def parse_ingredient(text):
    normalized = _normalize_text(text)
    if not normalized:
        return {"ingredient": "", "grams": 0}

    tokens = normalized.split()
    idx = 0
    quantity = None

    first = _to_float(tokens[0])
    if first is not None:
        quantity = first
        idx = 1
        if idx < len(tokens):
            second = _to_float(tokens[idx])
            if second is not None and "/" in tokens[idx]:
                quantity += second
                idx += 1
    elif tokens[0] in ("a", "an"):
        quantity = 1.0
        idx = 1

    measure = None
    if idx < len(tokens):
        candidate = tokens[idx].rstrip(".")
        if candidate in MEASURE_TO_GRAMS:
            measure = candidate
            idx += 1

    if quantity is None and tokens[0] in MEASURE_TO_GRAMS:
        quantity = 1.0
        measure = tokens[0]
        idx = 1

    if quantity is None:
        quantity = 1.0

    ingredient_text = " ".join(tokens[idx:]).strip()
    ingredient_name = _normalize_ingredient(ingredient_text)

    if measure:
        grams = quantity * MEASURE_TO_GRAMS[measure]
    else:
        grams = quantity * 100

    return {"ingredient": ingredient_name, "grams": round(grams, 2)}


def get_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ingredient_name = (meal.get(f"strIngredient{i}") or "").strip()
        if not ingredient_name:
            continue
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        parsed = parse_ingredient(f"{measure} {ingredient_name}".strip())
        if not parsed["ingredient"]:
            parsed["ingredient"] = _normalize_ingredient(ingredient_name)
        ingredients.append(parsed)
    return ingredients


def _calories_per_100g(ingredient):
    ingredient = ingredient.lower().strip()
    if ingredient in CALORIES_DICT:
        return CALORIES_DICT[ingredient]

    for key, calories in CALORIES_DICT.items():
        if key in ingredient or ingredient in key:
            return calories
    return 100


def calculate_calories(ingredients_list):
    total = 0.0
    for item in _merge_ingredients(ingredients_list):
        ingredient = (item.get("ingredient") or "").strip()
        grams = float(item.get("grams") or 0)
        if not ingredient or grams <= 0:
            continue
        kcal_100 = _calories_per_100g(ingredient)
        total += grams * kcal_100 / 100.0
    return int(round(total))


def _save_recipe_ingredients(recipe, ingredients_list):
    merged = _merge_ingredients(ingredients_list)
    RecipeIngredient.objects.filter(recipe=recipe).delete()

    rows = []
    for item in merged:
        ingredient_name = item["ingredient"]
        grams = float(item["grams"])
        kcal_100 = float(_calories_per_100g(ingredient_name))
        ingredient_obj, created = Ingredient.objects.get_or_create(
            name=ingredient_name,
            defaults={"calories_per_100g": kcal_100},
        )
        if not created and ingredient_obj.calories_per_100g is None:
            ingredient_obj.calories_per_100g = kcal_100
            ingredient_obj.save(update_fields=["calories_per_100g"])

        rows.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_obj,
                grams=grams,
            )
        )

    if rows:
        RecipeIngredient.objects.bulk_create(rows)


def fetch_and_save_recipes(query="chicken"):
    encoded_query = quote(query.strip() or "chicken")
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={encoded_query}"

    try:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not fetch recipes from TheMealDB: %s", exc)
        return 0

    meals = payload.get("meals") or []
    saved = 0
    for meal in meals:
        api_id = str(meal.get("idMeal") or "").strip()
        if not api_id:
            continue

        ingredients = get_ingredients(meal)
        calories = calculate_calories(ingredients)

        with transaction.atomic():
            recipe, _ = Recipe.objects.update_or_create(
                api_id=api_id,
                defaults={
                    "name": (meal.get("strMeal") or "").strip(),
                    "category": (meal.get("strCategory") or "").strip() or None,
                    "instructions": (meal.get("strInstructions") or "").strip(),
                    "image_url": (meal.get("strMealThumb") or "").strip() or None,
                    "calories": float(calories),
                },
            )
            _save_recipe_ingredients(recipe, ingredients)

        saved += 1
    return saved
