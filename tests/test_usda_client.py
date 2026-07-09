from unittest.mock import Mock, patch

import requests

from app.usda_client import lookup_nutrition_per_100g, scale_to_grams


@patch("app.usda_client.requests.get")
def test_lookup_nutrition_per_100g_parses_response(mock_get):
    resp = Mock()
    resp.json.return_value = {
        "foods": [
            {
                "foodNutrients": [
                    {"nutrientId": 1008, "value": 165.0},
                    {"nutrientId": 1003, "value": 31.0},
                    {"nutrientId": 1005, "value": 0.0},
                    {"nutrientId": 1004, "value": 3.6},
                ]
            }
        ]
    }
    resp.raise_for_status.return_value = None
    mock_get.return_value = resp

    result = lookup_nutrition_per_100g("chicken breast")

    assert result == {"calories": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6}


@patch("app.usda_client.requests.get")
def test_lookup_nutrition_per_100g_returns_none_when_no_results(mock_get):
    resp = Mock()
    resp.json.return_value = {"foods": []}
    resp.raise_for_status.return_value = None
    mock_get.return_value = resp

    assert lookup_nutrition_per_100g("nonexistent food xyz") is None


@patch("app.usda_client.requests.get")
def test_lookup_nutrition_per_100g_defaults_missing_nutrients_to_zero(mock_get):
    resp = Mock()
    resp.json.return_value = {"foods": [{"foodNutrients": [{"nutrientId": 1008, "value": 52.0}]}]}
    resp.raise_for_status.return_value = None
    mock_get.return_value = resp

    result = lookup_nutrition_per_100g("apple")

    assert result == {"calories": 52.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}


@patch("app.usda_client.requests.get")
def test_lookup_nutrition_per_100g_returns_none_on_http_error(mock_get):
    resp = Mock()
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
    mock_get.return_value = resp

    assert lookup_nutrition_per_100g("pizza") is None


@patch("app.usda_client.requests.get")
def test_lookup_nutrition_per_100g_returns_none_on_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("network unreachable")

    assert lookup_nutrition_per_100g("pizza") is None


def test_scale_to_grams():
    per_100g = {"calories": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6}
    result = scale_to_grams(per_100g, 150.0)
    assert result == {"calories": 247.5, "protein_g": 46.5, "carbs_g": 0.0, "fat_g": 5.4}


def test_scale_to_grams_zero_grams():
    per_100g = {"calories": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6}
    result = scale_to_grams(per_100g, 0.0)
    assert result == {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
