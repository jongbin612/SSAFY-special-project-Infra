# app/api/v1/__init__.py

from fastapi import APIRouter

from . import analysis, auth, categories, exercises, home, users, workouts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["운동"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["운동 목록"])
api_router.include_router(home.router, prefix="/home", tags=["메인페이지"])
api_router.include_router(categories.router, prefix="/categories", tags=["운동 카테고리"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["체형 분석"])
