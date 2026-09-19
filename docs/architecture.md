# IELTS Personal Learning Agent — Architecture Overview

> Version: 1.0 | Date: 2026-09-19 | Phase: 0 — Discovery & Architecture

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TELEGRAM USER                               │
│                    (Single authorized user)                          │
│              Text │ Voice │ Files │ Scheduled msgs                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ Long-polling (no webhooks)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      HERMES AGENT v0.21.3                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │ Telegram │  │  Skills  │  │   Cron   │  │   Voice Pipeline  │   │
│  │ Gateway  │  │  System  │  │  Engine  │  │ STT: faster-whisper│   │
│  │          │  │ SKILL.md │  │          │  │ TTS: Edge TTS     │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────────┘   │
│  ┌──────────────────┐  ┌──────────────────────────────────────────┐ │
│  │  Built-in Memory │  │           MCP Client                     │ │
│  │  SOUL.md (persona)│  │  (Model Context Protocol)               │ │
│  │  USER.md (profile)│  │                                         │ │
│  │  MEMORY.md (facts)│  │                                         │ │
│  └──────────────────┘  └────────────────┬─────────────────────────┘ │
│           │                              │                          │
│           ▼                              ▼                          │
│  ┌──────────────────┐     ┌──────────────────────────────────────┐  │
│  │    Honcho v3     │     │      MCP Tool Calls (typed)          │  │
│  │  (memory plugin) │     │  get_learner_profile, save_assessment │  │
│  │  Peer Cards      │     │  get_due_reviews, submit_review       │  │
│  │  Theory-of-Mind  │     │  generate_daily_plan, search_content  │  │
│  └────────┬─────────┘     └────────────────┬─────────────────────┘  │
└───────────┼────────────────────────────────┼────────────────────────┘
            │                                │
            ▼                                ▼
┌───────────────────────┐   ┌─────────────────────────────────────────┐
│   HONCHO SERVER v3    │   │         LEARNING SERVICE (FastAPI)       │
│  ┌─────────────────┐  │   │  ┌───────────────────────────────────┐  │
│  │   API Server    │  │   │  │         MCP Server                │  │
│  │   (port 8000)   │  │   │  │    (stdio / HTTP transport)       │  │
│  ├─────────────────┤  │   │  ├───────────────────────────────────┤  │
│  │    Deriver      │  │   │  │       Domain Services             │  │
│  │   (async worker)│  │   │  │  ┌─────────┐  ┌──────────────┐   │  │
│  ├─────────────────┤  │   │  │  │ Assessor │  │ Error Tracker│   │  │
│  │    Dreamer      │  │   │  │  ├─────────┤  ├──────────────┤   │  │
│  │  (consolidator) │  │   │  │  │ Planner  │  │ Weakness Eng.│   │  │
│  ├─────────────────┤  │   │  │  ├─────────┤  ├──────────────┤   │  │
│  │  PostgreSQL     │  │   │  │  │FSRS Sched│  │ Content/RAG  │   │  │
│  │  + pgvector     │  │   │  │  └─────────┘  └──────────────┘   │  │
│  ├─────────────────┤  │   │  ├───────────────────────────────────┤  │
│  │  Redis (internal│  │   │  │     Internal HTTP API              │  │
│  │   queue only)   │  │   │  │  /health  /admin  /metrics         │  │
│  └─────────────────┘  │   │  └───────────────┬───────────────────┘  │
└───────────────────────┘   └──────────────────┼──────────────────────┘
                                               │
                                               ▼
                            ┌──────────────────────────────────────────┐
                            │      POSTGRESQL 18 + pgvector 0.8.x     │
                            │                                          │
                            │  ┌────────────────────────────────────┐  │
                            │  │ Learner Data (source of truth)     │  │
                            │  │  • learner, skill_state, attempt   │  │
                            │  │  • assessment, criterion_score     │  │
                            │  │  • error_event, weakness           │  │
                            │  │  • learning_item, review_event     │  │
                            │  │  • practice_session, recommendation│  │
                            │  │  • audio_asset, learner_event      │  │
                            │  ├────────────────────────────────────┤  │
                            │  │ Vector Store (pgvector)            │  │
                            │  │  • Content embeddings              │  │
                            │  │  • Rubric embeddings               │  │
                            │  │  • Exercise embeddings             │  │
                            │  ├────────────────────────────────────┤  │
                            │  │ FSRS State                         │  │
                            │  │  • fsrs_state_json per item        │  │
                            │  │  • Indexed query fields            │  │
                            │  └────────────────────────────────────┘  │
                            └──────────────────────────────────────────┘
