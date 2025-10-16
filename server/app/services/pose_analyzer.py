# app/services/pose_analyzer.py

import asyncio
import threading
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import tensorflow as tf

from app.utils import PushupCounter, SquatCounter, preprocess_pushup, preprocess_squat


class SessionCounter:
    """세션별 운동 카운터 래퍼"""

    def __init__(self, session_id: int, exercise_type: str):
        self.session_id = session_id
        self.exercise_type = exercise_type
        self.counter = None

        # 서비스 객체들
        self.websocket = None
        self.workout_service = None
        self.socket_service = None
        self.socket_session_id = None

        # 운동 타입에 따른 카운터 생성
        if exercise_type == "푸쉬업":
            self.counter = PushupCounter(threshold=0.7, callback=self._handle_counter_message)
        elif exercise_type == "스쿼트":
            self.counter = SquatCounter(threshold=0.7, callback=self._handle_counter_message)

        self.counter.start()

    def set_services(self, websocket, workout_service, socket_service, socket_session_id):
        """서비스 객체들 설정"""
        self.websocket = websocket
        self.workout_service = workout_service
        self.socket_service = socket_service
        self.socket_session_id = socket_session_id

    def _handle_counter_message(self, message_data: Dict[str, Any]):
        """카운터에서 생성된 메시지 처리"""
        if message_data:

            def process_message():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._process_message_async(message_data))
                loop.close()

            thread = threading.Thread(target=process_message, daemon=True)
            thread.start()

    async def _process_message_async(self, message_data: Dict[str, Any]):
        """WebSocket 전송"""

        if message_data.get("type") == "pushup_feedback":
            data = message_data.get("data", {})
            socket_session = await self.socket_service.get_socket_session(self.socket_session_id)

            if data.get("rep_detected", False):
                await self.workout_service.complete_rep(socket_session.session_id, 1)

                updated_session = await self.workout_service.get_workout_session(
                    socket_session.session_id, socket_session.user_id
                )

                set_completed = self._check_set_completed(updated_session)

                workout_completed = self._check_workout_completed(updated_session)

                if workout_completed:
                    # 전체 운동 완료 - 세션 종료
                    await self._handle_workout_completion(socket_session)
                    return

                response_data = {
                    "type": "rep_success",
                    "data": {
                        "rep_detected": True,
                        "failed_detected": False,
                        "set_completed": set_completed,
                        "workout_completed": False,
                        "feedback_message": f"{updated_session.current_set - 1}세트 완료! {updated_session.level.rest_seconds} 초 동안 휴식하세요"
                        if set_completed
                        else f"{updated_session.total_reps_completed}개 완료",
                        "session": updated_session.model_dump(mode="json"),
                    },
                }

            elif data.get("failed_detected", False):
                await self.workout_service.complete_failed_rep(socket_session.session_id, 1)

                updated_session = await self.workout_service.get_workout_session(
                    socket_session.session_id, socket_session.user_id
                )

                response_data = {
                    "type": "rep_success",
                    "data": {
                        "rep_detected": False,
                        "failed_detected": True,
                        "set_completed": False,
                        "workout_completed": False,
                        "feedback_message": data.get("feedback_message", "다시 시도하세요"),
                        "session": updated_session.model_dump(mode="json"),
                    },
                }
            else:
                return

        elif message_data.get("type") == "squat_feedback":
            data = message_data.get("data", {})
            socket_session = await self.socket_service.get_socket_session(self.socket_session_id)

            if data.get("rep_detected", False):
                await self.workout_service.complete_rep(socket_session.session_id, 1)

                updated_session = await self.workout_service.get_workout_session(
                    socket_session.session_id, socket_session.user_id
                )

                set_completed = self._check_set_completed(updated_session)
                workout_completed = self._check_workout_completed(updated_session)

                if workout_completed:
                    await self._handle_workout_completion(socket_session)
                    return

                response_data = {
                    "type": "rep_success",
                    "data": {
                        "rep_detected": True,
                        "failed_detected": False,
                        "set_completed": set_completed,
                        "workout_completed": False,
                        "feedback_message": f"{updated_session.current_set - 1}세트 완료! {updated_session.level.rest_seconds} 초 동안 휴식하세요"
                        if set_completed
                        else f"{updated_session.total_reps_completed}개 완료",
                        "session": updated_session.model_dump(mode="json"),
                    },
                }
            else:
                return

        else:
            return

        await self.websocket.send_json(response_data)

    def _check_set_completed(self, session) -> bool:
        """세트 완료 여부 확인 - current_set_reps가 0이고 이전에 반복이 있었다면 세트 완료"""
        return session.current_set_reps == 0 and session.total_reps_completed > 0

    def _check_workout_completed(self, session) -> bool:
        """전체 운동 완료 여부 확인"""
        if hasattr(session, "level") and session.level:
            return session.current_set > session.level.target_sets
        return False

    async def _handle_workout_completion(self, socket_session):
        """운동 완료"""
        try:
            # 총 칼로리 계산 및 저장
            updated_session = await self.workout_service.get_workout_session(
                socket_session.session_id, socket_session.user_id
            )

            total_calories = updated_session.total_reps_completed * updated_session.exercise.calorie
            await self.workout_service.update_total_calories(socket_session.session_id, total_calories)

            # 운동 세션 완료 처리
            result = await self.workout_service.complete_workout(socket_session.session_id)

            completion_message = {"type": "workout_completed", "data": {}}

            await self.websocket.send_json(completion_message)

            # 연결 상태 업데이트 후 종료
            await self.socket_service.update_connection_status(socket_session.socket_session_id, "disconnected")
            await self.websocket.close()

        except Exception as e:
            print(f"Workout completion error: {e}")
            try:
                await self.websocket.close()
            except:
                pass

    def update_position(self, *args):
        """카운터에 포지션 정보 전달"""
        if self.exercise_type == "푸쉬업":
            position, down, up, mid = args[:4]
            self.counter.position.put((position, down, up, mid))
        elif self.exercise_type == "스쿼트":
            position, confidence = args[:2]
            self.counter.position.put((position, confidence))

    def cleanup(self):
        """카운터 스레드 정리"""
        self.counter.stop()


