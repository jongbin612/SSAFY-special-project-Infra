# app/models/exercise_level.py

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ExerciseLevelModel(Base):
    __tablename__ = "exercise_levels"

    level_id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    level = Column(Integer, nullable=False, comment="1-9999")
    target_sets = Column(Integer, default=3, comment="목표 세트 수")
    target_reps = Column(Integer, default=5, comment="목표 반복 수")
    rest_seconds = Column(Integer, default=30, comment="세트간 휴식 시간")
    experience_points = Column(Integer, default=0, comment="완료시 획득 경험치")
    created_at = Column(DateTime, default=func.now())

    # Relationships
    exercise = relationship("ExerciseModel", back_populates="levels")
    workout_sessions = relationship("WorkoutSessionModel", back_populates="level")

    # Index
    __table_args__ = (Index("ix_exercise_level_unique", "exercise_id", "level", unique=True),)
