# app/api/v1/exercises.py

from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user  # get_optional_current_user 대신 사용
from app.schemas.exercise import ExerciseDetail, ExerciseLevelList, ExerciseList
from app.schemas.user import User
from app.services.exercise_service import ExerciseService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/",
    response_model=List[ExerciseList],
    summary="전체 운동 목록 조회",
    description="모든 운동의 목록을 조회합니다. 카테고리별 필터링이 가능합니다.",
)
async def get_exercises(
    category_id: int | None = Query(None, description="카테고리 ID로 필터링"),
    search: str | None = Query(None, min_length=1, max_length=50, description="운동명 검색"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """전체 운동 목록 조회"""
    exercise_service = ExerciseService()

    try:
        exercises = await exercise_service.get_exercises(
            category_id=category_id, search=search, user_id=current_user.user_id
        )

        return exercises

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"운동 목록 조회 실패: {str(e)}")


@router.get(
    "/{exercise_id}",
    response_model=ExerciseDetail,
    summary="특정 운동 상세 정보 조회",
    description="특정 운동의 상세 정보와 모든 레벨 정보를 조회합니다.",
)
async def get_exercise_detail(
    exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """특정 운동 상세 정보 조회"""
    exercise_service = ExerciseService()

    try:
        exercise = await exercise_service.get_exercise_detail(exercise_id=exercise_id, user_id=current_user.user_id)

        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="운동을 찾을 수 없습니다")

        return exercise

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"운동 상세 정보 조회 실패: {str(e)}"
        )


@router.get(
    "/{exercise_id}/levels",
    response_model=List[ExerciseLevelList],
    summary="운동 레벨 목록 조회",
    description="특정 운동의 모든 레벨 정보를 조회합니다.",
)
async def get_exercise_levels(
    exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """운동 레벨 목록 조회"""
    exercise_service = ExerciseService()

    try:
        levels = await exercise_service.get_exercise_levels(exercise_id=exercise_id, user_id=current_user.user_id)

        if not levels:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="운동 레벨을 찾을 수 없습니다")

        return levels

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"운동 레벨 조회 실패: {str(e)}")


@router.get(
    "/categories/{category_id}",
    response_model=List[ExerciseList],
    summary="카테고리별 운동 목록 조회",
    description="특정 카테고리의 운동 목록을 조회합니다.",
)
async def get_exercises_by_category(
    category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """카테고리별 운동 목록 조회"""
    exercise_service = ExerciseService()

    try:
        exercises = await exercise_service.get_exercises(category_id=category_id, user_id=current_user.user_id)

        return exercises

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"카테고리별 운동 목록 조회 실패: {str(e)}"
        )
