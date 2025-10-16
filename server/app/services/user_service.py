# app/services/user_service.py

import uuid
from pathlib import Path
from typing import List

from app.core.auth import get_password_hash, verify_password
from app.core.database import SessionLocal
from app.models.user import UserModel
from app.schemas.user import User, UserCreateEmail, UserCreateGoogle, UserDetail
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session


class UserService:
    def __init__(self):
        pass

    def _get_db(self) -> Session:
        """데이터베이스 세션 생성"""
        return SessionLocal()

    async def get_user_detail(self, user_id: int, current_user: User | None = None) -> UserDetail | None:
        """사용자 상세 정보 조회"""
        db = self._get_db()
        try:
            # 1. 기본 사용자 정보 조회
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(stmt).scalar_one_or_none()

            if not user_model:
                return None

            # 2. 본인 프로필 여부 확인
            is_own_profile = current_user and current_user.user_id == user_id

            # 3. 모든 정보 포함하여 구성
            user_data = {
                "user_id": user_model.user_id,
                "name": user_model.name,
                "profile_image_url": user_model.profile_image_url,
                "birth_date": user_model.birth_date,
                "gender": user_model.gender,
                "height": user_model.height,
                "weight": user_model.weight,
                "created_at": user_model.created_at,
            }

            # 본인만 볼 수 있는 정보
            if is_own_profile:
                user_data.update({"email": user_model.email})

            return UserDetail(**user_data)

        except Exception as e:
            raise Exception(f"사용자 상세 정보 조회 실패: {str(e)}")
        finally:
            db.close()

    async def get_user_by_email(self, email: str) -> User | None:
        db = self._get_db()
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = db.execute(stmt)
            user_model = result.scalar_one_or_none()

            return User.from_orm(user_model) if user_model else None

        except Exception as e:
            raise Exception(f"사용자 조회 실패: {str(e)}")
        finally:
            db.close()

    async def create_user_email(self, user_data: UserCreateEmail) -> User:
        db = self._get_db()
        try:
            # 이메일 중복 체크
            if await self._check_user_by_email(user_data.email, db):
                raise Exception("이미 등록된 이메일입니다")

            # 사용자 생성
            user_model = UserModel(
                google_id=None,
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                name=user_data.name,
                profile_image_url=user_data.profile_image_url,
                birth_date=user_data.birth_date,
                gender=user_data.gender,
                height=user_data.height,
                weight=user_data.weight,
            )

            db.add(user_model)
            db.commit()
            db.refresh(user_model)

            return User.from_orm(user_model)

        except Exception as e:
            db.rollback()
            raise Exception(f"이메일 회원가입 실패: {str(e)}")
        finally:
            db.close()

    async def create_user_google(self, user_data: UserCreateGoogle) -> User:
        db = self._get_db()
        try:
            # 중복 체크
            if await self._check_user_by_email(user_data.email, db):
                raise Exception("이미 등록된 이메일입니다")

            if await self._check_user_by_google_id(user_data.google_id, db):
                raise Exception("이미 등록된 Google 계정입니다")

            # 사용자 생성
            user_model = UserModel(
                google_id=user_data.google_id,
                email=user_data.email,
                password_hash=None,
                name=user_data.name,
                profile_image_url=user_data.profile_image_url,
                birth_date=user_data.birth_date,
                gender=user_data.gender,
                height=user_data.height,
                weight=user_data.weight,
            )

            db.add(user_model)
            db.commit()
            db.refresh(user_model)

            return User.from_orm(user_model)

        except Exception as e:
            db.rollback()
            raise Exception(f"Google 회원가입 실패: {str(e)}")
        finally:
            db.close()

    async def authenticate_user_email(self, email: str, password: str) -> User | None:
        db = self._get_db()
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            user_model = db.execute(stmt).scalar_one_or_none()

            if not user_model or user_model.google_id or not verify_password(password, user_model.password_hash):
                return None

            # 마지막 로그인 시간 업데이트
            from datetime import datetime

            user_model.updated_at = datetime.utcnow()
            db.commit()

            return User.from_orm(user_model)

        except Exception as e:
            raise Exception(f"이메일 로그인 실패: {str(e)}")
        finally:
            db.close()

    async def authenticate_user_google(self, email: str, google_id: str) -> User | None:
        db = self._get_db()
        try:
            # Google ID로 사용자 조회
            stmt = select(UserModel).where(UserModel.google_id == google_id)
            user_model = db.execute(stmt).scalar_one_or_none()

            if user_model and user_model.email == email:
                # 마지막 로그인 시간 업데이트
                from datetime import datetime

                user_model.updated_at = datetime.utcnow()
                db.commit()

                return User.from_orm(user_model)

            return None

        except Exception as e:
            raise Exception(f"Google 로그인 실패: {str(e)}")
        finally:
            db.close()

    async def check_email_exists(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return user is not None

    async def update_user_profile(
        self, user_id: int, update_data: dict, profile_image_url: UploadFile | None = None
    ) -> tuple[User, List[str]]:
        """사용자 프로필 업데이트 - 추가 정보 포함"""
        db = self._get_db()
        try:
            # 사용자 조회
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(stmt).scalar_one_or_none()

            if not user_model:
                raise Exception("사용자를 찾을 수 없습니다")

            # Google 계정인 경우 비밀번호 변경 제한
            if user_model.google_id and "password" in update_data:
                raise Exception("Google 계정은 비밀번호를 변경할 수 없습니다")

            updated_fields = []

            # 기본 정보 업데이트
            if "name" in update_data and update_data["name"]:
                user_model.name = update_data["name"]
                updated_fields.append("name")

            if "birth_date" in update_data and update_data["birth_date"] is not None:
                user_model.birth_date = update_data["birth_date"]
                updated_fields.append("birth_date")

            if "gender" in update_data and update_data["gender"]:
                user_model.gender = update_data["gender"]
                updated_fields.append("gender")

            if "height" in update_data and update_data["height"] is not None:
                user_model.height = update_data["height"]
                updated_fields.append("height")

            if "weight" in update_data and update_data["weight"] is not None:
                user_model.weight = update_data["weight"]
                updated_fields.append("weight")

            # 비밀번호 업데이트
            if "password" in update_data and update_data["password"]:
                user_model.password_hash = get_password_hash(update_data["password"])
                updated_fields.append("password")

            # 프로필 이미지 업데이트
            if profile_image_url:
                image_url = await self._save_profile_image(user_id, profile_image_url)
                user_model.profile_image_url = image_url
                updated_fields.append("profile_image_url")

            if not updated_fields:
                raise Exception("수정할 정보가 없습니다")

            # 업데이트 시간 갱신
            from datetime import datetime

            user_model.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(user_model)

            return User.from_orm(user_model), updated_fields

        except Exception as e:
            db.rollback()
            raise Exception(f"프로필 업데이트 실패: {str(e)}")
        finally:
            db.close()

    async def verify_current_password(self, user_id: int, password: str) -> bool:
        """현재 비밀번호 확인"""
        db = self._get_db()
        try:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(stmt).scalar_one_or_none()

            if not user_model or user_model.google_id:
                return False

            return verify_password(password, user_model.password_hash)

        except Exception:
            return False
        finally:
            db.close()

    async def _check_user_by_email(self, email: str, db: Session) -> bool:
        """이메일 중복 체크"""
        stmt = select(UserModel).where(UserModel.email == email)
        result = db.execute(stmt).scalar_one_or_none()
        return result is not None

    async def _check_user_by_google_id(self, google_id: str, db: Session) -> bool:
        """Google ID 중복 체크"""
        stmt = select(UserModel).where(UserModel.google_id == google_id)
        result = db.execute(stmt).scalar_one_or_none()
        return result is not None

    async def _save_profile_image(self, user_id: int, image_file: UploadFile) -> str:
        """프로필 이미지 파일 저장"""
        try:
            # 파일 유효성 검사
            if not image_file.content_type or not image_file.content_type.startswith("image/"):
                raise Exception("이미지 파일만 업로드 가능합니다")

            # 파일 크기 제한 (5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            content = await image_file.read()
            if len(content) > max_size:
                raise Exception("파일 크기는 5MB를 초과할 수 없습니다")

            # 저장 디렉토리 생성
            upload_dir = Path("static/profile_images")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # 고유한 파일명 생성
            file_extension = image_file.filename.split(".")[-1] if "." in image_file.filename else "jpg"
            unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
            file_path = upload_dir / unique_filename

            # 파일 저장
            with open(file_path, "wb") as buffer:
                buffer.write(content)

            # URL 반환
            return f"/static/profile_images/{unique_filename}"

        except Exception as e:
            raise Exception(f"이미지 저장 실패: {str(e)}")

    async def get_all_users(self) -> list[User]:
        """DB 전체 사용자 조회"""
        db = self._get_db()
        try:
            stmt = select(UserModel)
            result = db.execute(stmt)
            return [User.from_orm(user_model) for user_model in result.scalars()]

        except Exception as e:
            raise Exception(f"전체 사용자 조회 실패: {str(e)}")
        finally:
            db.close()
