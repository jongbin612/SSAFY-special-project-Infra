# app/services/home_service.py

from typing import List

from app.core.database import get_db
from app.models.exercise import ExerciseModel
from app.models.user_exercise import UserExerciseModel
from app.schemas.exercise import ExerciseList
from app.schemas.home import HomePageResponse
from sqlalchemy import desc, func


class HomeService:
    """메인페이지 관련 서비스"""

    def __init__(self):
        self.db = next(get_db())

    async def get_home_page_data(self, user_id: int) -> HomePageResponse:
        """메인페이지 데이터 조회"""

        recent_exercises = await self._get_recent_exercises(user_id)
        hot_exercises = await self._get_hot_exercises()

        return HomePageResponse(recent=recent_exercises, hot=hot_exercises)

    async def _get_recent_exercises(self, user_id: int) -> List[ExerciseList]:
        """최근 운동 3개 조회"""

        # N+1 문제를 피하기 위해 두 단계로 분리
        recent_user_exercises = (
            self.db.query(UserExerciseModel)
            .filter(UserExerciseModel.user_id == user_id, UserExerciseModel.last_performed.is_not(None))
            .order_by(desc(UserExerciseModel.last_performed))
            .limit(3)
            .all()
        )

        if not recent_user_exercises:
            return []

        # 운동 ID 리스트 추출
        exercise_ids = [ue.exercise_id for ue in recent_user_exercises]

        # 운동 정보와 카테고리를 한번에 로드
        exercises_data = (
            self.db.query(ExerciseModel)
            .join(ExerciseModel.category)  # 일반 join 사용
            .filter(ExerciseModel.exercise_id.in_(exercise_ids))
            .all()
        )

        # 순서 유지를 위한 딕셔너리
        exercise_dict = {ex.exercise_id: ex for ex in exercises_data}

        recent_exercises = []
        for user_exercise in recent_user_exercises:
            if user_exercise.exercise_id in exercise_dict:
                exercise = exercise_dict[user_exercise.exercise_id]
                exercise_list = ExerciseList.from_orm(exercise)
                recent_exercises.append(exercise_list)

        return recent_exercises

    async def _get_hot_exercises(self) -> List[ExerciseList]:
        """인기 운동 조회"""

        # 서브쿼리로 운동별 사용자 수 계산
        user_count_subquery = (
            self.db.query(
                UserExerciseModel.exercise_id, func.count(UserExerciseModel.user_exercise_id).label("user_count")
            )
            .group_by(UserExerciseModel.exercise_id)
            .subquery()
        )

        # 인기 운동 ID 조회 (정렬된 순서)
        hot_exercise_ids = (
            self.db.query(ExerciseModel.exercise_id)
            .outerjoin(user_count_subquery, ExerciseModel.exercise_id == user_count_subquery.c.exercise_id)
            .order_by(desc(func.coalesce(user_count_subquery.c.user_count, 0)), ExerciseModel.name)
            .limit(6)
            .all()
        )

        if not hot_exercise_ids:
            return []

        exercise_ids = [row.exercise_id for row in hot_exercise_ids]

        # 운동 정보와 카테고리 로드
        hot_exercises_data = (
            self.db.query(ExerciseModel)
            .join(ExerciseModel.category)
            .filter(ExerciseModel.exercise_id.in_(exercise_ids))
            .all()
        )

        # 정렬 순서 유지
        exercise_dict = {ex.exercise_id: ex for ex in hot_exercises_data}
        hot_exercises = []
        for exercise_id in exercise_ids:
            if exercise_id in exercise_dict:
                exercise_list = ExerciseList.from_orm(exercise_dict[exercise_id])
                hot_exercises.append(exercise_list)

        return hot_exercises
