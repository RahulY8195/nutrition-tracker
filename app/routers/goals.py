from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.auth import require_api_key
from app.database import get_db
from app.schemas import GoalCreate, GoalOut

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", dependencies=[Depends(require_api_key)], response_model=GoalOut)
def set_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    return crud.create_goal(db, goal.model_dump())


@router.get("/latest", response_model=GoalOut)
def get_latest_goal(db: Session = Depends(get_db)):
    goal = crud.get_latest_goal(db)
    if goal is None:
        raise HTTPException(status_code=404, detail="No goal set yet")
    return goal
