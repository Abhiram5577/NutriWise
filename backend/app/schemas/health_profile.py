"""Pydantic schemas for health profile with validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


VALID_GENDERS = {"male", "female", "other", "prefer_not_to_say"}
VALID_ACTIVITY_LEVELS = {"sedentary", "light", "moderate", "active", "very_active"}
VALID_DIETARY_PREFERENCES = {
    "omnivore", "vegetarian", "vegan", "pescatarian",
    "keto", "paleo", "gluten_free", "dairy_free", "other",
}


class HealthProfileCreate(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=150, description="Age in years")
    gender: Optional[str] = Field(None, max_length=20, description="Gender")
    height_cm: Optional[float] = Field(None, gt=0, le=300, description="Height in cm")
    weight_kg: Optional[float] = Field(None, gt=0, le=700, description="Weight in kg")
    activity_level: Optional[str] = Field(None, max_length=50, description="Activity level")
    dietary_preference: Optional[str] = Field(None, max_length=100, description="Dietary preference")
    allergies: Optional[str] = Field(None, max_length=500, description="Comma-separated allergies")
    medical_conditions: Optional[str] = Field(None, max_length=500, description="Comma-separated medical conditions")
    health_goals: Optional[str] = Field(None, max_length=500, description="Comma-separated health goals")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_GENDERS:
                raise ValueError(f"Gender must be one of: {', '.join(sorted(VALID_GENDERS))}")
        return v

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_ACTIVITY_LEVELS:
                raise ValueError(
                    f"Activity level must be one of: {', '.join(sorted(VALID_ACTIVITY_LEVELS))}"
                )
        return v

    @field_validator("dietary_preference")
    @classmethod
    def validate_dietary_preference(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_DIETARY_PREFERENCES:
                raise ValueError(
                    f"Dietary preference must be one of: {', '.join(sorted(VALID_DIETARY_PREFERENCES))}"
                )
        return v


class HealthProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=150, description="Age in years")
    gender: Optional[str] = Field(None, max_length=20, description="Gender")
    height_cm: Optional[float] = Field(None, gt=0, le=300, description="Height in cm")
    weight_kg: Optional[float] = Field(None, gt=0, le=700, description="Weight in kg")
    activity_level: Optional[str] = Field(None, max_length=50, description="Activity level")
    dietary_preference: Optional[str] = Field(None, max_length=100, description="Dietary preference")
    allergies: Optional[str] = Field(None, max_length=500, description="Comma-separated allergies")
    medical_conditions: Optional[str] = Field(None, max_length=500, description="Comma-separated medical conditions")
    health_goals: Optional[str] = Field(None, max_length=500, description="Comma-separated health goals")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_GENDERS:
                raise ValueError(f"Gender must be one of: {', '.join(sorted(VALID_GENDERS))}")
        return v

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_ACTIVITY_LEVELS:
                raise ValueError(
                    f"Activity level must be one of: {', '.join(sorted(VALID_ACTIVITY_LEVELS))}"
                )
        return v

    @field_validator("dietary_preference")
    @classmethod
    def validate_dietary_preference(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_DIETARY_PREFERENCES:
                raise ValueError(
                    f"Dietary preference must be one of: {', '.join(sorted(VALID_DIETARY_PREFERENCES))}"
                )
        return v


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    health_goals: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
