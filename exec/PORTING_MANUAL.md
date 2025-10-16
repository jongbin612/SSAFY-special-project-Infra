# 홈피티 - 포팅 매뉴얼

## 1. 개발 환경

### Backend
- FastAPI  
- Django + DRF  
- PostgreSQL (SQLAlchemy, psycopg2)  
- PyTorch  
- HuggingFace Transformers  
- JWT / OAuth (djoser, allauth, social-auth, simplejwt)  

### Frontend
- TypeScript  
- React  
- Next.js  
- Tailwind  

### DB
- PostgreSQL  

### Infra
- AWS EC2  
- Ubuntu  
- Docker  
- Docker Compose  
- Jenkins  

---

## 2. 서버 환경 정보

| 항목 | 버전 / 내용 |
| --- | --- |
| OS | **Ubuntu 22.04.5 LTS (Jammy Jellyfish)** |
| Kernel | **6.8.0-1036-aws** |
| Nginx | **1.18.0** |
| Node.js | **v20.19.5** |
| npm | **10.8.2** |
| Python | **3.10.12** |
| Uvicorn | **0.15.0** |
| Git | **2.34.1** |
| Jenkins | **2.529** |
| Docker | **28.4.0** |
| Docker Compose | **v2.39.4** |
| PostgreSQL | **17** |

---

## 3. 프로젝트 사용 도구

| 구분 | 도구 |
| --- | --- |
| **이슈 관리** | JIRA |
| **형상 관리** | GitLab |
| **커뮤니케이션** | Notion, Mattermost |
| **디자인** | Figma |
| **CI/CD** | EC2, Jenkins, Docker |

---

## 4. FRONTEND - Dockerfile

```dockerfile
# 1단계: 빌드
FROM node:20-alpine AS build

WORKDIR /app

# 패키지 설치
COPY package.json package-lock.json* ./

# 우선 lock 파일 기반 설치, 실패하면 일반 npm install
RUN npm ci || npm install

# 소스 복사
COPY . .

# Vite 빌드
RUN npm run build

# 2단계: Nginx로 정적 파일 서빙
FROM nginx:1.27-alpine

# Vite 빌드 결과물 복사
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. BACKEND - Dockerfile

```dockerfile
# Python slim 이미지 사용
FROM python:3.12-slim

WORKDIR /app

# psycopg2 빌드를 위한 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential libpq-dev curl     && rm -rf /var/lib/apt/lists/*

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
```

---

## 6. docker-compose.yml

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile
    container_name: frontend-container
    ports:
      - "3000:80"  # Nginx 서빙
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: ./server
      dockerfile: Dockerfile
    container_name: backend-container
    ports:
      - "9000:9000"  # FastAPI
    env_file:
      - /var/lib/jenkins/workspace/frontend-pipeline/server/.env
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    container_name: postgres-container
    environment:
      POSTGRES_DB: ww
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 6363
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ww"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

---

## 7. Nginx 설정 (etc/nginx/conf.d/myserver.conf)

```nginx
# HTTP → HTTPS 리다이렉트
server {
    listen 80;
    server_name j13m103.p.ssafy.io;

    return 301 https://$host$request_uri;
}

# HTTPS 서버 블록
server {
    listen 443 ssl http2;
    server_name j13m103.p.ssafy.io;

    ssl_certificate     /etc/letsencrypt/live/j13m103.p.ssafy.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/j13m103.p.ssafy.io/privkey.pem;
    
    location / {
        root /home/ubuntu/S13P21M703/client/dist;
        index index.html;
        try_files $uri /index.html;
    }

    # === FastAPI 백엔드 (9000포트) ===
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # === AI 서버 (8081포트) ===
    location /ai {
        proxy_pass http://localhost:8081;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # === WebSocket 설정 ===
    location /ws/ {
        proxy_pass http://localhost:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

---

## 8. 빌드 시 사용되는 환경 변수

### Backend (`server/.env`)

```env
# 애플리케이션 설정
APP_NAME={애플리케이션 이름}
DEBUG={true/false}

# 인증 관련 설정
SECRET_KEY={JWT 시크릿 키}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES={43200}

# PostgreSQL 데이터베이스 설정
DATABASE_URL=postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}

# Google OAuth 설정
GOOGLE_CLIENT_ID={구글 OAuth 클라이언트 ID}
GOOGLE_CLIENT_SECRET={구글 OAuth 클라이언트 시크릿}

# Redirect URI
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/google/callback
# 운영 환경 예시
# GOOGLE_REDIRECT_URI=https://{SERVER_HOST}/api/v1/auth/google/callback
```

### Frontend (`client/.env`)

```env
VITE_API_URL=/api/v1
VITE_ELEVENLABS_API_KEY={VITE_ELEVENLABS_API_KEY}
VITE_SOCKET_URL=wss://j13m103.p.ssafy.io
```

---

## 9. 서버 기본 설정

### 시스템 업데이트
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

### 필수 패키지 설치
```bash
sudo apt-get install -y     curl     wget     unzip     apt-transport-https     ca-certificates     gnupg-agent     software-properties-common     lsb-release
```

### Node.js & npm 설치
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

node -v
npm -v
```

### PostgreSQL
```bash
sudo apt-get install -y postgresql postgresql-contrib
psql --version
```

### Docker & Docker Compose
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

sudo curl -L "https://github.com/docker/compose/releases/download/v2.39.4/docker-compose-$(uname -s)-$(uname -m)"   -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker --version
docker compose version
```

### Jenkins
```bash
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo tee     /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]     https://pkg.jenkins.io/debian binary/ | sudo tee     /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y openjdk-17-jdk jenkins

sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```
