# Gap Analysis & Remediation Roadmap (Phase 0 -> Spec v2)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P0-GAP-ANALYSIS`  
**Date:** 2026-09-19  
**Status:** ACTIVE  
**Reference Specification:** `IELTS_Hermes_Antigravity_Master_Execution_Spec_v2.md`  

---

## 1. Executive Summary

This Gap Analysis compares the state of the `ielts-hermes` repository against the complete 30-phase roadmap articulated in **Master Execution Specification v2**.

While the foundational Python backend, domain models, IELTS scoring algorithms, and 14 Hermes skill packages are implemented and pass all 38 automated tests with 84% coverage, critical production requirements—specifically dual-persona behavioral isolation, single-user security locks, privacy export/erasure, specialized regression suites (general assistant, coding agent, memory), deployment systemd units, and disaster recovery—remain to be fully implemented and verified.

---

## 2. Phase-by-Phase Matrix (Phases 0 to 30)

| Phase | Spec Title | Current Implementation State | Gap / Missing Elements | Target Phase Action |
|---|---|---|---|---|
| **P0** | Current-State Audit | **VERIFIED & COMPLETE** | None. Audit completed, Hermes v0.21.0 locked, 38 tests verified. | Close P0. |
| **P1** | Bootstrap Hardening | **PARTIALLY IMPLEMENTED** | Pinned deps exist; need pre-commit config, gitignore audit, CI workflow alignment. | Harden configs, lock files, pre-commit. |
| **P2** | Hermes Foundation & Profile | **IMPLEMENTED** | Base profile exists in `profiles/ielts-tutor/`; needs formal verification of isolation. | Verify config.yaml with Hermes v0.21.0 keys. |
| **P3** | Telegram Gateway | **CONFIGURED** | Config template exists; needs single-user Telegram ID whitelist enforcement. | Harden Telegram authorization filter. |
| **P4** | Persistent Memory | **PARTIALLY IMPLEMENTED** | Honcho service in docker-compose; need explicit policy boundary doc & tests. | Formalize Honcho vs DB vs built-in memory rules. |
| **P5** | Database Domain | **VERIFIED & COMPLETE** | 8 domain tables, Alembic migration `0001_initial_schema.py`, pgvector. | Add repository integration tests. |
| **P6** | Learner State Engine | **VERIFIED & COMPLETE** | Error aggregator, trend calculator, priority scorer, weakness service. | Maintain & verify with real DB fixtures. |
| **P7** | IELTS Assessment Engine | **VERIFIED & COMPLETE** | Writing verifiers (Task 1 & 2, 1/3 & 2/3 weight), bottleneck detector, rubrics. | Add benchmark calibration tests. |
| **P8** | IELTS Skill System | **VERIFIED & COMPLETE** | 14 skill directories with SKILL.md, references, and templates. | Verify skill auto-loading in Hermes CLI. |
| **P9** | MCP Learning Service | **VERIFIED & COMPLETE** | FastMCP server, 25 typed tools across all domains. | Test MCP tool connection via `hermes mcp test`. |
| **P10** | Content & RAG | **PARTIALLY IMPLEMENTED** | 5 seed datasets present; hybrid retriever implemented but lacks integration tests. | Add retriever unit/integration tests with DB. |
| **P11** | Vocabulary System + FSRS | **VERIFIED & COMPLETE** | FSRS-6 adapter, vocabulary filter, interval calculation tested. | Maintain test coverage. |
| **P12** | Grammar Mastery System | **VERIFIED & COMPLETE** | Error taxonomy v1, pattern analyzer, feedback generation. | Maintain test coverage. |
| **P13** | Speech Pipeline | **PARTIALLY IMPLEMENTED** | Speech metrics analyzer implemented; audio storage & faster-whisper pipeline integration. | Add audio file retention & transcription tests. |
| **P14** | Adaptive Planner | **VERIFIED & COMPLETE** | Daily study plan generator, weakness-targeted scheduling. | Verify dynamic plan adjustments. |
| **P15** | Daily & Weekly Routines | **PARTIALLY IMPLEMENTED** | Cron prompt templates created; Hermes cron scheduling commands need runbooks. | Create automated cron setup script. |
| **P16** | Onboarding & Diagnostic | **VERIFIED & COMPLETE** | `/diagnostic/onboard` API, baseline test logic, adaptive initial plan. | Verify end-to-end user onboarding flow. |
| **P17** | Tutor Identity & Behavior | **PARTIALLY IMPLEMENTED** | `SOUL.md` exists; needs dual-persona anti-hallucination rules and general assistant balance. | Update `SOUL.md` per Spec v2 Sec 1 & 47. |
| **P18** | Observability | **VERIFIED & COMPLETE** | Structured JSON logging, `ObservabilityMiddleware`, X-Request-ID tracking. | Verify metrics export. |
| **P19** | Security | **MISSING** | Telegram user ID whitelist enforcement, secret masking, env token validation. | Implement Telegram security middleware / lock. |
| **P20** | Data Retention & Privacy | **MISSING** | Data export (`/export_data`), data erasure (`/forget_me`), audio retention TTL. | Implement GDPR-compliant export & purge tools. |
| **P21** | General Assistant Regression | **MISSING** | Automated regression suite verifying non-IELTS questions (coding, Linux, general knowledge). | Build automated regression test suite for general tasks. |
| **P22** | Coding Agent Regression | **MISSING** | Test suite verifying repository inspection, patching, terminal execution. | Build automated coding agent test suite. |
| **P23** | Memory Regression | **MISSING** | Test suite verifying cross-session memory retention without Git pollution. | Build cross-session continuity tests. |
| **P24** | Evaluation & Benchmarking | **PARTIALLY IMPLEMENTED** | Synthetic benchmark suite stub exists; needs gold-standard essay calibration. | Run benchmark calibration against IELTS band standards. |
| **P25** | Hardened Testing | **PARTIALLY IMPLEMENTED** | 38 unit tests (84% cov); needs integration tests covering DB repositories and retriever. | Increase coverage to >=90% with test DB fixtures. |
| **P26** | Deployment | **MISSING** | Systemd service files, Caddy reverse proxy config, production environment config. | Author systemd units and Caddyfile. |
| **P27** | Disaster Recovery | **MISSING** | Automated DB backup script, restore verification procedure, runbook. | Author backup script and restore drill test. |
| **P28** | Production Release Gate | **PENDING** | Formal gate checklist verifying all 30 phases before production sign-off. | Execute release gate audit. |
| **P29** | Post-MVP Enhancements | **FUTURE** | Multi-device sync, analytics dashboard export. | Document roadmap. |
| **P30** | Future Intelligence Layer | **FUTURE** | Multi-agent debate evaluation, synthetic conversational partner. | Document roadmap. |

---

## 3. High-Priority Remediation Plan

To execute Spec v2 systematically, work will proceed strictly in phase order:

1. **Phase 1 (Bootstrap Hardening):** Verify environment, clean pre-commit hooks, verify `.gitignore`, normalize tooling.
2. **Phase 2–4 (Hermes Profile, Telegram & Memory):** Validate profile configuration against Hermes v0.21.0, configure Telegram single-user whitelist, establish memory boundary.
3. **Phase 10 & 13 (Content & Speech Hardening):** Add tests for content retriever and audio lifecycle management.
4. **Phase 17 (Tutor Identity & Dual Persona):** Update `SOUL.md` to prevent IELTS mode hijacking on general queries.
5. **Phase 19 & 20 (Security & Privacy):** Implement single-user Telegram ID verification, data export, data deletion, and audio cleanup scripts.
6. **Phase 21–23 (Regression Suites):** Implement rigorous tests for general assistant mode, coding capabilities, and memory retention.
7. **Phase 24–25 (Benchmarking & Hardened Tests):** Benchmark assessment algorithms and raise overall code coverage above 90%.
8. **Phase 26–28 (Deployment, DR & Production Gate):** Generate systemd services, Caddy reverse proxy, automated backup/restore scripts, and complete release gate sign-off.
