from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    daily_calories: float
    daily_protein_g: float
    daily_carbs_g: float
    daily_fat_g: float


class GoalOut(GoalCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class FoodItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    estimated_grams: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class MealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    logged_on: date
    created_at: datetime
    food_items: list[FoodItemOut]


class Totals(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class SummaryOut(BaseModel):
    date: date
    totals: Totals
    goal: GoalOut | None


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    for_date: date
    text: str
    created_at: datetime
