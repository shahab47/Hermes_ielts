# Phase 1 Readiness Checklist

This document defines the acceptance criteria and verification commands required to validate **Phase 1: Repository Bootstrap and Local Infrastructure** for the **IELTS Personal Learning Agent (`ielts-hermes`)**.

Phase 1 establishes the local developer foundation, core backend skeleton, containerized infrastructure, database layer, quality gates, and automated test pipelines prior to implementing agent integrations in Phase 2.

---

## 1. Environment & Tooling Readiness

- [ ] **Python 3.13 installed and verified**
  - *Verification*: `python --version` outputs `Python 3.13.x`.
  - *Acceptance*: Development baseline matches Python 3.13 across local environments and Docker runtimes.

- [ ] **uv package manager installed**
  - *Verification*: `uv --version` outputs `uv >= 0.4.x`.
  - *Acceptance*: `uv` is available on the system PATH and configured for deterministic dependency resolution.

- [ ] **Docker and Docker Compose installed**
  - *Verification*: `docker --version` and `docker compose version` execute without errors.
  - *Acceptance*: Docker daemon is responsive; Docker Compose v2 is active.

---

## 2. Dependencies & Code Quality Framework

- [ ] **Project dependencies installable with uv**
  - *Verification*: `uv sync --frozen` installs all packages from `pyproject.toml` and `uv.lock` without resolution errors.
  - *Acceptance*: Clean virtual environment is populated with verified pins from the Dependency Matrix.

- [ ] **pre-commit hooks configured**
  - *Verification*: `uv run pre-commit run --all-files` runs clean.
  - *Acceptance*: Hooks configured for whitespace cleanup, end-of-file formatting, Ruff linting, and secret checks.

- [ ] **Ruff configuration verified**
  - *Verification*: `uv run ruff check .` and `uv run ruff format --check .` exit with status code 0.
  - *Acceptance*: Pyproject configuration enforces modern Python 3.13 conventions and standard line lengths.

- [ ] **pyright configuration verified**
  - *Verification*: `uv run pyright` reports 0 errors.
  - *Acceptance*: Strict type-checking configured in `pyrightconfig.json` or `pyproject.toml` without stub warnings.

- [ ] **pytest runs successfully (even with 0 tests)**
  - *Verification*: `uv run pytest` executes and passes cleanly.
  - *Acceptance*: Test runner discovers tests and exits 0.

- [ ] **pytest-asyncio configured**
  - *Verification*: Async test cases decorated or configured with `asyncio_mode = "auto"` pass without event loop errors.
  - *Acceptance*: Asynchronous database and API fixture support validated.

- [ ] **structlog configured for JSON output**
  - *Verification*: Application startup emits structured JSON log entries containing `timestamp`, `level`, `event`, and context fields.
  - *Acceptance*: No plain unformatted stdout print statements in application modules.

---

## 3. Container & Database Infrastructure

- [ ] **PostgreSQL 18 Docker image pulled and tested**
  - *Verification*: `docker compose up -d postgres` pulls and starts the PostgreSQL 18 container.
  - *Acceptance*: Server accepts SQL connections on port 5432.

- [ ] **pgvector extension verified in Docker image**
  - *Verification*: `docker compose exec postgres psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname='vector';"`
  - *Acceptance*: Returns `pgvector 0.8.x`.

- [ ] **Docker Compose services defined (`postgres`, `learning-service`)**
  - *Verification*: `docker compose config` validates schema syntax for both services without errors.
  - *Acceptance*: Correct network isolation, volume persistence, and environment variable bindings.

- [ ] **Docker healthchecks defined**
  - *Verification*: `docker compose ps` displays `(healthy)` status for all running services after initialization.
  - *Acceptance*: Healthcheck probes defined for PostgreSQL (`pg_isready`) and the Learning Service (`/health`).

---

## 4. Application Skeleton & Persistence

- [ ] **`.env.example` complete with all required variables**
  - *Verification*: File contains templates for `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `HONCHO_URL`, `LOG_LEVEL`, and Telegram/Hermes tokens.
  - *Acceptance*: New developer can copy `.env.example` to `.env` and immediately boot the stack.

- [ ] **Alembic initialized and configured**
  - *Verification*: `alembic.ini` and `apps/learning-service/alembic/` configured to use async SQLAlchemy connection strings.
  - *Acceptance*: Migrations load models from `apps.learning_service.app.models`.

- [ ] **Initial migration creates empty schema**
  - *Verification*: `uv run alembic upgrade head` executes against a fresh database container without errors.
  - *Acceptance*: `alembic_version` table is initialized and reflects the baseline revision.

- [ ] **FastAPI app starts and serves `/health` endpoint**
  - *Verification*: `curl -s http://localhost:8000/health` returns `{"status": "healthy", "database": "connected"}`.
  - *Acceptance*: App initializes lifespan context, verifies database connectivity, and terminates cleanly.

---

## 5. Automation, Build & Repository Gates

- [ ] **CI workflow file created (`.github/workflows/ci.yml`)**
  - *Verification*: Workflow YAML triggers on pull requests and pushes to `main`.
  - *Acceptance*: Executes Ruff, Pyright, Alembic migration verification, and Pytest suites in automated runners.

- [ ] **Makefile targets all functional**
  - *Verification*: Run and verify `make help`, `make install`, `make lint`, `make typecheck`, `make test`, `make up`, and `make down`.
  - *Acceptance*: All targets execute corresponding `uv` or `docker compose` commands without manual intervention.

- [ ] **README setup instructions work on clean clone**
  - *Verification*: Follow instructions in a fresh working copy from clone to passing `/health` endpoint.
  - *Acceptance*: Zero undocumented steps or hidden environment prerequisites.

- [ ] **All Phase 0 deliverables committed**
  - *Verification*: Repository contains `docs/hermes-compatibility.md`, ADRs 001–009, `docs/dependency-matrix.md`, and `docs/risk-register.md`.
  - *Acceptance*: Architecture decisions and compatibility constraints formally locked.
