import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

REFUSAL_PHRASES = ["i can't", "i cannot", "i'm sorry", "i am sorry"]

FALLBACK_RECOMMENDATION = "Log more meals today for a personalized recommendation."


def _generate(prompt: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def _is_refusal(response: str) -> bool:
    lowered = response.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def _build_prompt(totals: dict, goal: dict) -> str:
    return (
        "You are a nutrition coach reviewing someone's food log for today. "
        "This is not medical advice, just practical day-to-day guidance based "
        "on their own stated goals. Give specific, numbers-based feedback in "
        "2-3 sentences: what they're on track with, and one concrete "
        "suggestion for the rest of the day. Do not refuse or add disclaimers.\n\n"
        f"Today's goal: {goal['daily_calories']:.0f} kcal, "
        f"{goal['daily_protein_g']:.0f}g protein, {goal['daily_carbs_g']:.0f}g carbs, "
        f"{goal['daily_fat_g']:.0f}g fat.\n"
        f"Today's totals so far: {totals['calories']:.0f} kcal, "
        f"{totals['protein_g']:.0f}g protein, {totals['carbs_g']:.0f}g carbs, "
        f"{totals['fat_g']:.0f}g fat.\n\n"
        "Recommendation:"
    )


def generate_recommendation(totals: dict, goal: dict) -> str:
    prompt = _build_prompt(totals, goal)
    result = _generate(prompt)
    if _is_refusal(result):
        result = _generate(prompt)
    if _is_refusal(result):
        return FALLBACK_RECOMMENDATION
    return result
