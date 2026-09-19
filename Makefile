.DEFAULT_GOAL := help

.PHONY: help setup dev test lint typecheck migrate docker-up docker-down clean

help: ## Show available commands
	@echo "IELTS Personal Learning Agent — Hermes"
	@echo "Available make targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies for learning-service and environment
	@echo "Setting up development environment..."
	cd apps/learning-service && uv sync --all-extras || pip install -e ".[dev]"

dev: ## Start development environment (FastAPI service with hot reload)
	@echo "Starting development server..."
	cd apps/learning-service && uvicorn app.main:app --reload --port 8000

test: ## Run test suite
	@echo "Running tests..."
	cd apps/learning-service && pytest

lint: ## Run linting and style checks
	@echo "Running Ruff linter and formatter checks..."
	cd apps/learning-service && ruff check . && ruff format --check .

typecheck: ## Run type checking with pyright
	@echo "Running type checking..."
	cd apps/learning-service && pyright

migrate: ## Run database migrations via Alembic
	@echo "Applying database migrations..."
	cd apps/learning-service && alembic upgrade head

docker-up: ## Start Docker services (PostgreSQL, pgvector, Honcho)
	@echo "Starting Docker services..."
	docker compose up -d

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	docker compose down

clean: ## Clean temporary files and build artifacts
	@echo "Cleaning cache and build artifacts..."
	rm -rf apps/learning-service/.pytest_cache
	rm -rf apps/learning-service/.ruff_cache
	rm -rf apps/learning-service/.mypy_cache
	rm -rf apps/learning-service/htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
