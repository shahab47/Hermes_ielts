# IELTS Learning Service

The `learning-service` is the authoritative domain backend for the IELTS Personal Learning Agent. It exposes Model Context Protocol (MCP) tools to Hermes and provides internal HTTP endpoints for diagnostic analysis, curriculum planning, retention scheduling, and persistence.

---

## Directory Layout

- `app/api/`: FastAPI route handlers (health, internal admin, diagnostics, metrics).
- `app/domain/`: Core business models, entities, and validation invariants.
- `app/services/`: Application services orchestrating domain workflows.
- `app/repositories/`: SQLAlchemy 2.x persistence layers interfacing with PostgreSQL 18.
- `app/models/`: SQLAlchemy ORM database models.
- `app/schemas/`: Pydantic 2.x request/response models and transfer objects.
- `app/analyzers/`: IELTS diagnostic rubrics, text analysis, and error classification.
- `app/planner/`: Diagnostic-driven curriculum and study plan generation.
- `app/fsrs/`: FSRS-6 algorithm wrapper for micro-skill retention scheduling.
- `app/content/`: Question bank and RAG content management.
- `app/mcp/`: MCP server implementation exposing tools to Hermes Agent.
- `tests/`: Automated unit and integration test suites.
- `alembic/`: Database migration scripts.

---

## Development Setup

```bash
uv sync --all-extras
uvicorn app.main:app --reload --port 8000
```
