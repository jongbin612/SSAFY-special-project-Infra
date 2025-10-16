# utils/counters/squat_counter.py

import queue
import threading
import time
from datetime import datetime
from typing import Any, Dict


class SquatCounter(threading.Thread):
    def __init__(self, threshold=0.7, callback=None):
        super().__init__()
        self.daemon = True
        self.squat_count = 0  # 성공한 스쿼트 카운트
        self.failed_count = 0  # 실패 카운트

        # 메인 스레드에서 (pos, confidence) 형태로 예측 결과를 큐에 넣어줌
        self.position = queue.Queue()

        # 스레드 종료를 제어하기 위한 이벤트
        self._stop_event = threading.Event()

        # 신뢰도(확률) 임계값
        self.threshold = threshold

        # 메시지 콜백 함수 (웹소켓으로 메시지 전송용)
        self.message_callback = callback

    def run(self):
        """
        별도의 스레드로 실행되며, 큐에 들어오는 (자세/확률) 정보를 기반으로
        상태를 전환하고 스쿼트 개수를 세는 핵심 로직
        """
        prev_pos = 1  # 이전 포지션 (1=up, 0=down)
        cur_pos = 1  # 현재 포지션

        while not self._stop_event.is_set():
            # 새로운 입력이 없으면 잠시 대기
            if self.position.empty():
                time.sleep(0.05)
                continue

            try:
                # 메인에서 넣어준 값 꺼내오기
                # pos: 예측된 현재 자세 (0=down, 1=up)
                # confidence: 해당 자세의 신뢰도
                cur_pos, confidence = self.position.get(timeout=1)

                # 상태 전환 및 카운팅 로직
                message_data = self._process_state_transition(prev_pos, cur_pos, confidence)

                # 메시지가 있고 콜백이 설정되어 있으면 전송
                if message_data and self.message_callback:
                    print(f"📤 Sending callback to WebSocket: {message_data.get('type')}")
                    self.message_callback(message_data)

                prev_pos = cur_pos

            except Exception as e:
                # 큐에서 꺼내는 중 오류 발생 시 무시하고 루프 지속
                print(f"SquatCounter error: {e}")
                continue

    def _process_state_transition(self, prev_pos: int, cur_pos: int, confidence: float) -> Dict[str, Any] | None:
        """상태 전환 처리 및 성공 카운팅 (원본 로직과 동일)"""

        rep_detected = False
        feedback_message = ""

        # up(1) -> down(0) -> up(1) = 성공
        if prev_pos == 1 and cur_pos == 0 and confidence >= self.threshold:
            # up -> down (내려가는 중)
            print("UP → DOWN")

        elif prev_pos == 0 and cur_pos == 1 and confidence >= self.threshold:
            # down -> up (완전한 스쿼트 완성)
            self.squat_count += 1
            rep_detected = True
            feedback_message = "성공!"
            print(f"Squat count: {self.squat_count}")

        # 성공 시에만 메시지 전송 (실패 처리 없음)
        if rep_detected:
            print(f"🎯 Event detected: success={rep_detected}")
            return {
                "type": "squat_feedback",
                "data": {
                    "rep_detected": rep_detected,
                    "failed_detected": False,
                    "squat_count": self.squat_count,
                    "failed_count": self.failed_count,
                    "feedback_message": feedback_message,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        return None

    def get_current_state(self) -> Dict[str, Any]:
        """현재 상태 정보 반환"""
        return {
            "count": self.squat_count,
            "failed_count": self.failed_count,
            "threshold": self.threshold,
        }

    def reset_count(self):
        """카운트 초기화"""
        self.squat_count = 0
        self.failed_count = 0

    def stop(self):
        """
        외부에서 호출 시 스레드를 안전하게 종료할 수 있도록 플래그 설정
        """
        self._stop_event.set()
