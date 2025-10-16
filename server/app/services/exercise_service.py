# app/services/exercise_service.py

from typing import Any, Dict, List

from app.core.database import get_db
from app.models.exercise import ExerciseModel
from app.models.exercise_category import ExerciseCategoryModel
from app.models.exercise_level import ExerciseLevelModel
from app.models.user_exercise import UserExerciseModel
from app.schemas.exercise import ExerciseDetail, ExerciseLevelList, ExerciseList
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload


class ExerciseService:
    """운동 관련 서비스"""

    def __init__(self):
        self.db = next(get_db())

    async def get_exercises(
        self, category_id: int | None = None, search: str | None = None, user_id: int | None = None
    ) -> List[ExerciseList]:
        """운동 목록 조회"""

        query = self.db.query(ExerciseModel).options(joinedload(ExerciseModel.category))

        filters = []

        if category_id:
            filters.append(ExerciseModel.category_id == category_id)

        if search:
            filters.append(
                or_(
                    ExerciseModel.name.ilike(f"%{search}%"),
                    ExerciseModel.category.has(ExerciseCategoryModel.name.ilike(f"%{search}%")),
                )
            )

        if filters:
            query = query.filter(and_(*filters))

        exercises = query.order_by(ExerciseModel.name).all()

        exercises_list = []
        for exercise in exercises:
            exercise_data = ExerciseList.from_orm(exercise)
            exercises_list.append(exercise_data)

        return exercises_list

    async def get_exercise_detail(self, exercise_id: int, user_id: int) -> ExerciseDetail | None:
        """운동 상세 정보 조회"""

        exercise = (
            self.db.query(ExerciseModel)
            .options(joinedload(ExerciseModel.category), joinedload(ExerciseModel.levels))
            .filter(ExerciseModel.exercise_id == exercise_id)
            .first()
        )

        if not exercise:
            return None

        exercise_detail = ExerciseDetail.from_orm(exercise)

        # 레벨 정보 정렬 및 잠금/완료 상태 설정
        sorted_levels = sorted(exercise.levels, key=lambda x: x.level)

        # 사용자 진행도 조회
        user_progress = await self._get_user_exercise_progress(user_id, exercise_id)

        # 각 레벨의 잠금/완료 상태 설정
        levels_with_status = []
        for level in sorted_levels:
            level_data = ExerciseLevelList.from_orm(level)

            current_level = user_progress.get("current_level", 1)
            highest_completed = user_progress.get("highest_completed_level", 0)

            level_data.is_locked = level.level > current_level
            level_data.is_completed = level.level <= highest_completed

            levels_with_status.append(level_data)

        exercise_detail.levels = levels_with_status

        return exercise_detail

    async def get_exercise_levels(self, exercise_id: int, user_id: int) -> List[ExerciseLevelList]:
        """운동 레벨 목록 조회"""

        levels = (
            self.db.query(ExerciseLevelModel)
            .filter(ExerciseLevelModel.exercise_id == exercise_id)
            .order_by(ExerciseLevelModel.level)
            .all()
        )

        if not levels:
            return []

        # 사용자 진행도 조회
        user_progress = await self._get_user_exercise_progress(user_id, exercise_id)

        # 레벨별 잠금/완료 상태 설정
        levels_with_status = []
        for level in levels:
            level_data = ExerciseLevelList.from_orm(level)

            current_level = user_progress.get("current_level", 1)
            highest_completed = user_progress.get("highest_completed_level", 0)

            level_data.is_locked = level.level > current_level
            level_data.is_completed = level.level <= highest_completed

            levels_with_status.append(level_data)

        return levels_with_status

    async def _get_user_exercise_progress(self, user_id: int, exercise_id: int) -> Dict[str, Any]:
        """사용자의 운동 진행도 조회"""

        user_exercise = (
            self.db.query(UserExerciseModel)
            .filter(and_(UserExerciseModel.user_id == user_id, UserExerciseModel.exercise_id == exercise_id))
            .first()
        )

        if not user_exercise:
            return {
                "current_level": 1,  # 처음 시작하는 사용자는 레벨 1부터
                "highest_completed_level": 0,  # 아직 완료한 레벨 없음
                "total_sessions": 0,
                "total_reps": 0,
                "total_time": 0,
                "total_exp": 0,
                "last_performed": None,
            }

        return {
            "current_level": user_exercise.current_level,
            "highest_completed_level": user_exercise.highest_completed_level,
            "total_sessions": user_exercise.total_sessions,
            "total_reps": user_exercise.total_reps_completed,
            "total_time": user_exercise.total_time_exercised,
            "total_exp": user_exercise.total_experience_points,
            "last_performed": user_exercise.last_performed,
        }

    async def get_exercise_by_id(self, exercise_id: int) -> ExerciseList | None:
        """운동 ID로 운동 정보 조회"""

        exercise = (
            self.db.query(ExerciseModel)
            .options(joinedload(ExerciseModel.category))
            .filter(ExerciseModel.exercise_id == exercise_id)
            .first()
        )

        if not exercise:
            return None

        return ExerciseList.model_validate(exercise)
