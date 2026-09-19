# IELTS Personal Learning Agent — Hermes + Telegram

Personal, longitudinal IELTS Academic learning companion powered by NousResearch Hermes Agent and Telegram. It acts as an adaptive learning tutor that continuously diagnoses strengths and weaknesses, schedules targeted micro-skill retention via FSRS, and prepares learners across all four IELTS modules (Writing, Speaking, Reading, Listening).

> [!NOTE]
> IELTS scoring produced by this system is diagnostic and formative. The scoring authority is grounded in official IELTS public band descriptors, not certified institutional score reports.

---

## Architecture Overview

```mermaid
flowchart LR
    User([Telegram User]) <-->|Text / Voice| Hermes[Hermes Agent Gateway]
    Hermes <-->|MCP Protocol| LearningService[Learning Service (FastAPI)]
    LearningService <-->|SQLAlchemy 2.x| Postgres[(PostgreSQL 18 + pgvector)]
    LearningService <-->|Retention Engine| FSRS[FSRS-6 Scheduler]
    Hermes <-->|User Modeling| Honcho[Honcho Service]
```

### Architectural Principles
- **Hermes Agent** handles conversation orchestration, agentic reasoning, voice ingestion (via `faster-whisper`), TTS (via `Edge TTS`), and Telegram messaging.
- **MCP (Model Context Protocol)** serves as the strict integration boundary exposing typed domain tools to Hermes.
- **Learning Service (FastAPI)** encapsulates domain logic: diagnostic analyzers, curriculum planning, retention scheduling, and evaluation.
- **PostgreSQL 18 + pgvector** is the authoritative source of truth for all learner attempts, rubric scores, error taxonomy, item banks, and vector retrieval.
- **Honcho** manages cross-session user modeling and theory-of-mind cognitive profiling.
- **FSRS-6** governs spaced repetition scheduling for atomic vocabulary and grammar micro-skills.

---

## Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Orchestration Agent** | NousResearch Hermes Agent (`v0.21.3`) | Telegram bot gateway, voice I/O, MCP client |
| **User Modeling** | Honcho (`v3.0.6`) | Long-term memory & cognitive user representation |
| **Backend Service** | Python 3.13, FastAPI | Core learning API and MCP server |
| **Database & Search** | PostgreSQL 18, pgvector 0.8.x | Authoritative learner state, curriculum items, RAG embeddings |
| **Spaced Repetition** | FSRS v6.3.2 (`py-fsrs`) | 21-parameter modern SRS scheduling |
| **Speech Processing** | faster-whisper & Edge TTS | Native voice message transcription and UK English speech synthesis |
| **Infrastructure** | Docker Compose, Caddy, systemd | Self-hosted deployment on Ubuntu 24.04 LTS |
| **Code Quality** | Ruff, Pyright, Pytest | Formatting, strict typing, and automated testing |

---

## Project Status

**Current Status:** `Phase 0 — Discovery & Architecture`

- [x] Repository scaffolding & workspace setup
- [ ] Technology compatibility lock & Hermes baseline verification
- [ ] Architecture Decision Records (ADRs)
- [ ] Phase 1: Core Domain & Data Foundations

---

## Quick Links to Documentation

- [Architecture Overview](file:///d:/00-VibeCoding/English/ielts-hermes/docs/architecture.md)
- [Architecture Decision Records (ADR)](file:///d:/00-VibeCoding/English/ielts-hermes/docs/adr/)
- [Setup & Development Guide](file:///d:/00-VibeCoding/English/ielts-hermes/docs/setup.md)
- [Operations & Deployment Runbooks](file:///d:/00-VibeCoding/English/ielts-hermes/docs/runbooks/)

---

## License

TBD
