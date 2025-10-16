# app/models/socket_session.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class SocketSessionModel(Base):
    __tablename__ = "socket_sessions"

    socket_session_id = Column(String(255), primary_key=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.session_id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    connection_status = Column(String(20), nullable=False, default="pending")
    last_heartbeat = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    workout_session = relationship("WorkoutSessionModel", back_populates="socket_session", uselist=False)
    user = relationship("UserModel", back_populates="socket_sessions")
