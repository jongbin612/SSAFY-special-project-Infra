# app/database.py

from app.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 설정에서 DATABASE_URL 가져오기
settings = get_settings()

# 엔진 생성
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=20,  # 기본 연결 풀 크기 증가
    max_overflow=30,  # 추가 연결 수 증가
    pool_timeout=30,  # 연결 대기 시간 증가 (기본 30초)
    pool_recycle=3600,  # 1시간마다 연결 재생성
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


# 의존성 주입용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