class PoseAnalyzer:
    """미디어파이프 좌표 기반 포즈 분석 서비스"""

    def __init__(self):
        self.models = {}
        self.session_counters = {}
        self.load_models()

    def load_models(self):
        """TFLite 모델들 로드"""
        # 푸쉬업 모델 로드
        pushup_model_path = Path("models/tf_lite_model/pushup_classifier.tflite")
        self.models["pushup"] = tf.lite.Interpreter(model_path=str(pushup_model_path))
        self.models["pushup"].allocate_tensors()

        # 스쿼트 모델 로드
        squat_model_path = Path("models/tf_lite_model/squat_classifier_v2.tflite")
        self.models["squat"] = tf.lite.Interpreter(model_path=str(squat_model_path))
        self.models["squat"].allocate_tensors()

    def _safe_float_conversion(self, value) -> float:
        """안전한 float 변환"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, np.ndarray):
            return float(value.item() if value.size == 1 else value.flat[0])
        else:
            return float(str(value))

    async def analyze_pose(self, landmarks: List[List[float]], exercise_type: str, session_id: int) -> Dict[str, Any]:
        """포즈 분석 메인 메서드"""
        if exercise_type == "푸시업":
            return await self._analyze_pushup(landmarks, session_id)
        elif exercise_type == "스쿼트":
            return await self._analyze_squat(landmarks, session_id)

    async def _analyze_pushup(self, landmarks: List[List[float]], session_id: int) -> Dict[str, Any]:
        """푸쉬업 포즈 분석"""

        # 세션별 카운터 초기화
        if session_id not in self.session_counters:
            self.session_counters[session_id] = SessionCounter(session_id, "푸쉬업")

        counter = self.session_counters[session_id]

        # MediaPipe 랜드마크 → (1,63) float32 벡터 변환
        input_data = preprocess_pushup(landmarks)

        # TFLite 추론
        interpreter = self.models["pushup"]
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]["index"])

        # 확률 추출
        probs = output_data[0] if len(output_data.shape) > 1 else output_data
        down = self._safe_float_conversion(probs[0])
        up = self._safe_float_conversion(probs[1])
        mid = self._safe_float_conversion(probs[2])

        # 클래스별 확률 처리
        prob_list = [down, up, mid]
        position_idx = int(np.argmax(prob_list))
        confidence = prob_list[position_idx]
        position_labels = ["down", "up", "mid"]
        position = position_labels[position_idx]

        # PushupCounter에 포지션 정보 전달
        counter.update_position(position_idx, down, up, mid)

        return {
            "position": position,
            "confidence": round(confidence, 3),
            "probabilities": {
                "down": round(down, 3),
                "up": round(up, 3),
                "mid": round(mid, 3),
            },
        }

    async def _analyze_squat(self, landmarks: List[List[float]], session_id: int) -> Dict[str, Any]:
        """스쿼트 포즈 분석"""
        # 세션별 카운터 초기화
        if session_id not in self.session_counters:
            self.session_counters[session_id] = SessionCounter(session_id, "스쿼트")

        counter = self.session_counters[session_id]

        # 스쿼트 모델 추론
        input_data = preprocess_squat(landmarks)

        interpreter = self.models["squat"]
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]["index"])

        # 확률 추출
        probs = output_data[0] if len(output_data.shape) > 1 else output_data
        down_prob = self._safe_float_conversion(probs[0])
        up_prob = self._safe_float_conversion(probs[1])

        position_idx = 1 if up_prob > down_prob else 0
        confidence = up_prob if position_idx == 1 else down_prob
        position = "up" if position_idx == 1 else "down"

        # SquatCounter에 포지션 정보 전달
        counter.update_position(position_idx, confidence)

        return {
            "position": position,
            "confidence": round(confidence, 3),
        }

    def cleanup_session(self, session_id: int):
        """세션 종료 시 카운터 정리"""
        if session_id in self.session_counters:
            self.session_counters[session_id].cleanup()
            del self.session_counters[session_id]
