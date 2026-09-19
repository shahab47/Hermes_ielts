# Post-MVP Enhancements & Future Intelligence Layer Roadmap (Phases 29 & 30)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P29-P30-ROADMAP`  
**Date:** 2026-09-19  
**Status:** ARCHITECTURAL SPECIFICATION & ROADMAP  

---

## 1. Phase 29: Post-MVP Architectural Enhancements

Per Master Execution Specification v2, Section 37, the following non-blocking capabilities are scheduled for progressive rollout only after the core MVP single-user tutoring loop is proven in daily practice:

### 1.1 Richer Reading & Listening Engine
- Multi-format audio parsing for Listening sections 1-4 with exact timestamp alignment.
- Interactive Reading skimming/scanning drill generator targeting matching headings, true/false/not given, and summary completion.

### 1.2 Advanced Acoustic Pronunciation Analysis
- Phoneme-level error heatmaps utilizing Wav2Vec2/Whisper token probabilities.
- Prosodic rhythm, intonation pitch contour tracking, and word-stress emphasis scoring.

### 1.3 Teacher-Grade Analytical Dashboards
- Exportable weekly PDF performance dossiers for academic advisors.
- Longitudinal trajectory plots across CEFR B1 through C2 milestones.

### 1.4 Controlled Multi-User Support
- Optional tenant isolation allowing separate learner IDs per Telegram chat with shared content seed banks.

---

## 2. Phase 30: Future Intelligence Layer

Per Master Execution Specification v2, Section 38, advanced cognitive intelligence will activate once sufficient longitudinal learner data is accumulated in the authoritative PostgreSQL database:

### 2.1 Predictive Mistake Forecasting
- Bayesian knowledge tracing over grammatical and lexical error taxonomies.
- Proactive warning prompts before the student attempts high-risk essay structures.

### 2.2 Synthetic Conversational Partners
- Multi-agent debate simulations for Speaking Part 3 (e.g. Devil's Advocate persona questioning academic assertions).

### 2.3 Empirical Model Benchmark Routing
- Dynamically routing complex Writing Task 2 evaluations to high-reasoning models while serving quick vocabulary flashcards with local/fast models.

### 2.4 Strict Safety Mandate
- **No self-modifying production code.** All model weights, prompts, and database migrations remain strictly controlled under engineering review, Git versioning, and CI test suites.
