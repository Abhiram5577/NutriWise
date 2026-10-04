"""Nutrition integration router."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from pydantic import BaseModel

from app.services.nutrition_service import NutritionService
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition Integration"])


class NutritionSearchResult(BaseModel):
    food_name: str
    calories_100g: float
    protein_100g: float
    carbs_100g: float
    fat_100g: float
    fiber_100g: float
    default_serving_g: float
    image_url: str


@router.get("/search", response_model=List[NutritionSearchResult])
async def search_nutrition(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Search the external nutrition database (Open Food Facts) for food items.
    Returns normalized nutritional data per 100g.
    """
    try:
        results = await NutritionService.search_food(query, limit)
        return results
    except Exception as e:
        # Gracefully handle API failures
        raise HTTPException(
            status_code=503,
            detail="External nutrition service is currently unavailable. Please enter food manually."
        )
