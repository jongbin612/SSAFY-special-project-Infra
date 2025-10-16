# app/main.py


from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.init_db import init_db, init_sample_data
from app.websockets import workout_socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 설정 로드
settings = get_settings()

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 데이터베이스 초기화
init_db()

# 샘플 데이터 초기화
init_sample_data()

# FastAPI 앱 생성
app = FastAPI(
    title="ww",
    description="Workout Service",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    root_path="/api",
    servers=[{"url": "/api"}],
)


ALLOWED_ORIGINS = ["http://localhost:5173", "https://j13m103.p.ssafy.io"]

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# API v1 라우터 등록
app.include_router(api_router, prefix="/v1")
app.include_router(workout_socket.router, prefix="/ws")


@app.get("/")
def read_root():
    """서비스 루트"""
    return {
        "service": "wo",
        "description": "Workout Service",
        "version": "1.0.0",
        "docs": "/docs",
    }
