"""Health profile model storing user biometrics and preferences."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String(50), nullable=True)  # sedentary, light, moderate, active, very_active
    dietary_preference = Column(String(100), nullable=True)  # omnivore, vegetarian, vegan, etc.
    allergies = Column(String(500), nullable=True)  # comma-separated list
    medical_conditions = Column(String(500), nullable=True)
    health_goals = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_profile")
