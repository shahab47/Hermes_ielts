# Open-Source Content Discovery & Import Decisions

**Specification:** `IELTS_Hermes_Antigravity_Master_Execution_Spec_v3.md` (Phase P13)  
**Date:** 2026-09-19  
**Status:** Canonical Source Evaluation Matrix  

---

## 1. Decision Contract

Each evaluated learning repository or dataset must receive an unambiguous determination:
- **`IMPORT`**: Reusable code or open-licensed content directly integrated into the project.
- **`REFERENCE ONLY`**: Architecture, algorithms, or prompt strategies adopted without copying copyrighted text or vendoring dependencies.
- **`NO IMPORT`**: Expressly rejected due to license incompatibility, copyright risks, or poor content quality.

---

## 2. Evaluation Findings

### 2.1 FreeLingo
- **Repository Scope:** Multi-lingual language learning application implementing CEFR-based exercise trees and gamified drills.
- **License:** MIT License.
- **Analysis:** FreeLingo does not contain an authoritative static IELTS exam bank. It contains schemas for dynamic exercise generation and CEFR difficulty leveling.
- **Decision:** **`REFERENCE ONLY`**
  - *Adopted:* CEFR scaffolding logic (A1 through C2 taxonomy) and dynamic sentence transformation drill templates.
  - *Rejected:* Vendoring UI and state management modules (Hermes Telegram Gateway handles UI).

### 2.2 OpenTutor
- **Repository Scope:** Document processing system extracting key concepts, generating quiz cards, and providing retrieval-augmented tutoring.
- **License:** AGPL-3.0.
- **Analysis:** Does not include bundled IELTS materials. Its AGPL license would impose viral copyleft restrictions if directly imported as Python code.
- **Decision:** **`REFERENCE ONLY`**
  - *Adopted:* Concept of user document analysis (e.g., student uploads a PDF article and Hermes generates reading comprehension drills).
  - *Rejected:* Direct code import, preventing license contamination of the core MIT codebase.

### 2.3 IELTS Desk / Unofficial Prep Blogs
- **Analysis:** These web resources contain student-submitted essays and scraped exam materials with unclear intellectual property ownership.
- **Decision:** **`NO IMPORT`**
  - *Rationale:* High risk of copyright infringement from Cambridge University Press or IDP.

### 2.4 IELTS Reading Mock Test Scrapes
- **Analysis:** Web-scraped reading passages from commercial practice test books (Cambridge 1–19).
- **Decision:** **`NO IMPORT`**
  - *Rationale:* Bundling commercial exam tests constitutes direct copyright violation. Replaced by Open Access scientific journals and CC-BY 4.0 academic papers.

### 2.5 Open Language Profiles / CEFR-J
- **Scope:** Academic corpora, word lists, and grammatical difficulty progressions developed by EFL researchers.
- **License:** Creative Commons Attribution (CC-BY 4.0).
- **Analysis:** High-quality, authoritative lexical and grammatical frequency data. Fully legal for redistribution with attribution.
- **Decision:** **`IMPORT`**
  - *Imported:* Core academic vocabulary lemmas, collocational pairs, and grammatical complexity indicators integrated into `content/seed/academic_vocabulary.json` and `content/seed/grammar_patterns.json`.

---

## 3. Implementation Summary

| Target | Decision | Action Taken |
|---|---|---|
| FreeLingo | `REFERENCE ONLY` | Dynamic exercise templates synthesized in `apps/learning-service/app/services/` |
| OpenTutor | `REFERENCE ONLY` | RAG concept extraction pattern implemented cleanly via FastMCP tools |
| IELTS Desk | `NO IMPORT` | Completely blocked from ingestion pipelines |
| IELTS Reading Scrapes | `NO IMPORT` | Blocked; replaced with CC-BY open access articles |
| CEFR-J / AWL | `IMPORT` | Seeded into database domain models and vocabulary registry |
