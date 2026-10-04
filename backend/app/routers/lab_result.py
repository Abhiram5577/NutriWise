"""Lab results router for blood/lab value tracking."""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lab_result import LabResult
from app.schemas.lab_result import LabResultCreate, LabResultUpdate, LabResultResponse
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/lab-results", tags=["Lab Results"])


@router.get("/", response_model=List[LabResultResponse])
def list_lab_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all lab results for the current user."""
    results = (
        db.query(LabResult)
        .filter(LabResult.user_id == current_user.id)
        .order_by(LabResult.test_date.desc(), LabResult.id.desc())
        .all()
    )
    return results


@router.get("/date/{query_date}", response_model=List[LabResultResponse])
def get_lab_results_by_date(
    query_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get lab results for a specific date."""
    results = (
        db.query(LabResult)
        .filter(LabResult.user_id == current_user.id, LabResult.test_date == query_date)
        .order_by(LabResult.id.desc())
        .all()
    )
    return results


@router.post("/", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
def create_lab_result(
    data: LabResultCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record new lab/blood test results."""
    result = LabResult(user_id=current_user.id, **data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.put("/{result_id}", response_model=LabResultResponse)
def update_lab_result(
    result_id: int, 
    data: LabResultUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing lab result."""
    result = (
        db.query(LabResult)
        .filter(LabResult.id == result_id, LabResult.user_id == current_user.id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lab result not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(result, field, value)

    db.commit()
    db.refresh(result)
    return result


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_result(
    result_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a lab result record."""
    result = (
        db.query(LabResult)
        .filter(LabResult.id == result_id, LabResult.user_id == current_user.id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    db.delete(result)
    db.commit()
