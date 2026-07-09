from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import coach, crud
from app.auth import require_api_key
from app.database import get_db
from app.schemas import RecommendationOut

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate", dependencies=[Depends(require_api_key)], response_model=RecommendationOut)
def generate_recommendation(db: Session = Depends(get_db)):
    today = date.today()
    goal = crud.get_latest_goal(db)
    if goal is None:
        raise HTTPException(status_code=404, detail="Set a goal before requesting a recommendation")

    totals = crud.get_totals_for_date(db, today)
    goal_dict = {
        "daily_calories": goal.daily_calories,
        "daily_protein_g": goal.daily_protein_g,
        "daily_carbs_g": goal.daily_carbs_g,
        "daily_fat_g": goal.daily_fat_g,
    }
    text = coach.generate_recommendation(totals, goal_dict)
    return crud.create_recommendation(db, today, text)


@router.get("/latest", response_model=RecommendationOut)
def get_latest_recommendation(db: Session = Depends(get_db)):
    rec = crud.get_latest_recommendation(db, date.today())
    if rec is None:
        raise HTTPException(status_code=404, detail="No recommendation generated yet today")
    return rec
