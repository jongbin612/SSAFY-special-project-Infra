# 홈피티 (HomePT)<img width="50" height="50" alt="image" src="https://github.com/user-attachments/assets/d1faec8c-a60f-419e-bb82-8a757452b5d8" />


AI 트레이너 기반 홈 트레이닝 서비스입니다.  
Frontend(React/Next.js)와 Backend(FastAPI/Django)를 Docker 기반으로 통합 배포했으며,  
Jenkins를 통한 CI/CD 자동화 파이프라인을 구축했습니다.

---

## 주요 기능

- 사용자 인증 (JWT / OAuth)
- 개인 맞춤 운동 추천 및 영상 피드백
- AI 체형 분석 및 운동 자세 평가
- 커뮤니티 기능 (게시글, 댓글)
- 실시간 WebSocket 기반 AI 코칭

---

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **Frontend** | React, Next.js, Tailwind, TypeScript | 사용자 인터페이스 |
| **Backend** | FastAPI, Django REST Framework | API 및 AI 서비스 |
| **Database** | PostgreSQL | 데이터 저장 |
| **Infra** | Jenkins, Docker, Docker Compose, Nginx, AWS EC2 | CI/CD 및 서버 운영 |
| **AI** | PyTorch, HuggingFace Transformers | 체형 분석 모델 |

---

## 인프라 담당 역할

### CI/CD 자동화 구축
- Jenkins를 이용해 **백엔드 자동 빌드 및 배포 파이프라인** 구성  
- Git push 시 Docker 이미지 빌드 및 컨테이너 재배포 자동화  
- 프론트엔드는 자동 배포 중 **Nginx 라우팅 충돌 이슈**로 인해  
  일시적으로 **정적 빌드 파일(Nginx 서빙)** 방식으로 대체  

### Docker 환경 구성
- `docker-compose.yml`을 통해 Backend, Frontend, Database 컨테이너 통합 관리  
- 단일 네트워크(`app-network`) 내 서비스 간 통신 및 의존성 제어  

### Reverse Proxy & HTTPS 구성
- Nginx Reverse Proxy를 이용해 `/api` 트래픽을 FastAPI로 라우팅  
- Let’s Encrypt 인증서로 SSL 적용 및 자동 갱신 설정  

### 서버 및 배포 환경 세팅
- Ubuntu 22.04 EC2 환경에서 Docker, Jenkins, PostgreSQL, Node.js 설치 및 설정  
- 환경 변수, 볼륨, 자동 재시작 정책(`restart: unless-stopped`) 구성  

---

## 배포 구조
[GitLab Repository]  
↓ (Webhook)  
[Jenkins Server - CI/CD Pipeline]  
↓  
[Docker Build & Deploy]  
↓  
[Nginx Reverse Proxy]  
├─ [Frontend - Next.js]  
├─ [Backend - FastAPI]  
└─ [Database - PostgreSQL]


---

## 트러블슈팅

| 이슈 | 원인 | 조치 |
|------|------|------|
| 프론트 자동 배포 실패 | Jenkins에서 Vite 빌드 후 Nginx 경로 충돌 발생 | 정적 빌드(`dist/`)를 서버에 직접 복사하여 임시 해결 |
| Certbot 인증 갱신 충돌 | Nginx 재시작 시 인증서 경로 잠김 | `--nginx` 옵션 추가로 자동 갱신 해결 |
| 백엔드 이미지 빌드 오류 | uv.lock 환경 패키지 충돌 | `uv sync --no-install-project`로 재설정 후 해결 |

---

## 결과 요약

- 백엔드 자동 배포 파이프라인 완성 (Jenkins → Docker → FastAPI)  
- 프론트는 정적 빌드로 전환하여 서비스 안정적으로 운영  
- Jenkins, Docker, Nginx, SSL 환경 직접 세팅 및 최적화 수행  
- 향후 프론트 자동 배포 구조 개선을 위해 Jenkins stage 분리 계획  

---

> 인프라 담당으로 CI/CD, Docker Compose, Nginx, 서버 세팅 전반을 직접 설계 및 구현했습니다.
