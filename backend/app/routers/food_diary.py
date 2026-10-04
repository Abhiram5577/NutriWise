"""Food diary CRUD router."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_diary import FoodDiaryEntry
from app.models.user import User
from app.schemas.food_diary import FoodDiaryCreate, FoodDiaryUpdate, FoodDiaryResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/food-diary", tags=["Food Diary"])


@router.get("/", response_model=List[FoodDiaryResponse])
def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all food diary entries for the current user, newest first."""
    entries = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.user_id == current_user.id)
        .order_by(FoodDiaryEntry.logged_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return entries


@router.get("/date/{entry_date}", response_model=List[FoodDiaryResponse])
def list_entries_by_date(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all food diary entries for a specific date, ordered by meal type."""
    meal_order = {"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}
    entries = (
        db.query(FoodDiaryEntry)
        .filter(
            FoodDiaryEntry.user_id == current_user.id,
            FoodDiaryEntry.entry_date == entry_date,
        )
        .all()
    )
    # Sort in Python to handle custom meal ordering
    entries.sort(key=lambda e: meal_order.get(e.meal_type, 99))
    return entries


@router.get("/{entry_id}", response_model=FoodDiaryResponse)
def get_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a single food diary entry by ID."""
    entry = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.id == entry_id, FoodDiaryEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Food diary entry not found")
    return entry


@router.post("/", response_model=FoodDiaryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(data: FoodDiaryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new food diary entry."""
    entry = FoodDiaryEntry(
        user_id=current_user.id,
        entry_date=data.entry_date or date.today(),
        **data.model_dump(exclude={"entry_date"}),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=FoodDiaryResponse)
def update_entry(entry_id: int, data: FoodDiaryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update an existing food diary entry."""
    entry = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.id == entry_id, FoodDiaryEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Food diary entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a food diary entry."""
    entry = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.id == entry_id, FoodDiaryEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Food diary entry not found")

    db.delete(entry)
    db.commit()
