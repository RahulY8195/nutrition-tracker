from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import SummaryOut

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/", response_model=SummaryOut)
def get_summary(on_date: date | None = None, db: Session = Depends(get_db)):
    target_date = on_date or date.today()
    totals = crud.get_totals_for_date(db, target_date)
    goal = crud.get_latest_goal(db)
    return SummaryOut(date=target_date, totals=totals, goal=goal)
