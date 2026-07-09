from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


def create_goal(db: Session, goal_data: dict) -> models.Goal:
    goal = models.Goal(**goal_data)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_latest_goal(db: Session) -> models.Goal | None:
    return db.query(models.Goal).order_by(models.Goal.created_at.desc()).first()


def create_meal_with_items(
    db: Session, logged_on: date, items: list[dict]
) -> models.Meal:
    meal = models.Meal(logged_on=logged_on)
    meal.food_items = [models.FoodItem(**item) for item in items]
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def get_meals(db: Session, on_date: date | None = None) -> list[models.Meal]:
    q = db.query(models.Meal)
    if on_date is not None:
        q = q.filter(models.Meal.logged_on == on_date)
    return q.order_by(models.Meal.created_at.desc()).all()


def get_meal(db: Session, meal_id: int) -> models.Meal | None:
    return db.query(models.Meal).filter(models.Meal.id == meal_id).first()


def get_totals_for_date(db: Session, on_date: date) -> dict:
    row = (
        db.query(
            func.coalesce(func.sum(models.FoodItem.calories), 0.0),
            func.coalesce(func.sum(models.FoodItem.protein_g), 0.0),
            func.coalesce(func.sum(models.FoodItem.carbs_g), 0.0),
            func.coalesce(func.sum(models.FoodItem.fat_g), 0.0),
        )
        .join(models.Meal, models.FoodItem.meal_id == models.Meal.id)
        .filter(models.Meal.logged_on == on_date)
        .one()
    )
    calories, protein_g, carbs_g, fat_g = row
    return {
        "calories": float(calories),
        "protein_g": float(protein_g),
        "carbs_g": float(carbs_g),
        "fat_g": float(fat_g),
    }


def create_recommendation(db: Session, for_date: date, text: str) -> models.Recommendation:
    rec = models.Recommendation(for_date=for_date, text=text)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_latest_recommendation(db: Session, for_date: date) -> models.Recommendation | None:
    return (
        db.query(models.Recommendation)
        .filter(models.Recommendation.for_date == for_date)
        .order_by(models.Recommendation.created_at.desc())
        .first()
    )
