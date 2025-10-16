# app/models/exercise_category.py

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ExerciseCategoryModel(Base):
    __tablename__ = "exercise_categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    exercises = relationship("ExerciseModel", back_populates="category")
