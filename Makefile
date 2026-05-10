.PHONY: dev db-up db-down db-logs migrate revision 

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

revision:
	uv run alembic revision --autogenerate -m "$(MSG)"

lint:
	uv run ruff check .
	
format:
	uv run ruff format .
	uv run ruff check --fix .

cli:
	uv run company-lens $(ARGS)
