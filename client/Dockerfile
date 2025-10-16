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
