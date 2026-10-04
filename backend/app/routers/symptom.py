"""Symptom tracking router."""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.symptom import Symptom
from app.schemas.symptom import SymptomCreate, SymptomUpdate, SymptomResponse
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/symptoms", tags=["Symptoms"])


@router.get("/", response_model=List[SymptomResponse])
def list_symptoms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all symptom records for the current user."""
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.symptom_date.desc(), Symptom.id.desc())
        .all()
    )
    return symptoms


@router.get("/date/{query_date}", response_model=List[SymptomResponse])
def get_symptoms_by_date(
    query_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get symptom records for a specific date."""
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id, Symptom.symptom_date == query_date)
        .order_by(Symptom.id.desc())
        .all()
    )
    return symptoms


@router.post("/", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
def create_symptom(
    data: SymptomCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a new symptom."""
    symptom = Symptom(user_id=current_user.id, **data.model_dump())
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom


@router.put("/{symptom_id}", response_model=SymptomResponse)
def update_symptom(
    symptom_id: int, 
    data: SymptomUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing symptom."""
    symptom = (
        db.query(Symptom)
        .filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id)
        .first()
    )
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(symptom, field, value)

    db.commit()
    db.refresh(symptom)
    return symptom


@router.delete("/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_symptom(
    symptom_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a symptom record."""
    symptom = (
        db.query(Symptom)
        .filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id)
        .first()
    )
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    db.delete(symptom)
    db.commit()
