# app/models/workout_session.py

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class WorkoutSessionModel(Base):
    __tablename__ = "workout_sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"), nullable=False)
    level_id = Column(Integer, ForeignKey("exercise_levels.level_id"), nullable=False)

    status = Column(String(20), nullable=False, default="active")
    current_set = Column(Integer, nullable=False, default=1)
    current_set_reps = Column(Integer, nullable=False, default=0)
    total_reps_completed = Column(Integer, nullable=False, default=0)
    total_reps_failed = Column(Integer, nullable=False, default=0)
    total_calories_burned = Column(Float, nullable=False, default=0.0)

    # 타이머 관리 필드들
    start_time = Column(DateTime, nullable=False, default=func.now())
    end_time = Column(DateTime, nullable=True)
    last_pause_time = Column(DateTime, nullable=True)
    total_pause_duration = Column(Float, nullable=False, default=0.0)
    duration_seconds = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="workout_sessions")
    exercise = relationship("ExerciseModel", back_populates="workout_sessions")
    level = relationship("ExerciseLevelModel", back_populates="workout_sessions")
    socket_session = relationship("SocketSessionModel", back_populates="workout_session", uselist=False)

    def get_current_duration(self) -> float:
        """현재까지의 실제 운동 시간 계산"""
        if self.status == "completed" and self.end_time:
            return self.duration_seconds

        current_time = datetime.utcnow()
        total_elapsed = (current_time - self.start_time).total_seconds()

        current_pause_time = 0.0
        if self.status == "paused" and self.last_pause_time:
            current_pause_time = (current_time - self.last_pause_time).total_seconds()

        actual_duration = total_elapsed - self.total_pause_duration - current_pause_time
        return max(0.0, actual_duration)

    def is_workout_complete(self) -> bool:
        """현재 세트의 모든 반복이 완료되었는지 확인"""
        if hasattr(self, "level") and self.level:
            return self.current_set > self.level.target_sets
        return False
