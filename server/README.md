## 개발 환경 설정

### 1. uv 패키지 매니저 설치

이 프로젝트는 uv 패키지 매니저를 사용합니다. uv가 설치되지 않은 경우 [설치 가이드](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)를 참고하여 설치하세요.

### 2. VSCode 확장 프로그램 설치

- charliermarsh.ruff

- 프로젝트 루트에 .vscode/settings.json 파일을 생성하고 다음 내용을 추가하세요.

```
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.nativeServer": "on"
}
```

### 3. 실행

- 프로젝트 루트 디렉토리에서 다음 명령어로 개발 서버를 실행하세요.

```
uv run uvicorn app.main:app --reload
```
