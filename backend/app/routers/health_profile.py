"""Health profile router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.health_profile import HealthProfile
from app.models.user import User
from app.schemas.health_profile import HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/health-profile", tags=["Health Profile"])


@router.get("/", response_model=HealthProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current user's health profile."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found. Create one first.")
    return profile


@router.post("/", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(data: HealthProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a health profile for the current user."""
    existing = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Health profile already exists. Use PUT to update.")

    profile = HealthProfile(user_id=current_user.id, **data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/", response_model=HealthProfileResponse)
def update_profile(data: HealthProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update the current user's health profile."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found. Create one first.")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
