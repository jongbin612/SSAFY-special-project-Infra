# app/api/v1/home.py

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.home import HomePageResponse
from app.schemas.user import User
from app.services.home_service import HomeService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/",
    response_model=HomePageResponse,
    summary="메인페이지 데이터 조회",
    description="최근 운동 3개와 인기 운동을 조회합니다.",
)
async def get_home_page_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """메인페이지 데이터 조회"""
    home_service = HomeService()

    try:
        home_data = await home_service.get_home_page_data(user_id=current_user.user_id if current_user else None)

        return home_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"메인페이지 데이터 조회 실패: {str(e)}"
        )
