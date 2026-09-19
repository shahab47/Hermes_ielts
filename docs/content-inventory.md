# Content Inventory & Provenance Catalog

**Specification:** `IELTS_Hermes_Antigravity_Master_Execution_Spec_v3.md` (Phases P0, P11, P12)  
**Last Updated:** 2026-09-19  
**Status:** Authoritative Content Catalog  

---

## 1. Principles of Content Governance

1. **Explicit Provenance:** Every question, passage, rubric, and audio prompt must carry a verifiable source reference and retrieval timestamp.
2. **Zero Unauthorized Redistribution:** No commercial third-party IELTS materials (e.g., Cambridge IELTS Practice Tests 1–19, Barron's, Kaplan) are bundled into the Git repository.
3. **Source Categorization:** All learning materials are classified into one of six canonical categories:
   - `official`: Publicly released sample tasks from IELTS partners (IELTS.org, British Council, IDP).
   - `open_source`: Permissively licensed code or learning datasets (MIT, Apache 2.0).
   - `open_dataset`: Public domain or academic corpora (CC-BY, CC0, Open Database).
   - `user_owned`: Material explicitly uploaded or typed by the individual learner during a session.
   - `generated`: Dynamically synthesized learning items created by the local AI engine with validated difficulty and anti-hallucination checks.
   - `reference_only`: Proprietary rubrics or structures referenced for calibration and scoring without reproducing copyrighted text.

---

## 2. Seed Content Registry

| Item ID | Skill / Domain | Source Type | Title / Description | Publisher / Origin | License / Rights | Redistribution Allowed | Version / Date |
|---|---|---|---|---|---|---|---|
| `seed-band-desc-01` | Writing & Speaking | `reference_only` | Public IELTS Band Descriptors (Tasks 1 & 2, Speaking) | British Council / IDP / Cambridge | Public Educational Reference | Yes (Fair Use/Transformative Calibration) | 2026.1 / 2026-09-19 |
| `seed-acad-vocab-01` | Vocabulary | `open_dataset` | Academic Word List (AWL) & CEFR B2–C2 Sublists (100 Core Lemmas) | Averil Coxhead / CEFR-J | Creative Commons (CC-BY 4.0) | Yes | 2026.1 / 2026-09-19 |
| `seed-grammar-pat-01`| Grammar | `open_source` | Complex Sentence Patterns & Inversion Drills (12 Templates) | IELTS Hermes Project | MIT License | Yes | 2026.1 / 2026-09-19 |
| `seed-task2-prompt-01`| Writing | `generated` | Band 7+ Task 2 Essay Prompts (8 Standard Themes) | Synthesized with Rubric Alignment | Project Original (CC-BY-SA 4.0) | Yes | 2026.1 / 2026-09-19 |
| `seed-speak-part2-01` | Speaking | `generated` | Part 2 Cue Cards with Follow-Up Questions (10 Cards) | Synthesized with Lexical Gating | Project Original (CC-BY-SA 4.0) | Yes | 2026.1 / 2026-09-19 |
| `seed-reading-passage-01` | Reading | `open_dataset` | Academic Reading Sample: Cognitive Science of Language Acquisition | Open Access Academic Text (PLOS) | CC-BY 4.0 | Yes | 2026.1 / 2026-09-19 |
| `seed-listening-audio-01` | Listening | `open_dataset` | Section 1 Campus Housing Inquiry Transcript & Form | Synthetic Dialogue & Audio Spec | Project Original | Yes | 2026.1 / 2026-09-19 |

---

## 3. Required Metadata Schema for All Ingested Items

Every record in the content database (`content_items` and `questions`) enforces the following contract:

```json
{
  "id": "item-unique-uuid",
  "source_type": "official | open_source | open_dataset | user_owned | generated | reference_only",
  "publisher": "string",
  "url_or_reference": "string",
  "license": "string",
  "rights_status": "verified_permissive | fair_use | public_domain | local_user_only",
  "redistribution_allowed": true,
  "retrieval_method": "seed_fixture | dynamic_generation | user_upload | web_retrieval",
  "version": "string",
  "retrieved_at": "ISO-8601 UTC timestamp"
}
```

---

## 4. Verification and Content Integrity

- **Automated Check:** Database migration seeds validate that `rights_status` and `license` are non-null for all bundled records.
- **Fair Use Boundary:** Only structural rubric descriptors (TA, CC, LR, GRA) and freely licensed public domain sample questions are bundled. No paywalled or commercial exam books are ever ingested.
