install:
	uv sync --all-groups

up:
	docker compose up --build -d

stop:
	docker compose stop

down:
	docker compose down

logs:
	docker compose logs -f api consumer

migrate-up:
	uv run alembic -c pyproject.toml upgrade head

migrate-empty:
	@NUM=$$(ls src/infrastructure/database/sql/migration/versions/*.py | wc -l); \
	uv run alembic -c pyproject.toml revision --rev-id $$(printf "%04d" $$((NUM+1)))

test:
	uv run pytest

lint:
	uv run ruff check

format:
	uv run ruff check --fix && uv run ruff format
