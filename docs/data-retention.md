# Data Retention, Privacy & Right to Erasure Specification (Phase 20)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P20-RETENTION`  
**Date:** 2026-09-19  
**Status:** PRODUCTION READY  

---

## 1. Data Classification Matrix

To balance effective pedagogical personalization against storage constraints and user privacy, data collected by the agent is categorized into three tiers with explicit retention lifecycles.

| Data Category | Examples | Storage Location | Retention Policy | Rationale |
|---|---|---|---|---|
| **Tier A: Core Pedagogical Truth** | Band estimates, criterion scores, error taxonomies, FSRS review states, learning goals, target exam date. | PostgreSQL (`learners`, `skill_states`, `detected_errors`, `learning_items`) | **Indefinite** (or until user explicitly purges) | Essential for longitudinal adaptive planning and progress tracking. |
| **Tier B: Transient Media & Transcripts** | Raw Speaking `.ogg`/`.wav` voice recordings, verbatim Whisper alignment tokens. | `audio_storage/` / Local filesystem | **Configurable TTL (14 Days)** | Raw audio is needed only for initial acoustic analysis and short-term review. Discarded to save disk space. |
| **Tier C: Episodic Conversational Context** | Informal chit-chat, daily greetings, transient debugging output, tool execution traces. | SQLite (`state.db`), Honcho session logs | **Ephemeral (Auto-pruned / Summarized)** | Summarized into `MEMORY.md` milestones; verbatim message logs can be cleared with `/reset` without pedagogical loss. |

---

## 2. Right to Erasure & Data Purge Procedure (`/forget_me`)

In accordance with privacy best practices and user control principles (Spec v2 Section 28 & 46), the user can request complete or targeted data erasure.

### 2.1 Full Erasure (`purge_user_data.py --all`)
When requested:
1. Deletes all database records associated with the learner ID across `learners`, `attempts`, `assessment_results`, `detected_errors`, `learning_items`, and `study_events` via cascading foreign keys.
2. Removes all files in `audio_storage/`.
3. Resets `USER.md` and `MEMORY.md` to baseline clean templates.
4. Purges Honcho session memory for the user ID.

### 2.2 Automated Media Cleanup (`purge_user_data.py --cleanup-audio --days 14`)
A cron routine or system maintenance job executes weekly:
- Scans `audio_storage/` for files with `mtime > 14 days`.
- Removes obsolete audio assets while preserving the extracted acoustic metrics (`wpm`, `pause_count`, `articulation_rate`) in the `speech_metrics` database table.

---

## 3. Data Portability & Machine Migration

The user owns their data. The export process provides complete data portability:

```bash
# 1. Export complete state to timestamped portable archive
python infra/scripts/export_learner_memory.py --output-dir backups

# 2. Transfer archive to new host/environment
scp backups/learner_memory_export_*.zip user@new-machine:~/

# 3. Restore identity on target machine
python infra/scripts/import_learner_memory.py --archive learner_memory_export_*.zip --profile-dir ~/.hermes/profiles/ielts-tutor
```
