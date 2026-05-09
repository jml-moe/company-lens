.PHONY: dev db-up db-down db-logs migrate

dev:
	uv run uvicorn app.main:app --reload

db-up:
	docker compose up -d

db-down:
	docker compose down

db-logs:
	docker compose logs -f postgres

migrate:
	uv run alembic upgrade head
