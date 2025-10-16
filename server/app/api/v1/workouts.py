# app/api/v1/workouts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import User
from app.schemas.workout import SocketConnectionInfo, WorkoutSessionResponse, WorkoutStartRequest, WorkoutStartResponse
from app.services.socket_service import SocketService
from app.services.workout_service import WorkoutService

router = APIRouter()


@router.post(
    "/start",
    response_model=WorkoutStartResponse,
    summary="운동 시작",
    description="새로운 운동 세션과 소켓 세션을 모두 생성하고 세션 ID만 반환합니다.",
)
async def start_workout(
    workout_request: WorkoutStartRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """운동 시작 - 모든 세션 생성 완료"""
    workout_service = WorkoutService()
    socket_service = SocketService()

    try:
        # 기존 활성 세션 확인
        active_session = await workout_service.get_active_session(current_user.user_id)
        if active_session:
            return WorkoutStartResponse(
                message=f"이미 진행 중인 운동 세션이 있습니다. 세션 ID: {active_session.session_id}",
                session_id=active_session.session_id,
            )

        # 운동과 레벨 정보 검증
        exercise_level = await workout_service.get_exercise_level(workout_request.exercise_id, workout_request.level)

        if not exercise_level:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 운동의 레벨을 찾을 수 없습니다")

        # 사용자 운동 권한 확인
        user_exercise = await workout_service.get_user_exercise(current_user.user_id, workout_request.exercise_id)

        # 사용자의 현재 도전 가능한 최대 레벨 계산
        if user_exercise:
            max_available_level = user_exercise.current_level
        else:
            max_available_level = 1

        # 권한 검증
        if workout_request.level > max_available_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"현재 도전 가능한 최대 레벨은 {max_available_level}입니다. 요청한 레벨: {workout_request.level}",
            )

        # 새 운동 세션 생성
        workout_session = await workout_service.create_workout_session(
            user_id=current_user.user_id, exercise_id=workout_request.exercise_id, level_id=exercise_level.level_id
        )

        # 소켓 세션 생성
        socket_session = await socket_service.create_socket_session(
            session_id=workout_session.session_id, user_id=current_user.user_id
        )

        return WorkoutStartResponse(message="운동 세션이 시작되었습니다", session_id=workout_session.session_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"운동 시작 실패: {str(e)}")


@router.get(
    "/{session_id}",
    response_model=WorkoutSessionResponse,
    summary="운동 세션 정보 조회",
    description="세션 ID로 기존 운동 세션 정보와 소켓 정보를 조회합니다.",
)
async def get_workout_session(
    session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """운동 세션 정보 조회"""
    workout_service = WorkoutService()
    socket_service = SocketService()

    try:
        # 1. 운동 세션 조회 및 권한 확인
        workout_detail = await workout_service.get_workout_session(session_id, current_user.user_id)

        if not workout_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="운동 세션을 찾을 수 없거나 접근 권한이 없습니다"
            )

        # 2. 소켓 세션 조회
        socket_session = await socket_service.get_socket_session_by_workout(session_id)

        if not socket_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="소켓 세션을 찾을 수 없습니다. 운동을 다시 시작해주세요."
            )

        # 3. 응답 데이터 구성
        return WorkoutSessionResponse(
            message="운동 세션 정보 조회 성공",
            session=workout_detail,
            socket_info=SocketConnectionInfo(
                socket_session_id=socket_session.socket_session_id,
                websocket_url=f"/ws/workout/{socket_session.socket_session_id}",
                connection_status=socket_session.connection_status,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"운동 세션 조회 실패: {str(e)}")
