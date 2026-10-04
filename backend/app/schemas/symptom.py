"""Pydantic schemas for symptom tracking."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, constr, validator


class SymptomCreate(BaseModel):
    symptom_name: str
    severity: str
    symptom_date: date
    notes: Optional[str] = None

    @validator('severity')
    def severity_must_be_valid(cls, v):
        valid = ['mild', 'moderate', 'severe']
        if v.lower() not in valid:
            raise ValueError(f"Severity must be one of {valid}")
        return v.lower()


class SymptomUpdate(BaseModel):
    symptom_name: Optional[str] = None
    severity: Optional[str] = None
    symptom_date: Optional[date] = None
    notes: Optional[str] = None

    @validator('severity')
    def severity_must_be_valid(cls, v):
        if v is None:
            return v
        valid = ['mild', 'moderate', 'severe']
        if v.lower() not in valid:
            raise ValueError(f"Severity must be one of {valid}")
        return v.lower()


class SymptomResponse(BaseModel):
    id: int
    user_id: int
    symptom_name: str
    severity: str
    symptom_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True
