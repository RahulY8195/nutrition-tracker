from unittest.mock import Mock, patch

from app.vision import _parse_items, identify_food_items


def test_parse_items_valid_json():
    raw = '[{"name": "grilled chicken breast", "estimated_grams": 150}]'
    result = _parse_items(raw)
    assert result == [{"name": "grilled chicken breast", "estimated_grams": 150.0}]


def test_parse_items_with_surrounding_text():
    raw = (
        "Sure, here's what I see:\n"
        '[{"name": "rice", "estimated_grams": 200}, {"name": "broccoli", "estimated_grams": 80}]'
        "\nLet me know if you need anything else."
    )
    result = _parse_items(raw)
    assert result == [
        {"name": "rice", "estimated_grams": 200.0},
        {"name": "broccoli", "estimated_grams": 80.0},
    ]


def test_parse_items_invalid_json_returns_empty():
    assert _parse_items("I can't identify anything in this image.") == []


def test_parse_items_skips_entries_missing_fields():
    raw = '[{"name": "toast"}, {"estimated_grams": 50}, {"name": "eggs", "estimated_grams": 100}]'
    result = _parse_items(raw)
    assert result == [{"name": "eggs", "estimated_grams": 100.0}]


def test_parse_items_skips_non_positive_grams():
    raw = '[{"name": "salt", "estimated_grams": 0}, {"name": "pepper", "estimated_grams": -5}]'
    assert _parse_items(raw) == []


@patch("app.vision.requests.post")
def test_identify_food_items_calls_ollama_and_parses(mock_post):
    resp = Mock()
    resp.json.return_value = {"response": '[{"name": "apple", "estimated_grams": 180}]'}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    result = identify_food_items(b"fake-image-bytes")

    assert result == [{"name": "apple", "estimated_grams": 180.0}]
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["images"]
    assert call_kwargs["json"]["stream"] is False
