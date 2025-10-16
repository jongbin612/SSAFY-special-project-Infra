# app/api/v1/analysis.py

import logging
from typing import List

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.schemas.exercise import ExerciseList
from app.schemas.user import User
from app.services.body_type_service import BodyTypeService
from app.services.exercise_service import ExerciseService
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

settings = get_settings()

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 서비스 인스턴스
body_type_service = BodyTypeService()
exercise_service = ExerciseService()


class BodyTypeAnalysisResponse(BaseModel):
    """체형 분석 응답 모델"""

    predicted_body_type: str
    confidence: float
    processing_time_seconds: float
    message: str
    recommendations: List[ExerciseList]
    body_type_image_url: str

    class Config:
        from_attributes = True


@router.post(
    "/types",
    response_model=BodyTypeAnalysisResponse,
    summary="체형 분석",
    description="업로드된 전신 사진을 분석하여 체형을 예측하고 추천 운동을 제공합니다.",
)
async def analyze_body_type(
    file: UploadFile = File(..., description="분석할 전신 사진"), current_user: User = Depends(get_current_user)
):
    """체형 분석 API"""

    # 파일 형식 검증
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    # 파일 크기 검증
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")

    try:
        # 이미지 파일 읽기
        image_bytes = await file.read()

        # 체형 분석 수행
        result = body_type_service.analyze_body_type(image_bytes)

        recommended_exercises = []
        for exercise_id in [1, 2]:
            try:
                exercise = await exercise_service.get_exercise_by_id(exercise_id)
                if exercise:
                    recommended_exercises.append(exercise)
            except Exception as e:
                logger.warning(f"Failed to get exercise {exercise_id}: {e}")
                continue

        logger.info(f"Body type analysis completed for user {current_user.user_id}: {result['predicted_body_type']}")

        body_type_image_url = f"{settings.static_url}images/body_types/{result['predicted_body_type']}.png"

        return BodyTypeAnalysisResponse(
            predicted_body_type=result["predicted_body_type"],
            confidence=result["confidence"],
            processing_time_seconds=result["processing_time_seconds"],
            message="체형 분석이 완료되었습니다.",
            recommendations=recommended_exercises,
            body_type_image_url=body_type_image_url,
        )

    except ValueError as e:
        logger.error(f"Body type analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in body type analysis: {e}")
        raise HTTPException(status_code=500, detail="체형 분석 중 오류가 발생했습니다.")


@router.get(
    "/supported",
    summary="지원하는 체형 유형 조회",
    description="이 모델이 분류할 수 있는 체형 유형들을 반환합니다.",
)
async def get_supported_body_types():
    """지원하는 체형 유형 조회"""
    try:
        # 모델의 라벨 정보 반환
        supported_types = list(body_type_service.model.config.id2label.values())

        return {
            "supported_body_types": supported_types,
            "total_types": len(supported_types),
            "message": "지원하는 체형 유형 목록입니다.",
        }
    except Exception as e:
        logger.error(f"Failed to get supported body types: {e}")
        raise HTTPException(status_code=500, detail="체형 유형 조회 중 오류가 발생했습니다.")
