"""Pydantic schemas for food diary entries with validation."""

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack"}


class FoodDiaryCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=255, description="Name of the food")
    quantity_g: float = Field(..., gt=0, le=10000, description="Quantity in grams")
    meal_type: str = Field(..., max_length=50, description="Meal type")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    entry_date: Optional[date] = Field(None, description="Date of the entry. Defaults to today.")
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    vitamin_a_mcg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)

    @field_validator("food_name")
    @classmethod
    def clean_food_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_MEAL_TYPES:
            raise ValueError(f"Meal type must be one of: {', '.join(sorted(VALID_MEAL_TYPES))}")
        return v


class FoodDiaryUpdate(BaseModel):
    food_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity_g: Optional[float] = Field(None, gt=0, le=10000)
    meal_type: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    vitamin_a_mcg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)

    @field_validator("food_name")
    @classmethod
    def clean_food_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_MEAL_TYPES:
                raise ValueError(f"Meal type must be one of: {', '.join(sorted(VALID_MEAL_TYPES))}")
        return v


class FoodDiaryResponse(BaseModel):
    id: int
    user_id: int
    food_name: str
    quantity_g: float
    meal_type: str
    notes: Optional[str] = None
    entry_date: Optional[date] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    vitamin_a_mcg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    logged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    """Aggregated daily nutrition totals."""
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    entry_count: int
