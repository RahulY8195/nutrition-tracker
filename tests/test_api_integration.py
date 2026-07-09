import pytest

from tests.conftest import POSTGRES_AVAILABLE

pytestmark = pytest.mark.skipif(
    not POSTGRES_AVAILABLE,
    reason="Postgres not reachable at DATABASE_URL; run `docker compose up -d db` to enable these tests",
)

GOAL_PAYLOAD = {
    "daily_calories": 2000,
    "daily_protein_g": 120,
    "daily_carbs_g": 200,
    "daily_fat_g": 65,
}

FAKE_IDENTIFIED_ITEMS = [
    {"name": "grilled chicken breast", "estimated_grams": 150.0},
    {"name": "white rice", "estimated_grams": 200.0},
]

FAKE_NUTRITION_BY_NAME = {
    "grilled chicken breast": {"calories": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6},
    "white rice": {"calories": 130.0, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3},
}


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    monkeypatch.setattr(
        "app.routers.meals.vision.identify_food_items",
        lambda image_bytes: FAKE_IDENTIFIED_ITEMS,
    )
    monkeypatch.setattr(
        "app.routers.meals.usda_client.lookup_nutrition_per_100g",
        lambda name: FAKE_NUTRITION_BY_NAME.get(name),
    )
    monkeypatch.setattr(
        "app.routers.recommendations.coach.generate_recommendation",
        lambda totals, goal: "Great job staying on track. Add a vegetable side for dinner.",
    )


def _log_fake_meal(client):
    return client.post(
        "/meals/",
        files={"photo": ("meal.jpg", b"fake-image-bytes", "image/jpeg")},
        headers={"X-API-Key": "dev-key"},
    )


def test_set_and_get_latest_goal(client):
    resp = client.post("/goals/", json=GOAL_PAYLOAD, headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 200
    assert resp.json()["daily_calories"] == 2000

    latest = client.get("/goals/latest")
    assert latest.status_code == 200
    assert latest.json()["daily_protein_g"] == 120


def test_get_goal_404_when_none_set(client):
    resp = client.get("/goals/latest")
    assert resp.status_code == 404


def test_set_goal_requires_api_key(client):
    resp = client.post("/goals/", json=GOAL_PAYLOAD)
    assert resp.status_code in (401, 422)


def test_log_meal_requires_api_key(client):
    resp = client.post("/meals/", files={"photo": ("meal.jpg", b"bytes", "image/jpeg")})
    assert resp.status_code in (401, 422)


def test_log_meal_creates_meal_with_scaled_nutrition(client):
    resp = _log_fake_meal(client)
    assert resp.status_code == 200
    body = resp.json()

    assert len(body["food_items"]) == 2
    chicken = next(i for i in body["food_items"] if i["name"] == "grilled chicken breast")
    assert chicken["estimated_grams"] == 150.0
    assert chicken["calories"] == pytest.approx(247.5)
    assert chicken["protein_g"] == pytest.approx(46.5)


def test_log_meal_422_when_nothing_identified(client, monkeypatch):
    monkeypatch.setattr("app.routers.meals.vision.identify_food_items", lambda image_bytes: [])
    resp = _log_fake_meal(client)
    assert resp.status_code == 422


def test_log_meal_422_when_no_nutrition_data_found(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.meals.usda_client.lookup_nutrition_per_100g", lambda name: None
    )
    resp = _log_fake_meal(client)
    assert resp.status_code == 422


def test_list_meals_and_get_single_meal(client):
    logged = _log_fake_meal(client).json()

    listed = client.get("/meals/").json()
    assert len(listed) == 1
    assert listed[0]["id"] == logged["id"]

    fetched = client.get(f"/meals/{logged['id']}")
    assert fetched.status_code == 200
    assert len(fetched.json()["food_items"]) == 2


def test_get_meal_404_for_unknown_id(client):
    resp = client.get("/meals/999999")
    assert resp.status_code == 404


def test_summary_reflects_logged_meals_and_goal(client):
    client.post("/goals/", json=GOAL_PAYLOAD, headers={"X-API-Key": "dev-key"})
    _log_fake_meal(client)

    summary = client.get("/summary/").json()
    assert summary["totals"]["calories"] == pytest.approx(247.5 + 260.0)
    assert summary["goal"]["daily_calories"] == 2000


def test_summary_goal_is_none_when_not_set(client):
    _log_fake_meal(client)
    summary = client.get("/summary/").json()
    assert summary["goal"] is None
    assert summary["totals"]["calories"] > 0


def test_generate_recommendation_requires_goal_to_exist(client):
    resp = client.post("/recommendations/generate", headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 404


def test_generate_recommendation_creates_and_persists(client):
    client.post("/goals/", json=GOAL_PAYLOAD, headers={"X-API-Key": "dev-key"})
    _log_fake_meal(client)

    resp = client.post("/recommendations/generate", headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 200
    assert "vegetable" in resp.json()["text"]

    latest = client.get("/recommendations/latest")
    assert latest.status_code == 200
    assert latest.json()["text"] == resp.json()["text"]


def test_get_latest_recommendation_404_when_none_generated(client):
    resp = client.get("/recommendations/latest")
    assert resp.status_code == 404
