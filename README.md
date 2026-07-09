# AI Nutrition Tracker

Log a meal by taking a photo. A local vision model identifies the food items and estimates portion sizes; nutrition facts come from the USDA FoodData Central database, not model guesses. Tracks daily totals against a goal and generates coaching recommendations.

## Features

- Photo-based meal logging: a local vision model (`llava`) identifies food items and estimates serving size directly from an image
- Nutrition facts (calories, protein, carbs, fat) come from the USDA FoodData Central API, scaled to the estimated serving size
- Daily calorie/macro goals, tracked against today's logged totals
- AI-generated coaching recommendations based on how today's totals compare to the goal
- REST API with API-key auth on write endpoints
- Streamlit UI: upload a photo, see the identified items, track progress, get a recommendation
- Runs entirely locally (Ollama) except for the USDA lookup — no LLM API costs
- Two-tier test suite: offline unit tests (network mocked) and API integration tests against a real Postgres database, both run in CI

## Architecture

```
app/
  database.py         SQLAlchemy engine/session (PostgreSQL)
  models.py            Goal, Meal, FoodItem, Recommendation
  schemas.py            Pydantic request/response models
  auth.py                 API key auth
  vision.py                 photo -> identified food items (Ollama vision model)
  usda_client.py              USDA FoodData Central lookup + serving-size scaling
  coach.py                       goal + totals -> coaching recommendation (Ollama)
  crud.py                          database access
  routers/                          meals, goals, summary, recommendations
  main.py                             FastAPI app
frontend/
  streamlit_app.py                     UI (API client)
tests/
  test_vision.py, test_usda_client.py, test_coach.py, test_auth.py    unit tier
  test_api_integration.py                                             integration tier
```

## Tech Stack

Python, FastAPI, PostgreSQL, Ollama (local vision + text models), USDA FoodData Central API, Streamlit, Docker Compose, pytest, GitHub Actions.

## Setup

1. Get a free USDA FoodData Central API key at https://fdc.nal.usda.gov/api-key-signup — the shared `DEMO_KEY` is rate-limited across all users and will not work reliably.
2. Copy `.env.example` to `.env` and set `USDA_API_KEY`.
3. Start everything:
   ```bash
   docker compose up -d --build
   ```
4. Pull the local models (one-time, after containers are up):
   ```bash
   docker compose exec ollama ollama pull llama3.2:1b
   docker compose exec ollama ollama pull llava:7b
   ```

The API runs on http://localhost:8001, the UI on http://localhost:8502 (offset from the default FastAPI/Streamlit/Postgres/Ollama ports so this can run alongside other local projects using the standard ports).

## Usage

### UI

Open http://localhost:8502. Set your daily goals in the sidebar, upload a photo of a meal, click **Analyze & Log**, then **Get Recommendation**.

### API

Set a goal (requires `X-API-Key`):

```bash
curl -X POST "http://localhost:8001/goals/" \
  -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"daily_calories": 2000, "daily_protein_g": 120, "daily_carbs_g": 200, "daily_fat_g": 65}'
```

Log a meal from a photo:

```bash
curl -X POST "http://localhost:8001/meals/" \
  -H "X-API-Key: dev-key" \
  -F "photo=@meal.jpg"
```

Get today's totals vs. goal:

```bash
curl "http://localhost:8001/summary/"
```

Generate a coaching recommendation:

```bash
curl -X POST "http://localhost:8001/recommendations/generate" -H "X-API-Key: dev-key"
```

Full API docs: http://localhost:8001/docs

## Tests

```bash
pip install -r requirements.txt
pytest -v
```

Two tiers:

- **Unit tests** (`test_vision.py`, `test_usda_client.py`, `test_coach.py`, `test_auth.py`) — pure logic, network calls mocked, no external services required.
- **API integration tests** (`test_api_integration.py`) — exercise the full request path through FastAPI, SQLAlchemy, and a real Postgres database (the vision model, USDA lookup, and coaching LLM call are mocked; only persistence and request handling are real). These need Postgres running:

  ```bash
  docker compose up -d db
  pytest -v
  ```

  If Postgres isn't reachable, this file's tests are skipped automatically rather than failing — CI runs both tiers via a Postgres service container.

## How meal logging works

1. `POST /meals` sends the uploaded photo to a local vision model, which returns each identified food item with an estimated serving size in grams.
2. Each item is looked up in USDA FoodData Central for its per-100g nutrition, then scaled to the estimated serving size.
3. The meal and its food items are stored in Postgres.
4. `POST /recommendations/generate` pulls today's totals, compares them to the goal, and asks the LLM for specific, numbers-based coaching advice.
