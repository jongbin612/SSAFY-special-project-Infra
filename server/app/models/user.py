# app/models/user.py

from sqlalchemy import BigInteger, Column, Date, DateTime, Float, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    google_id = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(100), nullable=False)
    profile_image_url = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    user_exercises = relationship("UserExerciseModel", back_populates="user")
    workout_sessions = relationship("WorkoutSessionModel", back_populates="user")
    socket_sessions = relationship("SocketSessionModel", back_populates="user")
