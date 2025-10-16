# app/models/user_exercise.py

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class UserExerciseModel(Base):
    __tablename__ = "user_exercises"

    user_exercise_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    current_level = Column(Integer, default=1, comment="현재 도전 가능한 레벨")
    highest_completed_level = Column(Integer, default=0, comment="최고 완료 레벨")
    total_sessions = Column(Integer, default=0)
    total_reps_completed = Column(Integer, default=0)
    total_time_exercised = Column(Integer, default=0, comment="seconds")
    total_experience_points = Column(Integer, default=0)
    last_performed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserModel")
    exercise = relationship("ExerciseModel", back_populates="user_exercises")

    # Index
    __table_args__ = (Index("ix_user_exercise_unique", "user_id", "exercise_id", unique=True),)
