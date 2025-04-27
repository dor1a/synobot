# Synobot (Refactor Version)

## 주요 변경사항

### 1. Telegram 제거 → Discord Webhook 기반 알림 전환
- 기존 Telegram Bot 의존성 제거
- Discord Webhook을 통한 임베드(embed) 스타일 알림 지원
- 에러/로그인/다운로드 상태별 색상 표시 (성공: 초록, 에러: 빨강, 대기/일시중지: 파랑)

### 2. BotConfig.py 리팩토링
- Telegram 관련 불필요한 환경변수(TG_*) 정리
- Discord Webhook URL 만 환경변수로 사용 (DC_WEBHOOK_URL)

### 3. Bothandler.py / Synods.py 리팩토링
- 코드 간결화 및 기능 분리
- 상태 변화 감지 시에만 알림 발송
- 상태별 embed 색상 적용
- 상태 메시지 다국어 지원 (ko_kr.json 기반)

### 4. 다국어 (ko_kr.json) 지원
- 상태 메시지 및 오류 메시지 한글 적용
- fallback(기본) 영문 → 한글 변환 구조 적용

### 5. 기타 개선사항
- 무한 루프/중복 알림 방지
- Docker 로그(docker logs)에 Task 정보 출력
- task ID / 파일명 / 용량 / 사용자 정보 명확하게 출력
- 코드 스타일 개선 (PEP8 일부 준수)
- 시그널 처리(SIGTERM, SIGINT 등) 및 정상 종료 지원

---

## 사용 방법

### 환경 변수 예시
``` env
DC_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/yyy"
DSM_ID="your_synology_id"
DSM_PW="your_synology_password"
DSM_URL="https://your.synology.url"
DS_PORT="5001"
```

### 실행
``` bash
docker build -t synobot:latest .
docker run -d --name synobot synobot:latest
```

---

## 주의사항
- Docker 컨테이너 안에서 DSM 접근 가능해야 합니다.
- SSL 인증서 오류 무시 설정(환경변수 DSM_CERT) 여부에 따라 다릅니다.
- Discord 메시지 사이즈(Embed) 제한 주의하세요.

---

## 참고
- 본 프로젝트는 [acidpop/synobot](https://github.com/acidpop/synobot) 레포지토리를 기반으로 수정/개선되었습니다.
