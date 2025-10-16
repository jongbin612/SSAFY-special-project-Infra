# app/websockets/workout_socket.py - 수정된 버전

import json
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.pose_analyzer import PoseAnalyzer
from app.services.socket_service import SocketService
from app.services.workout_service import WorkoutService

router = APIRouter()


class WorkoutMessageHandler:
    """운동 WebSocket 메시지 처리 클래스"""

    def __init__(self, websocket: WebSocket, socket_session_id: str):
        self.websocket = websocket
        self.socket_session_id = socket_session_id
        self.socket_service = SocketService()
        self.workout_service = WorkoutService()
        self.pose_analyzer = PoseAnalyzer()
        self._session_id = None

    async def _get_session_id(self) -> int:
        """소켓 세션으로부터 운동 세션 ID 조회"""
        if self._session_id is None:
            socket_session = await self.socket_service.get_socket_session(self.socket_session_id)
            self._session_id = socket_session.session_id
        return self._session_id

    async def handle_message(self, message: Dict[str, Any]):
        """메시지 타입에 따른 처리"""
        message_type = message.get("type")
        data = message.get("data", {})

        handlers = {
            "heartbeat": self._handle_heartbeat,
            "mediapipe_coordinates": self._handle_mediapipe_coordinates,
            "manual_rep_add": self._handle_manual_rep_add,
            "manual_rep_subtract": self._handle_manual_rep_subtract,
            "get_session_status": self._handle_get_session_status,
            "workout_pause": self._handle_workout_pause,
            "workout_resume": self._handle_workout_resume,
            "workout_stop": self._handle_workout_stop,
        }

        if message_type in handlers:
            return await handlers[message_type](data)

        return None

    async def _handle_heartbeat(self, data: Dict[str, Any]):
        """하트비트 처리"""
        await self.socket_service.update_heartbeat(self.socket_session_id)
        return {
            "type": "heartbeat_ack",
            "data": {"timestamp": data.get("timestamp", datetime.utcnow().isoformat())},
        }

    async def _handle_mediapipe_coordinates(self, data: Dict[str, Any]):
        """미디어파이프 좌표 실시간 분석 처리"""
        landmarks = data.get("landmarks", [])
        session_id = await self._get_session_id()

        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)
        workout_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        # 서비스 객체들 설정
        if session_id in self.pose_analyzer.session_counters:
            counter = self.pose_analyzer.session_counters[session_id]
            if counter.websocket is None:
                counter.set_services(self.websocket, self.workout_service, self.socket_service, self.socket_session_id)

        await self.pose_analyzer.analyze_pose(
            landmarks=landmarks, exercise_type=workout_session.exercise.name, session_id=session_id
        )

        return None

    async def _handle_manual_rep_add(self, data: Dict[str, Any]):
        """수동 반복 추가"""
        reps = data.get("reps", 1)
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)
        await self.workout_service.manual_add_rep(socket_session.session_id, reps)

        updated_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        return {
            "type": "rep_success",
            "data": {
                "rep_detected": True,
                "failed_detected": False,
                "set_completed": False,
                "workout_completed": False,
                "feedback_message": f"{reps}개 수동 추가",
                "session": updated_session.model_dump(mode="json"),
            },
        }

    async def _handle_manual_rep_subtract(self, data: Dict[str, Any]):
        """수동 반복 차감"""
        reps = data.get("reps", 1)
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)
        await self.workout_service.manual_subtract_rep(socket_session.session_id, reps)

        updated_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        return {
            "type": "rep_success",
            "data": {
                "rep_detected": False,
                "failed_detected": False,
                "set_completed": False,
                "workout_completed": False,
                "feedback_message": f"{reps}개 수동 차감",
                "session": updated_session.model_dump(mode="json"),
            },
        }

    async def _handle_get_session_status(self, data: Dict[str, Any]):
        """현재 세션 상태 조회"""
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)
        status = await self.workout_service.get_session_status(socket_session.session_id)
        return {"type": "session_status", "data": status}

    async def _handle_workout_pause(self, data: Dict[str, Any]):
        """운동 일시정지"""
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)

        try:
            await self.workout_service.pause_workout(socket_session.session_id)
            feedback_message = "운동 일시정지"
        except ValueError as e:
            feedback_message = "이미 일시정지 상태입니다"
            print(f"Pause error: {e}")

        updated_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        return {
            "type": "rep_success",
            "data": {
                "rep_detected": False,
                "failed_detected": False,
                "set_completed": False,
                "workout_completed": False,
                "feedback_message": feedback_message,
                "session": updated_session.model_dump(mode="json"),
            },
        }

    async def _handle_workout_resume(self, data: Dict[str, Any]):
        """운동 재개"""
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)

        try:
            await self.workout_service.resume_workout(socket_session.session_id)
            feedback_message = "운동 재개"
        except ValueError as e:
            feedback_message = "이미 활성 상태입니다"
            print(f"Resume error: {e}")

        updated_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        return {
            "type": "rep_success",
            "data": {
                "rep_detected": False,
                "failed_detected": False,
                "set_completed": False,
                "workout_completed": False,
                "feedback_message": feedback_message,
                "session": updated_session.model_dump(mode="json"),
            },
        }

    async def _handle_workout_stop(self, data: Dict[str, Any]):
        """수동 운동 완료"""
        socket_session = await self.socket_service.get_socket_session(self.socket_session_id)

        # 세션 정리
        if self._session_id:
            self.pose_analyzer.cleanup_session(self._session_id)

        # 칼로리 계산 및 완료 처리
        updated_session = await self.workout_service.get_workout_session(
            socket_session.session_id, socket_session.user_id
        )

        total_calories = updated_session.total_reps_completed * updated_session.exercise.calorie
        await self.workout_service.update_total_calories(socket_session.session_id, total_calories)

        # 운동 완료 처리
        await self.workout_service.complete_workout(socket_session.session_id)
        await self.socket_service.update_connection_status(self.socket_session_id, "disconnected")

        # 소켓 종료
        await self.websocket.close()
        return None  # 응답 없이 종료


@router.websocket("/workout/{socket_session_id}")
async def workout_websocket_endpoint(websocket: WebSocket, socket_session_id: str):
    """운동 WebSocket 엔드포인트"""

    await websocket.accept()

    await websocket.send_json(
        {
            "type": "connection_established",
            "data": {
                "socket_session_id": socket_session_id,
                "message": "연결 완료",
                "server_time": datetime.utcnow().isoformat() + "Z",
            },
        }
    )

    socket_service = SocketService()
    await socket_service.update_connection_status(socket_session_id, "connected")
    handler = WorkoutMessageHandler(websocket, socket_session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            response = await handler.handle_message(message)

            if response is not None:
                await websocket.send_json(response)

    except WebSocketDisconnect:
        pass
    finally:
        await socket_service.update_connection_status(socket_session_id, "disconnected")
        if handler._session_id:
            handler.pose_analyzer.cleanup_session(handler._session_id)
