# Dependency Matrix

This document provides the authoritative record of all software components, runtimes, libraries, databases, and infrastructure dependencies for the **IELTS Personal Learning Agent (`ielts-hermes`)**.

All dependencies have been compatibility-checked against the **Python 3.13** runtime baseline and **Ubuntu 24.04 LTS** target environment.

---

## 1. Master Dependency Table

| Dependency | Version Pin | Category | Python Compat | Verified | Notes |
|---|---|---|---|---|---|
| **Python** | `3.13.x` | Runtime | — | ✅ | Primary development and execution baseline |
| **Hermes Agent** | `0.21.3` | Agent Runtime | `>=3.11,<3.14` | ✅ | NousResearch; orchestrates Telegram, skills, MCP, and memory |
| **Honcho (`honcho-ai`)** | `2.4.0` | User Modeling SDK | `>=3.10` | ✅ | Plastic Labs client library for cognitive learner modeling |
| **Honcho Server** | `3.0.6` | User Modeling Server | — | ✅ | Self-hosted Docker container stack for user theory-of-mind |
| **fsrs (`py-fsrs`)** | `6.3.2` | Spaced Repetition | `>=3.10` | ✅ | FSRS-6 algorithm implementation (21 parameters) |
| **PostgreSQL** | `18.x` | Database | — | ✅ | Authoritative system of record for learner state and scoring |
| **pgvector** | `0.8.x` | Vector Extension | — | ✅ | In-database semantic vector search and content retrieval |
| **FastAPI** | latest stable (`>=0.115`) | Web Framework | `>=3.9` | ✅ | Learning service REST and MCP transport layer |
| **SQLAlchemy** | `2.x` (`>=2.0.35`) | ORM | `>=3.7` | ✅ | Async SQLAlchemy 2.0 with type-safe Mapped models |
| **Alembic** | latest stable (`>=1.13`) | Database Migrations | `>=3.8` | ✅ | Schema evolution and version tracking |
| **Pydantic** | `2.x` (`>=2.9`) | Data Validation | `>=3.8` | ✅ | V2 schema parsing, serialization, and settings management |
| **psycopg** | `3.x` (`>=3.2`, `psycopg[binary]`) | PostgreSQL Driver | `>=3.8` | ✅ | Native async driver for PostgreSQL 18 |
| **structlog** | latest stable (`>=24.4`) | Structured Logging | `>=3.8` | ✅ | Production JSON structured logging and audit trails |
| **httpx** | latest stable (`>=0.27`) | HTTP Client | `>=3.8` | ✅ | Async HTTP client for external service integration |
| **faster-whisper** | latest stable (`>=1.0`) | Speech-to-Text | `>=3.8` | ✅ | CTranslate2-accelerated local Whisper STT engine |
| **edge-tts** | latest stable (`>=6.1`) | Text-to-Speech | `>=3.8` | ✅ | High-quality, zero-cost British English voice synthesis |
| **pytest** | latest stable (`>=8.3`) | Test Framework | `>=3.8` | ✅ | Unit, integration, and regression testing harness |
| **pytest-asyncio** | latest stable (`>=0.24`) | Async Test Runner | `>=3.8` | ✅ | Async test support (`asyncio_mode = "auto"`) |
| **ruff** | latest stable (`>=0.6`) | Linter / Formatter | `>=3.7` | ✅ | Ultra-fast linter and code formatter |
| **pyright** | latest stable (`>=1.1`) | Static Type Checker | `>=3.8` | ✅ | Strict typing analysis compatible with modern Python 3.13 |
| **pre-commit** | latest stable (`>=3.8`) | Git Quality Hooks | `>=3.9` | ✅ | Automated commit validation and formatting enforcement |
| **Docker** | latest stable (`>=26.x`) | Container Runtime | — | ✅ | Containerization of PostgreSQL, Honcho, and services |
| **Docker Compose** | `v2` (`>=2.27`) | Orchestration | — | ✅ | Local and production multi-container orchestration |
| **Caddy** | latest stable (`>=2.8`) | Reverse Proxy | — | ✅ | Automatic HTTPS, TLS termination, and reverse proxying |
| **Ubuntu** | `24.04 LTS` | Target Operating System | — | ✅ | Deployment environment (Noble Numbat) |

---

## 2. Dependency Management & Tooling Policy

### 2.1 Package Manager: `uv`
- **Tool**: Astral's `uv` is the standard package and environment manager for this project.
- **Lockfile Integrity**: The project maintains a deterministic `uv.lock` file. All developer environments and CI/CD pipelines must install dependencies strictly via:
  ```bash
  uv sync --frozen
  ```
- **Virtual Environments**: Virtual environments are managed automatically by `uv` within `.venv/`.

### 2.2 Version Pinning Strategy
1. **Critical Domain & Protocol Libraries**: Fixed to exact minor/patch versions (`==X.Y.Z`) to guarantee zero behavioral drift:
   - `hermes-agent == 0.21.3`
   - `honcho-ai == 2.4.0`
   - `py-fsrs == 6.3.2`
2. **Infrastructure Engines**: Pinned to major/minor versions:
   - `postgres:18-bookworm` (with `pgvector 0.8.x`)
   - `caddy:2-alpine`
3. **General Web & Development Libraries**: Pinned using semantic upper bounds (`~=`, `>=X.Y, <X.(Y+1)` or major pins `2.x`) to allow non-breaking security patches while preventing breaking API changes.

---

## 3. Subsystem Breakdown

### 3.1 Core Learning Service (`apps/learning-service`)
- **FastAPI + Pydantic v2**: High-performance asynchronous API endpoints and strict schema validation for MCP tools.
- **SQLAlchemy 2.0 (Async) + psycopg 3**: Asynchronous relational operations, connection pooling, and JSONB mapping.
- **Alembic**: Managed declarative schema migrations for PostgreSQL 18.
- **`py-fsrs` 6.3.2**: Algorithmic calculation of review intervals for vocabulary and grammar micro-skills.
- **`structlog`**: Contextual logging attaching `learner_id`, `session_id`, and `request_id` to every log event.

### 3.2 Agent & User Modeling (`hermes/` and external stack)
- **Hermes Agent (v0.21.3)**:
  - Manages Telegram gateway communication (text, voice audio, attachments).
  - Triggers scheduled learning routines via Hermes Cron.
  - Interfaces with the learning service via Model Context Protocol (MCP).
- **Honcho (v2.4.0 SDK / v3.0.6 Server)**:
  - Hosts cross-session conversational memory and Theory-of-Mind (ToM) modeling.
  - Maintains learner dialectic representations independently of PostgreSQL factual tables.

### 3.3 Audio & Speech Subsystem
- **`faster-whisper`**:
  - Operates locally without external cloud API calls.
  - Optimized via CTranslate2 CPU INT8 quantization or CUDA when available.
  - Language hint: `en`.
- **`edge-tts`**:
  - Generates clear British English voice audio for Telegram voice bubbles (e.g., `en-GB-SoniaNeural` or `en-GB-RyanNeural`).

### 3.4 Quality Assurance & Tooling
- **`ruff`**: Code formatting and linting (replaces Black, Flake8, and isort).
- **`pyright`**: Strict type checking enforcing Python 3.13 type hinting (`typing` enhancements, PEP 695 type parameter syntax).
- **`pytest` & `pytest-asyncio`**: Asynchronous test execution with isolated test databases.
- **`pre-commit`**: Client-side enforcement preventing formatting defects and unmigrated schema drifts from reaching git.
