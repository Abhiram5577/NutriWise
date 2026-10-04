"""User model for authentication and profile ownership."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    food_diary_entries = relationship("FoodDiaryEntry", back_populates="user")
    symptoms = relationship("Symptom", back_populates="user")
    lab_results = relationship("LabResult", back_populates="user")
