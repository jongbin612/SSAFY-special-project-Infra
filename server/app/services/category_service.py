# app/services/category_service.py

from typing import List

from app.core.database import get_db
from app.models.exercise_category import ExerciseCategoryModel
from app.schemas.exercise import ExerciseCategoryBase


class CategoryService:
    """카테고리 관련 서비스"""

    def __init__(self):
        self.db = next(get_db())

    async def get_all_categories(self) -> List[ExerciseCategoryBase]:
        """모든 카테고리 조회"""

        categories = self.db.query(ExerciseCategoryModel).order_by(ExerciseCategoryModel.name).all()

        return [ExerciseCategoryBase.from_orm(category) for category in categories]
