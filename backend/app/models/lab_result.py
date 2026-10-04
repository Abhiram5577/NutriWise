"""Lab result model for blood/lab values tracking."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship

from app.database import Base


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    test_name = Column(String(100), nullable=False)
    result_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    reference_range = Column(String(100), nullable=True)
    
    test_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="lab_results")
