# License Inventory & Third-Party Legal Governance

**Specification:** `IELTS_Hermes_Antigravity_Master_Execution_Spec_v3.md` (Phases P0, P11, P13)  
**Last Updated:** 2026-09-19  
**Status:** Authoritative Legal and Licensing Analysis  

---

## 1. Overview and Legal Boundary

This inventory audits all third-party datasets, repositories, and learning models referenced in the project architecture. It guarantees full legal compliance with intellectual property regulations and ensures zero copyright infringement of commercial testing organizations.

---

## 2. Third-Party Repository & Corpus Audit

| Entity / Target | Claimed / Found License | Content Nature | Reusability / Redistribution Rights | Technical Decision |
|---|---|---|---|---|
| **FreeLingo** | MIT License / Apache 2.0 | Language learning exercise generation architecture, CEFR level scaffolding | **Permissive for Code & Logic**. Question prompts are generated via LLM prompt chains; no proprietary static question bank. | **REFERENCE ONLY**: Reusable prompt patterns and CEFR scaffolding adopted; no heavy dependency vendored. |
| **OpenTutor** | AGPL-3.0 / MIT | Document upload $\to$ flashcard and quiz generator, adaptive tutoring pipeline | **Code Architecture Only**. Does not ship bundled IELTS exam sets. | **REFERENCE ONLY**: Concept of upload-to-drill flow adopted without importing AGPL code. |
| **IELTS Desk** | Community / Unlicensed or Proprietary | Aggregated IELTS blog posts, sample essays, community tips | **Non-Redistributable**. Risk of scraped commercial exam content. | **NO IMPORT**: Prohibited from ingestion. High copyright liability. |
| **IELTS Reading Mock Test (Public Web)** | Varied / All Rights Reserved | Scraped practice passages from Cambridge/British Council | **Non-Redistributable**. | **NO IMPORT**: Direct ingestion forbidden. Replaced by Open Access CC-BY research papers (PLOS, arXiv). |
| **Open Language Profiles / CEFR-J** | Creative Commons Attribution (CC-BY 4.0) | Standard European Framework adapted for EFL learners; frequency sublists | **Fully Permissive**. Redistribution permitted with attribution. | **IMPORT**: Academic Word List (AWL) & CEFR-J B2/C1/C2 lemma lists imported into vocabulary seed datasets. |
| **Official IELTS (Cambridge / BC / IDP)** | All Rights Reserved (Copyright Law) | Official Cambridge IELTS Examination Papers (Vols 1–19) | **Strictly Prohibited from Direct Redistribution**. Public band descriptors available for educational reference. | **REFERENCE ONLY**: Only public evaluation band criteria (TA, CC, LR, GRA) used for metric scoring. Zero copyrighted passages bundled. |

---

## 3. License Compatibility Matrix

```text
+-----------------------+--------------------+-----------------------------+
| Component             | License            | Project Compatibility       |
+-----------------------+--------------------+-----------------------------+
| ielts-hermes Core     | MIT License        | Clean permissive foundation |
| FastAPI / SQLAlchemy  | MIT / BSD          | Compatible                  |
| FSRS-6 Algorithm      | MIT License        | Compatible                  |
| CEFR-J Lexicon        | CC-BY 4.0          | Compatible (Attribution)    |
| PLOS Academic Texts   | CC-BY 4.0          | Compatible (Attribution)    |
| Nous Hermes Agent     | MIT License        | Compatible                  |
| 9Router               | MIT License        | Compatible                  |
+-----------------------+--------------------+-----------------------------+
```

---

## 4. Hard Enforcement Rules

1. **No Proprietary Crawling:** Scraped test prep websites must never be introduced into automated retrieval or database seed scripts.
2. **Transformative Synthetic Exercises:** Practice items must be dynamically synthesized using verified IELTS difficulty rubrics or drawn from verified open datasets.
3. **Audit Trail:** Every content addition to the database must include a valid license identifier verified against this document.
