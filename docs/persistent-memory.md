# Persistent Memory Architecture & Portability Specification (Phase 4)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P4-MEMORY`  
**Date:** 2026-09-19  
**Status:** ACTIVE & VERIFIED  

---

## 1. Memory Tier Separation Policy

To ensure robust personalization without context window exhaustion or data corruption, the system enforces a strict three-tier memory architecture.

```text
+-------------------------------------------------------------------------+
| Tier 1: Built-in Hermes Memory (Profile Local Files)                   |
| Location: ~/.hermes/profiles/ielts-tutor/ (USER.md, MEMORY.md)          |
| Injected into agent system prompt on every turn.                        |
| Role: Name, communication preferences, target score, active priorities. |
| Size limit: 2,200 chars (~800 tokens).                                  |
+-------------------------------------------------------------------------+
                                   |
                                   v
+-------------------------------------------------------------------------+
| Tier 2: Cognitive Theory-of-Mind Modeling (Honcho Service)              |
| Interface: Native Honcho Memory Provider / REST API                     |
| Role: Multi-session conversational context, psychological trajectory,  |
| cognitive fatigue signals, motivation patterns, behavioral tendencies.  |
+-------------------------------------------------------------------------+
                                   |
                                   v
+-------------------------------------------------------------------------+
| Tier 3: Authoritative Learner Ground Truth (PostgreSQL 18 + pgvector)   |
| Interface: FastMCP Tools (apps/learning-service)                        |
| Role: Exact attempt submissions, Task 1/2 scores, criterion breakdowns, |
| FSRS-6 item stability & review intervals, error recurrence taxonomies.  |
| Storage: Relational tables + embeddings, fully ACID compliant.         |
+-------------------------------------------------------------------------+
```

---

## 2. Permitted & Prohibited Storage Rules

### Tier 1: Built-in Memory (`USER.md` and `MEMORY.md`)
- **Permitted:**
  - Learner's preferred name or title.
  - Native language (Farsi) and primary reason for taking IELTS (immigration, academic admission).
  - Target band score (e.g. Overall 7.5, minimum 7.0 in Writing).
  - Target examination date or preparation horizon.
  - Active high-priority bottleneck (e.g., "Overusing 'furthermore' and run-on sentences in Task 2").
- **Strictly Prohibited:**
  - Full essay attempt text or audio transcripts.
  - Historical score tables or statistical aggregations.
  - Detailed error catalogs or full vocabulary review lists.
  - Any private secrets, API keys, or raw authentication tokens.

### Tier 2: Cognitive Modeling (Honcho)
- **Permitted:**
  - Session conclusion insights and cognitive fatigue markers.
  - Observed learning velocity and resilience patterns.
  - Conceptual associations across sessions.
- **Strictly Prohibited:**
  - Primary source of truth for band scores or FSRS flashcard review schedules.

### Tier 3: Authoritative Database (PostgreSQL 18)
- **Authoritative Storage:**
  - `learners` (target band, current estimated band, baseline date)
  - `tasks` (Task 1 prompts, Task 2 topics, Speaking cue cards)
  - `attempts` (submission text, audio metadata, total duration)
  - `assessment_results` (diagnostic band, TR/TA, CC, LR, GRA, evidence JSON)
  - `detected_errors` (taxonomy category, excerpt, correction, recurrence count)
  - `learning_items` (vocabulary, grammar patterns, FSRS stability, difficulty, due date)
  - `study_events` (event timestamps, event type, metadata)

---

## 3. Portability & Disaster Recovery Procedure

The ultimate measure of memory durability is machine portability:

$$\text{New Machine} + \text{New Hermes Install} + \text{Restored DB} + \text{Restored Honcho} + \text{Restored Profile} = \text{Identical Learner Identity}$$

### 3.1 Automated Backup / Export (`infra/scripts/export_learner_memory.py`)
Exports:
1. Complete PostgreSQL database dump (`pg_dump` format and JSON export).
2. Profile files: `SOUL.md`, `USER.md`, `MEMORY.md`, and `config.yaml`.
3. Honcho user session metadata.
4. Generates an encrypted/compressed `.tar.gz` archive in `backups/`.

### 3.2 Automated Restore / Import (`infra/scripts/import_learner_memory.py`)
Restores:
1. Restores PostgreSQL database state and applies any pending Alembic migrations.
2. Deploys `USER.md` and `MEMORY.md` into `~/.hermes/profiles/ielts-tutor/`.
3. Reconnects Hermes profile to the database and Honcho.
4. Executes verification health-check to ensure learner continuity.
