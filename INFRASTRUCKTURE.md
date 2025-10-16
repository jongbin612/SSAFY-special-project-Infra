
Git push 시 Jenkins가 자동으로 Docker 빌드 및 배포를 수행하며,  
Nginx가 Reverse Proxy로 프론트와 백엔드 트래픽을 라우팅합니다.

---

## System Components

| 구성 요소 | 기술 스택 | 역할 |
|------------|-----------|------|
| CI/CD | Jenkins | 코드 빌드 및 자동 배포 |
| Infra | Docker, Docker Compose | 컨테이너 통합 환경 관리 |
| Proxy | Nginx, Let’s Encrypt | HTTPS 트래픽 관리 및 리버스 프록시 |
| Frontend | Vue 3, Vite | 사용자 인터페이스 |
| Backend | FastAPI, Uvicorn | API 서버 |
| Database | PostgreSQL | 데이터 저장소 |

---

## Key Features

- Jenkins Webhook 기반 자동화 배포
- Docker Compose를 통한 멀티 컨테이너 환경
- HTTPS 기반 Reverse Proxy 구성
- SPA(Vue)와 API(FastAPI)의 통합 운영
- 서비스 간 통신을 위한 Docker 네트워크 관리

---

## Diagram
[Developer Push]
↓
[GitLab Repo]
↓ (Webhook)
[Jenkins Server]
↓
[Docker Compose Deploy]
↓
[Nginx Reverse Proxy]
├─ Frontend (Vue)
├─ Backend (FastAPI)
└─ PostgreSQL

이 구조를 통해 코드 푸시 한 번으로 전체 서비스가 자동으로 빌드되고 배포되도록 구성했습니다.