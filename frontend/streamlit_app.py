import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "dev-key")

st.set_page_config(page_title="AI Nutrition Tracker", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --surface-1: #fcfcfb;
        --page-plane: #f9f9f7;
        --text-primary: #0b0b0b;
        --text-secondary: #52514e;
        --text-muted: #898781;
        --border: rgba(11,11,11,0.10);
        --accent: #2a78d6;
        --accent-track: #cde2fb;
        --good: #0ca30c;
        --warning: #fab219;
    }

    .hero {
        padding: 12px 0 8px 0;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        margin-top: 10px;
        max-width: 640px;
        line-height: 1.5;
    }
    .hero-cta {
        margin-top: 20px;
    }
    .hero-cta a {
        display: inline-block;
        background: var(--accent);
        color: #ffffff;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 10px 22px;
        border-radius: 8px;
        text-decoration: none;
    }

    .lede {
        font-size: 1.05rem;
        color: var(--text-secondary);
        line-height: 1.65;
        max-width: 660px;
        margin: 4px 0 32px 0;
    }

    .feature-card {
        height: 100%;
    }
    .feature-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 8px;
        border: 1px solid var(--border);
        color: var(--accent);
        font-weight: 700;
        font-size: 0.85rem;
        font-variant-numeric: tabular-nums;
        margin-bottom: 10px;
    }
    .feature-title {
        font-weight: 700;
        color: var(--text-primary);
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .feature-body {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .divider-line {
        border: none;
        border-top: 1px solid var(--border);
        margin: 40px 0 0 0;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin: 28px 0 10px 0;
    }
    .page-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 6px 0 20px 0;
    }

    .card {
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }

    .food-item-name {
        font-weight: 700;
        color: var(--text-primary);
        font-size: 1rem;
    }
    .food-item-grams {
        color: var(--text-muted);
        font-weight: 500;
    }
    .food-item-macros {
        color: var(--text-secondary);
        font-size: 0.88rem;
        margin-top: 4px;
    }

    .meter-row {
        margin-bottom: 18px;
    }
    .meter-label {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        font-size: 0.88rem;
        margin-bottom: 6px;
    }
    .meter-name {
        color: var(--text-primary);
        font-weight: 600;
    }
    .meter-value {
        color: var(--text-secondary);
        font-variant-numeric: tabular-nums;
    }
    .meter-track {
        width: 100%;
        height: 10px;
        border-radius: 6px;
        background: var(--accent-track);
        overflow: hidden;
    }
    .meter-fill {
        height: 100%;
        border-radius: 6px;
        background: var(--accent);
    }
    .meter-fill.over {
        background: var(--warning);
    }
    .meter-over-note {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.8rem;
        color: var(--warning);
        margin-top: 5px;
        font-weight: 600;
    }

    .recommendation-card {
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 10px;
        padding: 16px 18px;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .empty-state {
        color: var(--text-muted);
        font-size: 0.9rem;
        padding: 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <p class="hero-title">Nutrition tracking, simplified.</p>
        <p class="hero-subtitle">
            AI Nutrition Tracker turns a photo of your plate into a full nutrition
            breakdown in seconds, verified against USDA data instead of guessed
            by a model.
        </p>
        <div class="hero-cta"><a href="#tracker">Start tracking</a></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="section-label" style="margin-top: 48px;">Why it matters</p>
    <p class="lede">
        Most nutrition tracking fails for one reason: logging food is tedious.
        Searching a database and estimating portions by hand takes long enough
        that most people quit within days. Research consistently links
        self-monitoring to better outcomes — the friction of doing it, not the
        value of doing it, is the real barrier. Removing that friction is the
        whole idea behind this tool.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="section-label">How it works</p>', unsafe_allow_html=True)
feature_cols = st.columns(3)
features = [
    (
        "01",
        "Capture",
        "Take a photo of your plate. No searching a food database, no manual entry.",
    ),
    (
        "02",
        "Identify",
        "A vision model recognizes each food item in the photo and estimates its portion size.",
    ),
    (
        "03",
        "Verify",
        "Every item is matched against the USDA FoodData Central database — real nutrition data, not a model's guess.",
    ),
]
for col, (number, title, body) in zip(feature_cols, features):
    with col:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-number">{number}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-body">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
st.markdown(
    '<p id="tracker" class="page-title">Try the tracker</p>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<p class="section-label">Daily Goals</p>', unsafe_allow_html=True)
    calories = st.number_input("Calories", min_value=0, value=2000, step=50)
    protein = st.number_input("Protein (g)", min_value=0, value=120, step=5)
    carbs = st.number_input("Carbs (g)", min_value=0, value=200, step=5)
    fat = st.number_input("Fat (g)", min_value=0, value=65, step=5)
    if st.button("Save Goals", width="stretch", type="primary"):
        try:
            resp = requests.post(
                f"{API_URL}/goals/",
                json={
                    "daily_calories": calories,
                    "daily_protein_g": protein,
                    "daily_carbs_g": carbs,
                    "daily_fat_g": fat,
                },
                headers={"X-API-Key": API_KEY},
                timeout=15,
            )
            resp.raise_for_status()
            st.success("Goals saved.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Couldn't save goals: {exc}")

st.markdown('<p class="section-label">Log a Meal</p>', unsafe_allow_html=True)
photo = st.file_uploader(
    "Photo of your meal", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
)
if photo:
    preview_col, button_col = st.columns([2, 1])
    with preview_col:
        st.image(photo, width="stretch")
    with button_col:
        st.write("")
        st.write("")
        analyze_clicked = st.button("Analyze & Log", type="primary", width="stretch")
    if analyze_clicked:
        with st.spinner("Identifying food items and looking up nutrition data..."):
            try:
                resp = requests.post(
                    f"{API_URL}/meals/",
                    files={"photo": (photo.name, photo.getvalue(), photo.type)},
                    headers={"X-API-Key": API_KEY},
                    timeout=120,
                )
                resp.raise_for_status()
                st.session_state["last_meal"] = resp.json()
            except requests.exceptions.RequestException as exc:
                st.error(f"Couldn't log this meal: {exc}")

last_meal = st.session_state.get("last_meal")
if last_meal:
    st.success(f"Logged {len(last_meal['food_items'])} item(s).")
    for item in last_meal["food_items"]:
        st.markdown(
            f"""
            <div class="card">
                <span class="food-item-name">{item['name']}</span>
                <span class="food-item-grams"> · {item['estimated_grams']:.0f}g</span>
                <div class="food-item-macros">
                    {item['calories']:.0f} kcal &nbsp;·&nbsp;
                    {item['protein_g']:.0f}g protein &nbsp;·&nbsp;
                    {item['carbs_g']:.0f}g carbs &nbsp;·&nbsp;
                    {item['fat_g']:.0f}g fat
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<p class="section-label">Today\'s Progress</p>', unsafe_allow_html=True)
try:
    summary = requests.get(f"{API_URL}/summary/", timeout=15).json()
    totals = summary["totals"]
    goal = summary["goal"]

    if goal is None:
        st.markdown(
            '<div class="empty-state">Set your daily goals in the sidebar to see progress.</div>',
            unsafe_allow_html=True,
        )
    else:
        meters = [
            ("Calories", "calories", "daily_calories", "kcal"),
            ("Protein", "protein_g", "daily_protein_g", "g"),
            ("Carbs", "carbs_g", "daily_carbs_g", "g"),
            ("Fat", "fat_g", "daily_fat_g", "g"),
        ]
        meter_html = ""
        for label, total_key, goal_key, unit in meters:
            current = totals[total_key]
            target = goal[goal_key]
            pct = min(current / target, 1.0) if target > 0 else 0.0
            is_over = target > 0 and current > target
            fill_class = "meter-fill over" if is_over else "meter-fill"
            over_note = (
                f'<div class="meter-over-note">{current - target:.0f}{unit} over goal</div>'
                if is_over
                else ""
            )
            meter_html += f"""
            <div class="meter-row">
                <div class="meter-label">
                    <span class="meter-name">{label}</span>
                    <span class="meter-value">{current:.0f} / {target:.0f} {unit}</span>
                </div>
                <div class="meter-track">
                    <div class="{fill_class}" style="width: {pct * 100:.1f}%;"></div>
                </div>
                {over_note}
            </div>
            """
        st.markdown(meter_html, unsafe_allow_html=True)
except requests.exceptions.RequestException as exc:
    st.error(f"Couldn't load today's summary: {exc}")

st.markdown('<p class="section-label">Coaching Recommendation</p>', unsafe_allow_html=True)
if st.button("Get Recommendation"):
    with st.spinner("Generating recommendation..."):
        try:
            resp = requests.post(
                f"{API_URL}/recommendations/generate",
                headers={"X-API-Key": API_KEY},
                timeout=60,
            )
            resp.raise_for_status()
            st.session_state["recommendation"] = resp.json()["text"]
        except requests.exceptions.RequestException as exc:
            st.error(f"Couldn't generate a recommendation: {exc}")

if st.session_state.get("recommendation"):
    st.markdown(
        f'<div class="recommendation-card">{st.session_state["recommendation"]}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="empty-state">No recommendation yet — log a meal and click above.</div>',
        unsafe_allow_html=True,
    )
