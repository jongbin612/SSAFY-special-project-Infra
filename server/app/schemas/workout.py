# app/schemas/workout.py

from datetime import datetime

from pydantic import BaseModel, Field


class WorkoutStartRequest(BaseModel):
    """운동 시작 요청"""

    exercise_id: int = Field(..., description="운동 ID")
    level: int = Field(..., ge=1, le=9999, description="도전할 레벨")


class WorkoutStopRequest(BaseModel):
    """운동 정지 요청"""

    pass


class ManualRepRequest(BaseModel):
    """수동 반복 수정 요청"""

    reps: int = Field(default=1, ge=1, le=50, description="추가/차감할 반복수")


class SocketConnectionInfo(BaseModel):
    """소켓 연결 정보"""

    socket_session_id: str = Field(..., description="소켓 세션 ID")
    websocket_url: str = Field(..., description="WebSocket 연결 URL")
    connection_status: str = Field(..., description="연결 상태")


class ExerciseDetail(BaseModel):
    """운동 상세 정보"""

    exercise_id: int
    name: str
    calorie: float | None = None
    category_id: int
    thumbnail_url: str | None = None
    target_image_url: str | None = None
    howto_image_url: str | None = None

    class Config:
        from_attributes = True


class ExerciseLevelDetail(BaseModel):
    """운동 레벨 상세 정보"""

    level_id: int
    exercise_id: int
    level: int
    target_sets: int
    target_reps: int
    rest_seconds: int
    experience_points: int

    class Config:
        from_attributes = True


class WorkoutSessionDetail(BaseModel):
    """운동 세션 상세 정보"""

    session_id: int
    user_id: int
    exercise_id: int
    level_id: int
    status: str
    current_set: int
    current_set_reps: int
    total_reps_completed: int
    total_reps_failed: int = 0
    total_calories_burned: float
    duration_seconds: float

    # 타이머 관련 필드
    start_time: datetime | None = None
    end_time: datetime | None = None
    last_pause_time: datetime | None = None
    total_pause_duration: float = 0.0

    # 관련 객체들
    exercise: ExerciseDetail | None = None
    level: ExerciseLevelDetail | None = None

    class Config:
        from_attributes = True


class WorkoutStartResponse(BaseModel):
    """운동 시작 응답"""

    message: str = Field(..., description="응답 메시지")
    session_id: int = Field(..., description="생성된 운동 세션 ID")


class WorkoutSessionResponse(BaseModel):
    """운동 세션 조회 응답"""

    message: str = Field(..., description="응답 메시지")
    session: WorkoutSessionDetail = Field(..., description="운동 세션 상세 정보")
    socket_info: SocketConnectionInfo = Field(..., description="소켓 연결 정보")
