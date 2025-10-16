# app/services/workout_service.py

from datetime import datetime

from app.core.database import get_db
from app.models.exercise_level import ExerciseLevelModel
from app.models.user_exercise import UserExerciseModel
from app.models.workout_session import WorkoutSessionModel
from app.schemas.workout import WorkoutSessionDetail
from sqlalchemy import and_
from sqlalchemy.orm import joinedload


class WorkoutService:
    """운동 세션 관리 서비스"""

    def __init__(self):
        self.db = next(get_db())

    async def get_exercise_level(self, exercise_id: int, level: int) -> ExerciseLevelModel | None:
        """운동 레벨 정보 조회"""
        return (
            self.db.query(ExerciseLevelModel)
            .options(joinedload(ExerciseLevelModel.exercise))
            .filter(
                and_(
                    ExerciseLevelModel.exercise_id == exercise_id,
                    ExerciseLevelModel.level == level,
                )
            )
            .first()
        )

    async def get_user_exercise(self, user_id: int, exercise_id: int) -> UserExerciseModel | None:
        """사용자 운동 정보 조회"""
        return (
            self.db.query(UserExerciseModel)
            .filter(
                and_(
                    UserExerciseModel.user_id == user_id,
                    UserExerciseModel.exercise_id == exercise_id,
                )
            )
            .first()
        )

    async def get_active_session(self, user_id: int) -> WorkoutSessionModel | None:
        """사용자의 활성 운동 세션 조회"""
        return (
            self.db.query(WorkoutSessionModel)
            .filter(
                and_(
                    WorkoutSessionModel.user_id == user_id,
                    WorkoutSessionModel.status.in_(["active", "paused"]),
                )
            )
            .first()
        )

    async def create_workout_session(self, user_id: int, exercise_id: int, level_id: int) -> WorkoutSessionModel:
        """새로운 운동 세션 생성"""
        exercise_level = self.db.query(ExerciseLevelModel).filter(ExerciseLevelModel.level_id == level_id).first()

        if not exercise_level:
            raise ValueError("Invalid exercise level")

        current_time = datetime.utcnow()

        workout_session = WorkoutSessionModel(
            user_id=user_id,
            exercise_id=exercise_id,
            level_id=level_id,
            status="active",
            current_set=1,
            current_set_reps=0,
            total_reps_completed=0,
            total_reps_failed=0,
            total_calories_burned=0.0,
            start_time=current_time,
            total_pause_duration=0.0,
            duration_seconds=0.0,
        )

        self.db.add(workout_session)
        self.db.commit()
        self.db.refresh(workout_session)

        return workout_session

    async def get_workout_session(self, session_id: int, user_id: int) -> WorkoutSessionDetail | None:
        """운동 세션 상세 조회"""
        session = (
            self.db.query(WorkoutSessionModel)
            .options(
                joinedload(WorkoutSessionModel.exercise),
                joinedload(WorkoutSessionModel.level),
            )
            .filter(
                and_(
                    WorkoutSessionModel.session_id == session_id,
                    WorkoutSessionModel.user_id == user_id,
                )
            )
            .first()
        )

        if not session:
            return None

        return WorkoutSessionDetail.from_orm(session)

    async def get_session_status(self, session_id: int) -> dict:
        """세션 상태 및 실시간 정보 조회"""
        session = self.db.query(WorkoutSessionModel).filter(WorkoutSessionModel.session_id == session_id).first()

        if not session:
            raise ValueError("Session not found")

        current_duration = session.get_current_duration()

        return {
            "session_id": session.session_id,
            "status": session.status,
            "current_set": session.current_set,
            "current_set_reps": session.current_set_reps,
            "total_reps_completed": session.total_reps_completed,
            "total_calories_burned": session.total_calories_burned,
            "duration_seconds": current_duration,
            "duration_minutes": round(current_duration / 60, 2),
            "start_time": session.start_time.isoformat(),
            "is_paused": session.status == "paused",
        }

    async def complete_failed_rep(self, session_id: int, failed_reps: int = 1) -> WorkoutSessionModel:
        """실패한 반복 처리"""
        session = (
            self.db.query(WorkoutSessionModel)
            .options(joinedload(WorkoutSessionModel.exercise), joinedload(WorkoutSessionModel.level))
            .filter(WorkoutSessionModel.session_id == session_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        # 실패 카운트만 증가
        session.total_reps_failed += failed_reps
        session.duration_seconds = session.get_current_duration()
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    async def complete_rep(self, session_id: int, reps: int = 1) -> WorkoutSessionModel:
        """반복 완료 처리"""
        session = (
            self.db.query(WorkoutSessionModel)
            .options(joinedload(WorkoutSessionModel.exercise), joinedload(WorkoutSessionModel.level))
            .filter(WorkoutSessionModel.session_id == session_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        prev_set = session.current_set

        # 현재 세트 반복수 및 총 반복수 증가
        session.current_set_reps += reps
        session.total_reps_completed += reps

        # 목표 반복수 달성 시 자동 세트 증가
        target_reps = session.level.target_reps
        if session.current_set_reps >= target_reps:
            session.current_set += 1
            session.current_set_reps = 0  # 현재 세트 반복수 초기화
            print(f"Set {prev_set} completed! Moving to set {session.current_set}")

        # 실시간 운동 시간 업데이트
        session.duration_seconds = session.get_current_duration()
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    async def manual_add_rep(self, session_id: int, reps: int = 1) -> WorkoutSessionModel:
        """수동 반복 추가"""
        return await self.complete_rep(session_id, reps)

    async def manual_subtract_rep(self, session_id: int, reps: int = 1) -> WorkoutSessionModel:
        """수동 반복 차감"""
        session = (
            self.db.query(WorkoutSessionModel)
            .options(
                joinedload(WorkoutSessionModel.exercise),
                joinedload(WorkoutSessionModel.level),
            )
            .filter(WorkoutSessionModel.session_id == session_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        # 반복수 차감 (0 이하로는 내려가지 않음)
        session.current_set_reps = max(0, session.current_set_reps - reps)
        session.total_reps_completed = max(0, session.total_reps_completed - reps)

        session.duration_seconds = session.get_current_duration()
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    async def pause_workout(self, session_id: int) -> WorkoutSessionModel:
        """운동 일시정지"""
        session = self.db.query(WorkoutSessionModel).filter(WorkoutSessionModel.session_id == session_id).first()

        if not session:
            raise ValueError("Session not found")

        if session.status != "active":
            raise ValueError(f"Cannot pause workout in {session.status} status")

        current_time = datetime.utcnow()

        # 일시정지 시점 기록
        session.status = "paused"
        session.last_pause_time = current_time
        session.duration_seconds = session.get_current_duration()  # 현재까지의 운동 시간 저장
        session.updated_at = current_time

        self.db.commit()
        self.db.refresh(session)

        return session

    async def resume_workout(self, session_id: int) -> WorkoutSessionModel:
        """운동 재개"""
        session = self.db.query(WorkoutSessionModel).filter(WorkoutSessionModel.session_id == session_id).first()

        if not session:
            raise ValueError("Session not found")

        if session.status != "paused":
            raise ValueError(f"Cannot resume workout in {session.status} status")

        current_time = datetime.utcnow()

        # 일시정지 시간 계산 및 누적
        if session.last_pause_time:
            pause_duration = (current_time - session.last_pause_time).total_seconds()
            session.total_pause_duration += pause_duration

        # 운동 재개
        session.status = "active"
        session.last_pause_time = None
        session.updated_at = current_time

        self.db.commit()
        self.db.refresh(session)

        return session

    async def update_total_calories(self, session_id: int, total_calories: float) -> WorkoutSessionModel:
        """총 칼로리 업데이트"""
        session = self.db.query(WorkoutSessionModel).filter(WorkoutSessionModel.session_id == session_id).first()

        if not session:
            raise ValueError("Session not found")

        session.total_calories_burned = total_calories
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    async def complete_workout(self, session_id: int) -> dict:
        """운동 완료 처리"""
        session = (
            self.db.query(WorkoutSessionModel)
            .options(joinedload(WorkoutSessionModel.level))
            .filter(WorkoutSessionModel.session_id == session_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        current_time = datetime.utcnow()

        # 일시정지 중이었다면 마지막 일시정지 시간도 누적
        if session.status == "paused" and session.last_pause_time:
            final_pause_duration = (current_time - session.last_pause_time).total_seconds()
            session.total_pause_duration += final_pause_duration

        # 최종 운동 시간 계산
        final_duration = session.get_current_duration()

        # 세션 완료 처리 - status = "completed"
        session.status = "completed"
        session.end_time = current_time
        session.duration_seconds = final_duration
        session.last_pause_time = None
        session.updated_at = current_time

        # 경험치 계산
        experience_gained = session.level.experience_points if session.level else 0

        # 사용자 운동 통계 업데이트
        await self._update_user_exercise_stats(
            session.user_id,
            session.exercise_id,
            session.level.level,
            session.total_reps_completed,
            final_duration,
            experience_gained,
        )

        self.db.commit()

        return {
            "total_reps_completed": session.total_reps_completed,
            "total_calories_burned": session.total_calories_burned,
            "duration_seconds": final_duration,
            "duration_minutes": round(final_duration / 60, 2),
            "experience_gained": experience_gained,
        }

    async def _update_user_exercise_stats(
        self,
        user_id: int,
        exercise_id: int,
        completed_level: int,
        total_reps: int,
        duration_seconds: float,
        experience_points: int,
    ):
        """사용자 운동 통계 업데이트"""
        user_exercise = await self.get_user_exercise(user_id, exercise_id)

        if user_exercise:
            user_exercise.total_sessions += 1
            user_exercise.total_reps_completed += total_reps
            user_exercise.total_time_exercised += int(duration_seconds)
            user_exercise.total_experience_points += experience_points
            user_exercise.last_performed = datetime.utcnow()

            if completed_level > user_exercise.highest_completed_level:
                user_exercise.highest_completed_level = completed_level
                if user_exercise.current_level <= completed_level:
                    user_exercise.current_level = completed_level + 1

            user_exercise.updated_at = datetime.utcnow()
        else:
            user_exercise = UserExerciseModel(
                user_id=user_id,
                exercise_id=exercise_id,
                current_level=2,
                highest_completed_level=completed_level,
                total_sessions=1,
                total_reps_completed=total_reps,
                total_time_exercised=int(duration_seconds),
                total_experience_points=experience_points,
                last_performed=datetime.utcnow(),
            )
            self.db.add(user_exercise)
