# app/schemas/home.py

from typing import List

from app.schemas.exercise import ExerciseList
from pydantic import BaseModel, Field


class HomePageResponse(BaseModel):
    """메인페이지 응답 스키마"""

    recent: List[ExerciseList] = Field(..., description="최근 운동 3개")
    hot: List[ExerciseList] = Field(..., description="인기 운동 목록")
