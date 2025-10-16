# app/api/v1/users.py

from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.schemas.user import User, UserDetail, UserProfileUpdateResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserDetail,
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다. 이메일 등 개인정보도 포함됩니다.",
)
async def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """내 프로필 조회"""
    user_service = UserService()

    try:
        user_detail = await user_service.get_user_detail(current_user.user_id, current_user)
        return user_detail

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/me/profile",
    response_model=UserProfileUpdateResponse,
    summary="내 프로필 수정",
    description="현재 로그인한 사용자의 프로필을 수정합니다. 이름, 비밀번호, 프로필 이미지를 변경할 수 있습니다.",
)
async def update_my_profile(
    name: str | None = Form(None, min_length=2, max_length=50, description="변경할 사용자 이름"),
    password: str | None = Form(None, min_length=8, description="변경할 비밀번호"),
    current_password: str | None = Form(None, description="현재 비밀번호 (비밀번호 변경 시 필수)"),
    profile_image_url: UploadFile | None = File(None, description="프로필 이미지 파일"),
    current_user: User = Depends(get_current_user),
):
    """내 프로필 수정"""
    user_service = UserService()

    try:
        # 비밀번호 변경 시 현재 비밀번호 확인
        if password and not current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 변경 시 현재 비밀번호가 필요합니다",
            )

        if password and current_password:
            is_valid = await user_service.verify_current_password(current_user.user_id, current_password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="현재 비밀번호가 일치하지 않습니다",
                )

        update_data = {}
        if name:
            update_data["name"] = name
        if password:
            update_data["password"] = password

        # 프로필 업데이트
        updated_user, updated_fields = await user_service.update_user_profile(
            current_user.user_id, update_data, profile_image_url
        )

        return UserProfileUpdateResponse(
            message="프로필이 성공적으로 업데이트되었습니다",
            updated_fields=updated_fields,
            user=updated_user,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 업데이트 실패: {str(e)}",
        )


@router.get(
    "/dev/all",
    response_model=List[User],
    summary="전체 사용자 조회",
    description="등록된 모든 사용자 목록을 조회합니다.",
)
async def get_all_users(db: Session = Depends(get_db)):
    """전체 사용자 조회"""
    user_service = UserService()

    try:
        users = await user_service.get_all_users()
        return users

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=UserDetail,
    summary="사용자 상세 정보",
    description="특정 사용자의 상세 정보를 조회합니다.",
)
async def get_user_detail(
    user_id: int,
    current_user: User | None = Depends(get_optional_current_user),
):
    """사용자 상세 정보 조회"""
    user_service = UserService()

    try:
        user_detail = await user_service.get_user_detail(user_id, current_user)

        if not user_detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")

        return user_detail

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
