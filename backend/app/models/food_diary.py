"""Food diary entry model with macro and micronutrient tracking."""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FoodDiaryEntry(Base):
    __tablename__ = "food_diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Food info
    food_name = Column(String(255), nullable=False)
    quantity_g = Column(Float, nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    notes = Column(Text, nullable=True)

    # Date for grouping / date-based queries
    entry_date = Column(Date, default=date.today, nullable=False, index=True)

    # Macronutrients
    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)

    # Micronutrients
    vitamin_a_mcg = Column(Float, nullable=True)
    vitamin_c_mg = Column(Float, nullable=True)
    calcium_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)

    logged_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="food_diary_entries")