```

---

## Responsibility Separation

| Component | Responsibility | NOT Responsible For |
|-----------|---------------|---------------------|
| **Hermes Agent** | Orchestration, conversation, skills, cron, voice I/O | Scoring, data storage, scheduling logic |
| **Honcho** | Cross-session user modeling, Theory-of-Mind, peer cards | Scores, attempts, FSRS state |
| **PostgreSQL** | Source of truth: scores, attempts, errors, mastery, scheduling | Conversation history, persona |
| **pgvector** | Semantic retrieval of content/rubrics | Primary scoring criteria storage |
| **FSRS** | Retention scheduling for vocabulary/grammar micro-skills | Full IELTS task planning |
| **Skills** | Pedagogy procedures, assessment workflows | Data persistence |
| **MCP** | Integration boundary (typed tool calls) | Business logic |
| **Telegram** | User interface (text, voice, files) | Data processing |
| **Speech Pipeline** | Audio evidence (transcript, metrics) | Pronunciation scoring from text alone |

---

## Core Learning Loop

```
OBSERVE → EVALUATE → CLASSIFY → STORE → PRIORITIZE → PRACTICE → REASSESS → UPDATE
   │          │          │         │          │            │           │          │
   │     LLM + Skills   │    PostgreSQL   Deterministic  Skills    LLM +      PostgreSQL
   │     + Rubrics    Taxonomy    │        Priority     + MCP    Evidence       │
Telegram              Engine      │        Formula       │       Engine        │
Voice/Text                        │                      │                     │
                                  └──────────────────────┘                     │
                                        FSRS for review items ─────────────────┘
```

---

## Data Flow: Writing Assessment Example

```
1. User sends Writing Task 2 via Telegram
2. Hermes receives text → activates ielts-writing-task2 skill
3. Skill calls MCP: create_attempt(skill="writing", task_type="task2", raw_input=...)
4. Skill performs assessment using LLM + official rubric
5. Skill calls MCP: save_assessment(criteria_scores, evidence, confidence)
6. Skill calls MCP: record_error_events(errors with category/subtype/severity)
7. Learning Service: aggregates errors → updates weaknesses → computes priority
8. Skill calls MCP: update_weakness_state()
9. Hermes sends feedback to user via Telegram
10. Hermes cron schedules follow-up practice based on weakness priority
```

---

## Four Distinct Data Stores

| Store | Technology | Purpose | Example Data |
|-------|-----------|---------|-------------|
| **Tutor Memory** | Hermes SOUL.md/USER.md/MEMORY.md + Honcho | Preferences, tendencies, strategy | "Prefers Farsi explanations" |
| **Learner Database** | PostgreSQL | Quantitative learning data | Scores, attempts, FSRS state |
| **Content Store** | PostgreSQL + pgvector | Teaching resources | Rubrics, exercises, embeddings |
| **Conversation History** | Hermes state.db | Session transcripts | Chat messages |

> **These four stores have different purposes and must not be merged.**

---

## Deployment Architecture (Production Target)

```
┌─────────────────────────────────────────────┐
│           Ubuntu 24.04 LTS VPS              │
│                                              │
│  ┌────────────────────────────┐              │
│  │        Caddy (HTTPS)       │ ← Port 443  │
│  └─────────────┬──────────────┘              │
│                │                             │
│  ┌─────────────────────────────────────────┐ │
│  │         Docker Compose                  │ │
│  │  ┌──────────┐  ┌──────────────────────┐ │ │
│  │  │ postgres │  │  learning-service    │ │ │
│  │  │  :5432   │  │  (FastAPI + MCP)     │ │ │
│  │  └──────────┘  └──────────────────────┘ │ │
│  │  ┌──────────────────────────────────┐   │ │
│  │  │        honcho (API + workers)    │   │ │
│  │  │  ┌────────┐  ┌───────────────┐   │   │ │
│  │  │  │ redis  │  │ postgres-honcho│   │   │ │
│  │  │  └────────┘  └───────────────┘   │   │ │
│  │  └──────────────────────────────────┘   │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌─────────────────────────────────────────┐ │
│  │  Hermes Agent (systemd / host process)  │ │
│  │  Profile: ielts-tutor                   │ │
│  │  Gateway: Telegram (long-polling)       │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────┐                      │
│  │ Encrypted Backups  │ → Offsite storage    │
│  └────────────────────┘                      │
└──────────────────────────────────────────────┘
```

---

## Related Documents

- [Hermes Compatibility Report](hermes-compatibility.md)
- [Dependency Matrix](dependency-matrix.md)
- [Risk Register](risk-register.md)
- [Phase 1 Checklist](p1-checklist.md)
- Architecture Decision Records: [docs/adr/](adr/)
