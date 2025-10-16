# utils/counters/pushup_counter.py

import queue
import threading
import time
from datetime import datetime
from typing import Any, Dict


class PushupCounter(threading.Thread):
    def __init__(self, threshold=0.7, callback=None):
        super().__init__()
        self.daemon = True
        self.pushup_count = 0  # 성공한 푸쉬업 카운트
        self.failed_count = 0  # 실패한 푸쉬업 카운트

        # 메인 스레드에서 (pos, prob_down, prob_up, prob_mid) 형태로
        # 예측 결과를 큐에 넣어주면 여기서 소비(consume)함
        self.position = queue.Queue()

        # 스레드 종료를 제어하기 위한 이벤트
        self._stop_event = threading.Event()

        # 신뢰도(확률) 임계값 → 이 값 이상일 때만 자세로 인정
        self.threshold = threshold

        # 시작 상태를 "up"(팔을 펴고 있는 상태)으로 가정
        self.state = "up"

        # 메시지 콜백 함수 (웹소켓으로 메시지 전송용)
        self.message_callback = callback

    def run(self):
        """
        별도의 스레드로 실행되며, 큐에 들어오는 (자세/확률) 정보를 기반으로
        상태를 전환하고 push-up 개수를 세는 핵심 로직
        """
        while not self._stop_event.is_set():
            # 새로운 입력이 없으면 잠시 대기
            if self.position.empty():
                time.sleep(0.05)
                continue

            try:
                # 메인에서 넣어준 값 꺼내오기
                # pos: 예측된 현재 자세 (0=down, 1=up, 2=mid)
                # prob_down, prob_up, prob_mid: 각 자세의 신뢰도
                pos, prob_down, prob_up, prob_mid = self.position.get(timeout=1)

                # 상태 전환 및 카운팅 로직 (콜백 포함)
                message_data = self._process_state_transition(pos, prob_down, prob_up, prob_mid)

                # 메시지가 있고 콜백이 설정되어 있으면 전송
                if message_data and self.message_callback:
                    print(f"📤 Sending callback to WebSocket: {message_data.get('type')}")
                    self.message_callback(message_data)

            except Exception as e:
                # 큐에서 꺼내는 중 오류 발생 시 무시하고 루프 지속
                print(f"PushupCounter error: {e}")
                continue

    def _process_state_transition(
        self, pos: int, prob_down: float, prob_up: float, prob_mid: float
    ) -> Dict[str, Any] | None:
        """상태 전환 처리 및 성공/실패 카운팅"""

        rep_detected = False
        failed_detected = False
        feedback_message = ""

        # 원본과 동일한 상태 전환(State Machine) 로직
        if self.state == "up":
            # UP → DOWN 으로 전환 (down 신뢰도가 높을 때)
            if pos == 0 and prob_down >= self.threshold:
                self.state = "down"
                print("UP → DOWN")
            # UP → MID (mid 신뢰도가 높을 때)
            elif pos == 2 and prob_mid >= self.threshold:
                self.state = "mid_from_up"
                print("UP → MID_FROM_UP")

        elif self.state == "down":
            # DOWN → UP 전환 = 한 번의 푸쉬업 성공
            if pos == 1 and prob_up >= self.threshold:
                self.pushup_count += 1
                rep_detected = True
                feedback_message = "성공!"
                self.state = "up"
                print(f"Push-up count: {self.pushup_count}")
            # DOWN → MID (중간 상태를 거친 경우)
            elif pos == 2 and prob_mid >= self.threshold:
                self.state = "mid_from_down"
                print("DOWN → MID_FROM_DOWN")

        elif self.state == "mid_from_up":
            # MID 이후 DOWN → 정상적인 동작 (정상 흐름: UP → MID → DOWN)
            if pos == 0 and prob_down >= self.threshold:
                self.state = "down"
                print("MID_FROM_UP → DOWN")
            # MID 이후 바로 UP → 깔짝 동작 (실패로 처리)
            elif pos == 1 and prob_up >= self.threshold:
                self.failed_count += 1
                failed_detected = True
                feedback_message = "더 깊게 내려가세요!"
                self.state = "up"
                print(f"Push-up failed (more down): {self.failed_count}")

        elif self.state == "mid_from_down":
            # MID 이후 UP → 정상적인 푸쉬업 완성 (정상 흐름: DOWN → MID → UP)
            if pos == 1 and prob_up >= self.threshold:
                self.pushup_count += 1
                rep_detected = True
                feedback_message = "성공!"
                self.state = "up"
                print(f"Push-up count: {self.pushup_count}")
            # MID 이후 바로 DOWN → 깔짝 동작 (실패로 처리)
            elif pos == 0 and prob_down >= self.threshold:
                self.failed_count += 1
                failed_detected = True
                feedback_message = "끝까지 올라가세요!"
                self.state = "down"
                print(f"Push-up failed (more up): {self.failed_count}")

        prev_state = self.state

        if prev_state != self.state or rep_detected or failed_detected:
            print(
                f"🎯 State: {prev_state}→{self.state} | Success:{self.pushup_count} Fail:{self.failed_count} | Event: {rep_detected or failed_detected}"
            )

        # 성공 또는 실패 시에만 메시지 전송
        if rep_detected or failed_detected:
            print(f"🎯 Event detected: success={rep_detected}, failed={failed_detected}")
            return {
                "type": "pushup_feedback",
                "data": {
                    "rep_detected": rep_detected,
                    "failed_detected": failed_detected,
                    "pushup_count": self.pushup_count,
                    "failed_count": self.failed_count,
                    "feedback_message": feedback_message,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        return None

    def get_current_state(self) -> Dict[str, Any]:
        """현재 상태 정보 반환"""
        return {
            "state": self.state,
            "count": self.pushup_count,
            "failed_count": self.failed_count,
            "threshold": self.threshold,
        }

    def reset_count(self):
        """카운트 초기화"""
        self.pushup_count = 0
        self.failed_count = 0
        self.state = "up"

    def stop(self):
        """
        외부에서 호출 시 스레드를 안전하게 종료할 수 있도록 플래그 설정
        """
        self._stop_event.set()
