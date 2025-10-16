# app/core/config.py

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """설정 클래스"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # 애플리케이션 설정
    app_name: str = Field(default="TMDB Movie API", description="애플리케이션 이름")
    debug: bool = Field(default=False, description="디버그 모드")

    # 데이터베이스 설정
    database_url: str = Field(description="PostgreSQL 데이터베이스 URL")

    # 인증 설정
    secret_key: str = Field(default="secret-jwt-key", description="JWT 토큰 암호화 키")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")
    access_token_expire_minutes: int = Field(default=30, description="JWT 토큰 만료 시간(분)")

    # Google OAuth 설정
    google_client_id: str = Field(description="Google OAuth Client ID")
    google_client_secret: str = Field(description="Google OAuth Client Secret")
    google_redirect_uri: str = Field(
        default="http://127.0.0.1:8000/api/v1/auth/google/callback",
        description="Google OAuth 리디렉트 URI",
    )

    # STATIC
    static_url: str = Field(default="/static", description="정적 파일 URL 경로")

    # Hugging Face 설정
    hf_token: str = Field(default="", description="Hugging Face 액세스 토큰")


@lru_cache
def get_settings() -> Settings:
    return Settings()
