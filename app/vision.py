import base64
import json
import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
VISION_MODEL = os.environ.get("VISION_MODEL", "llava:7b")

PROMPT = (
    "You are looking at a photo of a meal for a nutrition tracking app. "
    "Identify each distinct food item visible and estimate its serving size "
    "in grams. Respond with ONLY a JSON array, no other text, in this exact "
    'format: [{"name": "grilled chicken breast", "estimated_grams": 150}]'
)


def identify_food_items(image_bytes: bytes) -> list[dict]:
    encoded = base64.b64encode(image_bytes).decode()
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": VISION_MODEL, "prompt": PROMPT, "images": [encoded], "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return _parse_items(resp.json()["response"].strip())


def _parse_items(raw: str) -> list[dict]:
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        items = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return []

    parsed = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        grams = item.get("estimated_grams")
        if not name or not isinstance(grams, (int, float)) or grams <= 0:
            continue
        parsed.append({"name": str(name), "estimated_grams": float(grams)})
    return parsed
