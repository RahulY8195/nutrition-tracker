from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, usda_client, vision
from app.auth import require_api_key
from app.database import get_db
from app.schemas import MealOut

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/", dependencies=[Depends(require_api_key)], response_model=MealOut)
def log_meal(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = photo.file.read()
    identified = vision.identify_food_items(image_bytes)
    if not identified:
        raise HTTPException(
            status_code=422,
            detail="Couldn't identify any food items in this photo. Try a clearer shot.",
        )

    items = []
    for food in identified:
        per_100g = usda_client.lookup_nutrition_per_100g(food["name"])
        if per_100g is None:
            continue
        nutrition = usda_client.scale_to_grams(per_100g, food["estimated_grams"])
        items.append(
            {
                "name": food["name"],
                "estimated_grams": food["estimated_grams"],
                **nutrition,
            }
        )

    if not items:
        raise HTTPException(
            status_code=422,
            detail="Identified food items but couldn't find nutrition data for any of them.",
        )

    meal = crud.create_meal_with_items(db, date.today(), items)
    return meal


@router.get("/", response_model=list[MealOut])
def list_meals(on_date: date | None = None, db: Session = Depends(get_db)):
    return crud.get_meals(db, on_date=on_date)


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = crud.get_meal(db, meal_id)
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal
