runserver:
	uv run manage.py runserver 0.0.0.0:8000

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

test:
	DJANGO_SETTINGS_MODULE=config.settings.test
	uv run coverage run --source='.' --omit='*/migrations/*' --branch manage.py test
	uv run coverage report -m