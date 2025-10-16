# app/schemas/exercise.py

from typing import List

from pydantic import BaseModel


class ExerciseCategoryBase(BaseModel):
    """운동 카테고리 기본"""

    category_id: int
    name: str

    class Config:
        from_attributes = True


class ExerciseLevelList(BaseModel):
    """운동 레벨 목록용"""

    level_id: int
    level: int
    target_sets: int
    target_reps: int
    rest_seconds: int
    experience_points: int
    is_locked: bool | None = None
    is_completed: bool | None = None

    class Config:
        from_attributes = True


class ExerciseList(BaseModel):
    """운동 목록용 스키마"""

    exercise_id: int
    name: str
    calorie: float | None = None
    thumbnail_url: str | None = None
    category: ExerciseCategoryBase

    class Config:
        from_attributes = True


class ExerciseDetail(BaseModel):
    """운동 상세 정보 스키마"""

    exercise_id: int
    name: str
    calorie: float | None = None
    thumbnail_url: str | None = None
    target_image_url: str | None = None
    howto_image_url: str | None = None
    category: ExerciseCategoryBase
    levels: List[ExerciseLevelList] = []

    class Config:
        from_attributes = True
