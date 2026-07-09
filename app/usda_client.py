import os

import requests

USDA_API_KEY = os.environ.get("USDA_API_KEY", "DEMO_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

NUTRIENT_IDS = {
    "calories": 1008,
    "protein_g": 1003,
    "carbs_g": 1005,
    "fat_g": 1004,
}


def lookup_nutrition_per_100g(food_name: str) -> dict | None:
    try:
        resp = requests.get(
            USDA_SEARCH_URL,
            params={"query": food_name, "pageSize": 1, "api_key": USDA_API_KEY},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    foods = resp.json().get("foods", [])
    if not foods:
        return None

    nutrients_by_id = {
        n.get("nutrientId"): n.get("value", 0.0) for n in foods[0].get("foodNutrients", [])
    }
    return {key: float(nutrients_by_id.get(nid, 0.0)) for key, nid in NUTRIENT_IDS.items()}


def scale_to_grams(per_100g: dict, grams: float) -> dict:
    factor = grams / 100.0
    return {key: round(value * factor, 1) for key, value in per_100g.items()}
