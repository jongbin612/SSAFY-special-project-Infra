# app/models/exercise.py

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ExerciseModel(Base):
    __tablename__ = "exercises"

    exercise_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    calorie = Column(Float, nullable=True, comment="반복당 소모 칼로리")
    category_id = Column(Integer, ForeignKey("exercise_categories.category_id"), nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    target_image_url = Column(Text, nullable=True)
    howto_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    category = relationship("ExerciseCategoryModel", back_populates="exercises")
    levels = relationship("ExerciseLevelModel", back_populates="exercise")
    user_exercises = relationship("UserExerciseModel", back_populates="exercise")
    workout_sessions = relationship("WorkoutSessionModel", back_populates="exercise")
    workout_sessions = relationship("WorkoutSessionModel", back_populates="exercise")
