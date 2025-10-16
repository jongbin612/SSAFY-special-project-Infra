# Python slim 이미지 사용
FROM python:3.12-slim

WORKDIR /app

# psycopg2 빌드를 위한 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN pip install uv

# 의존성 복사 및 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 소스 복사
COPY . .

# 프로젝트 설치
RUN uv sync --frozen --no-dev

# FastAPI 실행
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
