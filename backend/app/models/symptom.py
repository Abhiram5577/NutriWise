"""Symptom assessment model for tracking health symptoms."""
from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship

from app.database import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptom_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # mild, moderate, severe
    symptom_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="symptoms")
