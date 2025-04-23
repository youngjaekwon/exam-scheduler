# Exam Scheduler API

## Summary
시험 일정 예약 시스템 API입니다.  
사용자는 시험 일정을 조회하고 원하는 일정에 대해 예상 응시 인원을 예약할 수 있습니다.  
관리자는 시험 일정을 생성 및 관리하며, 각 예약을 검토하여 최종 확정 처리할 수 있습니다.

---

## 기능 설명
### 시험 일정 (ExamSchedule)
- 관리자만 생성, 수정, 삭제 가능
- 제목, 설명, 시험 시작/종료 시간 입력
- 응시자 수가 자동 집계됨

### 예약 (Reservation)
- 사용자가 시험 일정에 대해 예약 가능
- 예약 시 예상 응시 인원을 지정해야 함
- 예약은 확정 전 까지만 수정/삭제 가능
- 관리자는 모든 사용자의 예약을 수정/확정/삭제 가능

### 예약 마감 조건
- 시험 시작일 기준 `EXAM_RESERVATION_DEADLINE_DAYS`(일) 이전까지만 예약 가능
- 최대 응시 인원 수 `EXAM_SCHEDULE_MAX_PARTICIPANTS`(명)를 초과하면 예약 불가

---

## 실행 방법 (Docker Compose)
### env 파일 설정
```bash
  cp .env.example .env
```

### Windows
```bash
  docker-compose up -d --build 
```

### Linux/MacOS
```bash
  docker compose up -d --build
```

웹 서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

---

## 초기 더미 데이터 설명

초기 더미 데이터는 `entrypoint.sh`에서 자동으로 생성됩니다.

### 생성되는 계정:
| 역할     | ID        | PW       |
|----------|-----------|----------|
| 관리자   | adminuser | admin123 |
| 사용자 1 | user1     | pass     |
| 사용자 2 | user2     | pass     |

### 생성되는 시험 일정:
- 예약 가능 일정 1개
- 날짜로 마감된 일정 1개
- 인원으로 마감된 일정 1개

### 생성되는 예약:
- user1: 확정 전 예약 1건, 확정된 예약 1건
- user2: 확정 전 예약 1건

---

## API 문서

### Swagger UI
Swagger UI 문서는 아래 주소에서 확인 가능합니다:
```
http://localhost:8000/api/docs/
```

### ReDoc
ReDoc 문서는 아래 주소에서 확인 가능합니다:
```
http://localhost:8000/api/redoc/
```

---
## 로컬 실행 방법
### env 파일 설정
```bash
  cp .env.dev.example .env.dev
```

### uv, make 사용
```bash
  uv sync
  make migrate
  make runserver
```

### pip 사용
```bash
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver
```

---

## 로컬 테스트 방법
### env 파일 설정
```bash
  cp .env.test.example .env.test
```

### uv, make 사용
```bash
  uv test
```

### pip 사용
```bash
  DJANGO_SETTINGS_MODULE=config.settings.test
  DJANGO_ENVIRONMENT_FILE=.env.test
  coverage run --source='.' --omit='*/migrations/*' --branch manage.py test
  coverage report -m
```

---

## 디렉터리 구조
```
.
├── config/              # Django 설정
├── core/                # 공통 기능 및 설정
├── schedules/           # 시험 일정 관련 앱
├── reservations/        # 예약 관련 앱
├── users/               # 사용자 등록/인증 관련 앱
├── manage.py
├── requirements.txt
├── docker-compose.yml
└── entrypoint.sh        # 초기 실행 스크립트
```