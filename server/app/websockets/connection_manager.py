# app/websockets/connection_manager.py

import json
from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 연결 관리자"""

    def __init__(self):
        # 활성 연결들을 관리
        self.active_connections: Dict[str, WebSocket] = {}
        # 사용자별 소켓 세션 매핑
        self.user_sessions: Dict[int, str] = {}
        # 운동 세션별 소켓 세션 매핑
        self.workout_sessions: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, socket_session_id: str, user_id: int, workout_session_id: int):
        """새로운 WebSocket 연결 등록"""
        await websocket.accept()

        self.active_connections[socket_session_id] = websocket
        self.user_sessions[user_id] = socket_session_id
        self.workout_sessions[workout_session_id] = socket_session_id

        print(f"User {user_id} connected with socket session {socket_session_id}")

    def disconnect(self, socket_session_id: str):
        """WebSocket 연결 해제"""
        if socket_session_id in self.active_connections:
            del self.active_connections[socket_session_id]

        # 사용자 매핑에서도 제거
        user_id_to_remove = None
        workout_session_to_remove = None

        for user_id, session_id in self.user_sessions.items():
            if session_id == socket_session_id:
                user_id_to_remove = user_id
                break

        for workout_id, session_id in self.workout_sessions.items():
            if session_id == socket_session_id:
                workout_session_to_remove = workout_id
                break

        if user_id_to_remove:
            del self.user_sessions[user_id_to_remove]
        if workout_session_to_remove:
            del self.workout_sessions[workout_session_to_remove]

    async def send_personal_message(self, socket_session_id: str, message: dict):
        """특정 연결에 메시지 전송"""
        if socket_session_id in self.active_connections:
            websocket = self.active_connections[socket_session_id]
            await websocket.send_text(json.dumps(message))

    async def send_to_user(self, user_id: int, message: dict):
        """특정 사용자에게 메시지 전송"""
        if user_id in self.user_sessions:
            socket_session_id = self.user_sessions[user_id]
            await self.send_personal_message(socket_session_id, message)

    def get_connection_count(self) -> int:
        """현재 활성 연결 수 반환"""
        return len(self.active_connections)


# 글로벌 연결 관리자 인스턴스
connection_manager = ConnectionManager()
