# app/services/socket_service.py

# finalize_workout 메서드 제거하고 기본 기능만 유지
import uuid
from datetime import datetime

from sqlalchemy import update

from app.core.database import get_db
from app.models.socket_session import SocketSessionModel


class SocketService:
    """소켓 세션 관리 서비스"""

    def __init__(self):
        self.db = next(get_db())

    async def create_socket_session(self, session_id: int, user_id: int) -> SocketSessionModel:
        """새로운 소켓 세션 생성"""

        socket_session_id = str(uuid.uuid4())

        socket_session = SocketSessionModel(
            session_id=session_id,
            socket_session_id=socket_session_id,
            user_id=user_id,
            connection_status="pending",
            last_heartbeat=datetime.utcnow(),
        )

        self.db.add(socket_session)
        self.db.commit()
        self.db.refresh(socket_session)

        return socket_session

    async def get_socket_session(self, socket_session_id: str) -> SocketSessionModel | None:
        """소켓 세션 조회"""
        return (
            self.db.query(SocketSessionModel).filter(SocketSessionModel.socket_session_id == socket_session_id).first()
        )

    async def update_connection_status(self, socket_session_id: str, status: str) -> bool:
        """연결 상태 업데이트"""
        try:
            result = self.db.execute(
                update(SocketSessionModel)
                .where(SocketSessionModel.socket_session_id == socket_session_id)
                .values(connection_status=status, last_heartbeat=datetime.utcnow())
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception:
            self.db.rollback()
            return False

    async def update_heartbeat(self, socket_session_id: str) -> bool:
        """하트비트 업데이트"""
        try:
            result = self.db.execute(
                update(SocketSessionModel)
                .where(SocketSessionModel.socket_session_id == socket_session_id)
                .values(last_heartbeat=datetime.utcnow())
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception:
            self.db.rollback()
            return False

    async def get_socket_session_by_workout(self, session_id: int) -> SocketSessionModel | None:
        """운동 세션 ID로 소켓 세션 조회"""
        return self.db.query(SocketSessionModel).filter(SocketSessionModel.session_id == session_id).first()
