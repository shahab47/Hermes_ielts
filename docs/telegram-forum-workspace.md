# Telegram Forum Workspace & Topic Skill Architecture

**Specification:** `IELTS_Hermes_Antigravity_Master_Execution_Spec_v3.md` (Phases P3, P4)  
**Date:** 2026-09-19  
**Status:** Authoritative Forum Architecture & Configuration Specification  

---

## 1. Overview and Workspace Concept

The IELTS Hermes agent transforms Telegram into a structured, persistent learning workspace through **Telegram Forum Topics** (threads within a supergroup or direct multi-topic channel). 

Rather than mixing essay reviews, vocabulary flashcards, audio drills, and programming questions into a single chaotic stream, each domain operates within its dedicated topic.

---

## 2. Topic Directory & Skill Bindings

The workspace defines **12 authoritative topics** with dedicated context bindings:

| Topic Name | Primary Function / Skill Binding | Hermes Skill ID | Behavior & Fallback Principle |
|---|---|---|---|
| **`General`** | Freeform dialogue, general knowledge, project queries | *(None / Core assistant)* | Full general-purpose capability. No forced IELTS prompt. |
| **`Dashboard`** | High-level learner profile, target band status, streak | `ielts-diagnostic` | Displays overview stats without initiating practice drills. |
| **`Listening`** | Audio streaming, Section 1–4 drills, note completion | `ielts-listening` | Contextualizes listening cues; retains general assistant ability. |
| **`Reading`** | Academic passage ingestion, TFNG, headings, timed sets | `ielts-reading` | Tracks passage comprehension and reading speed. |
| **`Writing`** | Task 1 reports/diagrams & Task 2 argumentative essays | `ielts-writing` | Evaluates against official band rubrics with evidence quotes. |
| **`Speaking`** | Voice message drills, cue cards, fluency feedback | `ielts-speaking` | Ingests voice recordings; triggers transcript analysis. |
| **`Vocabulary`** | Academic Word List, collocations, lexical resource | `vocabulary` | Focuses on C1/C2 vocabulary enhancement and flashcards. |
| **`Grammar`** | Complex structures, error taxonomy, sentence rewriting | `grammar` | Targets chronic grammatical weaknesses and drills patterns. |
| **`Review`** | Spaced repetition queue (FSRS-6), mistake drills | `review` | Prioritizes due items based on memory stability and difficulty. |
| **`Mock Exams`**| Full timed exam simulations (Listening + Reading + Writing) | `ielts-mock` | Strict timing, multi-part sequence, comprehensive reporting. |
| **`Progress`**  | Longitudinal trends, band trajectory, weekly reviews | `ielts-core` | Analytical performance breakdowns and bottleneck analysis. |
| **`Coding`**    | Development, Linux administration, Python/JS queries | `hermes-cli` | Full coding agent capabilities (file read, patch, test runner). |

---

## 3. Zero-Keyword Gating Mandate

> [!IMPORTANT]
> **Topic binding is CONTEXT, not an artificial restriction.**  
> If the user asks a Python coding question or a general world knowledge question inside the `Writing` or `Listening` topic, Hermes **must answer the question normally and accurately**. The topic serves as a default skill hint and session organizer, NEVER as a restrictive keyword gate.

---

## 4. Hermes Telegram Gateway Configuration

To bind topics to skills in `C:\Users\shkh\AppData\Local\hermes\config.yaml`, the platform profile uses topic bindings:

```yaml
telegram:
  reactions: false
  require_mention: false
  allow_bots: all
  group_policy: open
  dm_policy: open
  allowed_chats: '96431023'
  topic_skills:
    "Listening": "ielts-listening"
    "Reading": "ielts-reading"
    "Writing": "ielts-writing"
    "Speaking": "ielts-speaking"
    "Vocabulary": "vocabulary"
    "Grammar": "grammar"
    "Review": "review"
    "Mock Exams": "ielts-mock"
    "Coding": "hermes-cli"
```

---

## 5. Security and Session Isolation

1. **Numeric Whitelist:** Only user ID `96431023` is permitted to trigger state-mutating actions or review personal learner profiles.
2. **Session Key Isolation:** When operating in forum mode, Hermes generates topic-isolated session keys (`<user_id>_<topic_id>`) to preserve clean conversational memory within each thread while sharing the canonical PostgreSQL database across all topics.
