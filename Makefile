.PHONY: help setup dev test lint typecheck migrate docker-up docker-down clean
.DEFAULT_GOAL := help

SERVICE_DIR := apps/learning-service

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies
	cd $(SERVICE_DIR) && uv pip install --system ".[dev]"
	pre-commit install

dev: ## Start development environment
	docker compose up -d postgres
	cd $(SERVICE_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8100

test: ## Run tests
	cd $(SERVICE_DIR) && pytest -v --tb=short

lint: ## Run linting
	cd $(SERVICE_DIR) && ruff check . && ruff format --check .

typecheck: ## Run type checking
	cd $(SERVICE_DIR) && pyright

migrate: ## Run database migrations
	cd $(SERVICE_DIR) && alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="description")
	cd $(SERVICE_DIR) && alembic revision --autogenerate -m "$(MSG)"

docker-up: ## Start all Docker services
	docker compose up -d --build

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## Show Docker logs
	docker compose logs -f

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
