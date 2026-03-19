.PHONY: help dev up down logs test lint migrate shell

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------- Development ----------

dev: ## Start all services (dev mode with hot reload)
	docker compose up --build

up: ## Start all services (detached)
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

logs-web: ## Tail web service logs
	docker compose logs -f web

logs-worker: ## Tail celery worker logs
	docker compose logs -f celery_worker

# ---------- Database ----------

migrate: ## Run Alembic migrations
	docker compose exec web alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new msg="description")
	docker compose exec web alembic revision --autogenerate -m "$(msg)"

# ---------- Testing ----------

test: ## Run tests
	docker compose exec web pytest tests/ -v

test-unit: ## Run unit tests only
	docker compose exec web pytest tests/unit/ -v

test-int: ## Run integration tests only
	docker compose exec web pytest tests/integration/ -v

# ---------- Code Quality ----------

lint: ## Run ruff linter
	docker compose exec web ruff check src/ tests/

format: ## Auto-format code
	docker compose exec web ruff format src/ tests/

# ---------- Utilities ----------

shell: ## Open a Python shell in the web container
	docker compose exec web python

bash: ## Open a bash shell in the web container
	docker compose exec web bash

psql: ## Open psql in the postgres container
	docker compose exec postgres psql -U gtm_user -d gtm_analysis

redis-cli: ## Open redis-cli
	docker compose exec redis redis-cli
