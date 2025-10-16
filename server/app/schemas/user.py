# app/schemas/user.py

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int | None = Field(default=None, description="사용자 ID")
    google_id: str | None = Field(default=None, description="구글 ID")
    email: str = Field(description="이메일")
    name: str = Field(description="사용자 이름")
    profile_image_url: str | None = Field(default=None, description="프로필 이미지 URL")
    birth_date: date | None = Field(default=None, description="생년월일")
    gender: str | None = Field(default=None, description="성별 (male, female, other)")
    height: float | None = Field(default=None, description="신장 (cm)")
    weight: float | None = Field(default=None, description="체중 (kg)")
    created_at: datetime | None = Field(default=None, description="생성일시")
    updated_at: datetime | None = Field(default=None, description="수정일시")

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    """사용자 상세 정보"""

    user_id: int = Field(description="사용자 ID")
    email: str | None = Field(default=None, description="이메일 (본인만 조회 가능)")
    name: str = Field(description="사용자 이름")
    profile_image_url: str | None = Field(default=None, description="프로필 이미지 URL")
    birth_date: date | None = Field(default=None, description="생년월일")
    gender: str | None = Field(default=None, description="성별 (male, female, other)")
    height: float | None = Field(default=None, description="신장 (cm)")
    weight: float | None = Field(default=None, description="체중 (kg)")
    created_at: datetime = Field(description="가입일시")

    class Config:
        from_attributes = True


class UserCreateEmail(BaseModel):
    email: str = Field(description="이메일")
    password: str = Field(description="비밀번호", min_length=6)
    name: str = Field(description="사용자 이름", min_length=2)
    profile_image_url: str | None = Field(default=None, description="프로필 이미지 URL")
    birth_date: date | None = Field(default=None, description="생년월일")
    gender: str | None = Field(default=None, description="성별 (male, female, other)")
    height: float | None = Field(default=None, ge=50, le=300, description="신장 (cm)")
    weight: float | None = Field(default=None, ge=20, le=500, description="체중 (kg)")


class UserCreateGoogle(BaseModel):
    google_id: str = Field(description="구글 ID")
    email: str = Field(description="이메일")
    name: str = Field(description="사용자 이름")
    profile_image_url: str | None = Field(default=None, description="프로필 이미지 URL")
    birth_date: date | None = Field(default=None, description="생년월일")
    gender: str | None = Field(default=None, description="성별 (male, female, other)")
    height: float | None = Field(default=None, ge=50, le=300, description="신장 (cm)")
    weight: float | None = Field(default=None, ge=20, le=500, description="체중 (kg)")


class UserLoginEmail(BaseModel):
    email: str = Field(description="이메일")
    password: str = Field(description="비밀번호")


class EmailCheck(BaseModel):
    email: str = Field(description="확인할 이메일")


class TokenResponse(BaseModel):
    access_token: str = Field(description="액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user: User = Field(description="사용자 정보")


class UserProfileUpdate(BaseModel):
    """사용자 프로필 수정 요청"""

    name: str | None = Field(None, min_length=2, max_length=50, description="변경할 사용자 이름")
    password: str | None = Field(None, min_length=8, description="변경할 비밀번호")
    profile_image_url: str | None = Field(None, description="프로필 이미지 URL")
    birth_date: date | None = Field(None, description="생년월일")
    gender: str | None = Field(None, description="성별 (male, female, other)")
    height: float | None = Field(None, ge=50, le=300, description="신장 (cm)")
    weight: float | None = Field(None, ge=20, le=500, description="체중 (kg)")


class UserProfileUpdateResponse(BaseModel):
    """사용자 프로필 수정 응답"""

    message: str
    updated_fields: List[str]
    user: User


class UserProfileValidation(BaseModel):
    """프로필 데이터 유효성 검사용 스키마"""

    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("성별은 male, female 중 하나여야 합니다")
        return v

    @classmethod
    def validate_birth_date(cls, v):
        if v is not None:
            from datetime import date

            today = date.today()
            if v > today:
                raise ValueError("생년월일은 오늘 날짜보다 클 수 없습니다")
        return v

    @classmethod
    def validate_height(cls, v):
        if v is not None and (v < 0):
            raise ValueError("신장은 0cm보다 커야 합니다")
        return v

    @classmethod
    def validate_weight(cls, v):
        if v is not None and (v < 0):
            raise ValueError("체중은 0kg보다 커야 합니다")
        return v
