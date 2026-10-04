"""Pydantic schemas for lab/blood test results."""
from datetime import date
from typing import Optional
from pydantic import BaseModel


class LabResultCreate(BaseModel):
    test_name: str
    result_value: float
    unit: str
    reference_range: Optional[str] = None
    test_date: date
    notes: Optional[str] = None


class LabResultUpdate(BaseModel):
    test_name: Optional[str] = None
    result_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    test_date: Optional[date] = None
    notes: Optional[str] = None


class LabResultResponse(BaseModel):
    id: int
    user_id: int
    test_name: str
    result_value: float
    unit: str
    reference_range: Optional[str] = None
    test_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True
