from unittest.mock import Mock, patch

from app.coach import FALLBACK_RECOMMENDATION, generate_recommendation

TOTALS = {"calories": 1200.0, "protein_g": 80.0, "carbs_g": 130.0, "fat_g": 40.0}
GOAL = {"daily_calories": 2000.0, "daily_protein_g": 120.0, "daily_carbs_g": 200.0, "daily_fat_g": 65.0}


def _mock_response(text: str) -> Mock:
    resp = Mock()
    resp.json.return_value = {"response": text}
    resp.raise_for_status.return_value = None
    return resp


@patch("app.coach.requests.post")
def test_generate_recommendation_returns_model_response(mock_post):
    mock_post.return_value = _mock_response("You're on track. Add a protein-rich snack tonight.")
    result = generate_recommendation(TOTALS, GOAL)
    assert result == "You're on track. Add a protein-rich snack tonight."


@patch("app.coach.requests.post")
def test_generate_recommendation_retries_once_on_refusal(mock_post):
    mock_post.side_effect = [
        _mock_response("I'm sorry, I can't give medical advice."),
        _mock_response("Add more vegetables to your next meal."),
    ]
    result = generate_recommendation(TOTALS, GOAL)
    assert result == "Add more vegetables to your next meal."
    assert mock_post.call_count == 2


@patch("app.coach.requests.post")
def test_generate_recommendation_falls_back_after_two_refusals(mock_post):
    mock_post.return_value = _mock_response("I cannot provide that.")
    result = generate_recommendation(TOTALS, GOAL)
    assert result == FALLBACK_RECOMMENDATION
    assert mock_post.call_count == 2


@patch("app.coach.requests.post")
def test_generate_recommendation_includes_totals_and_goal_in_prompt(mock_post):
    mock_post.return_value = _mock_response("Looks good.")
    generate_recommendation(TOTALS, GOAL)
    prompt_sent = mock_post.call_args.kwargs["json"]["prompt"]
    assert "1200" in prompt_sent
    assert "2000" in prompt_sent
