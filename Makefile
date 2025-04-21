runserver:
	uv run manage.py runserver 0.0.0.0:8000

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate