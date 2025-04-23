FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 1. 프로젝트 복사
COPY . .

# 2. 의존성 설치
RUN uv sync --frozen

# 3. EntryPoint 설정
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# 4. gunicorn 실행
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]