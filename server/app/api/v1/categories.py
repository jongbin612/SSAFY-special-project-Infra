# app/api/v1/categories.py

from typing import List

from app.core.database import get_db
from app.schemas.exercise import ExerciseCategoryBase
from app.services.category_service import CategoryService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/",
    response_model=List[ExerciseCategoryBase],
    summary="운동 카테고리 목록 조회",
    description="모든 운동 카테고리를 조회합니다.",
)
async def get_categories(db: Session = Depends(get_db)):
    """운동 카테고리 목록 조회"""
    category_service = CategoryService()

    try:
        categories = await category_service.get_all_categories()
        return categories

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"카테고리 목록 조회 실패: {str(e)}"
        )
