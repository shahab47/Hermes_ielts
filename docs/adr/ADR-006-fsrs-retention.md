# ADR-006: FSRS for Retention Scheduling

## Status
Accepted

## Date
2026-09-19

## Context
A key capability of the IELTS Personal Learning Agent is driving long-term retention of lexical resources, collocations, grammatical structures, and pronunciation targets. The system needs an algorithmically sound, deterministic spaced repetition scheduler that calculates optimal review intervals based on empirical memory consolidation models.

Four primary options were evaluated:
1. **SM-2 (SuperMemo 2 / Legacy Anki)**:
   - *Advantages*: Widely known, simple mathematical formula based on ease factor and intervals.
   - *Disadvantages*: Heuristic-driven with rigid exponential intervals; poorly models memory lapses; assumes uniform difficulty scaling; lacks modern empirical validation against large-scale spaced repetition datasets.
2. **Leitner Box System**:
   - *Advantages*: Extremely simple fixed-bucket system.
   - *Disadvantages*: Far too coarse for granular, cross-skill retention tracking; does not model memory retrievability or stability decay over continuous time.
3. **Custom Spaced Repetition Heuristic**:
   - *Advantages*: Maximum control over custom rules.
   - *Disadvantages*: High engineering and calibration overhead; high risk of sub-optimal interval calculations; unvalidated mathematical foundations.
4. **FSRS (Free Spaced Repetition Scheduler)**:
   - *Advantages*: Modern, state-of-the-art DSR (Difficulty, Stability, Retrievability) model based on cognitive science and empirical memory research; proven and validated across hundreds of millions of reviews in the Anki community; provides pure Python implementations via `py-fsrs`; deterministic scheduling.
   - *Disadvantages*: More complex parameter set (21 parameters in FSRS-6) than SM-2.

## Decision
We will adopt the **FSRS-6 algorithm** implemented via the official Python package **`py-fsrs` v6.3.2**.

### Scope and Boundary
- **Item-level micro-skill reviews only**: FSRS will be used exclusively for scheduling individual micro-learning targets:
  - Vocabulary items (definitions, register, Academic Word List targets)
  - Lexical collocations and phrasal verbs
  - Specific grammar micro-skills (e.g., subject-verb agreement patterns, conditional clause structures, inversion)
  - Pronunciation targets where atomized review is meaningful (e.g., minimal pairs, word stress patterns)
- **Explicit exclusion from macro-planning**: FSRS will **NOT** be used as the planner or scheduler for full IELTS tasks (such as Writing Task 1/2 essays, full Reading/Listening practice sections, or full Speaking Part 1–3 simulations). Macro-level study plans and task sequencing are orchestrated by the domain `Planner` module based on diagnostic band gaps and exam timelines.

### Technical Implementation Details
1. **FSRS-6 Parameterization**:
   - The scheduler operates with the standard 21 default parameters defined in FSRS-6, providing robust cold-start performance without requiring per-learner hyperparameter tuning in the MVP.
   - Default target retention: `desired_retention = 0.9` (configurable per learner, e.g., 0.85–0.92 depending on urgency and target band).
2. **Ratings and States**:
   - Standard 4-point rating scale via `Rating` enum: `Again` (1), `Hard` (2), `Good` (3), and `Easy` (4).
   - Card lifecycle states via `State` enum: `New` (0), `Learning` (1), `Review` (2), and `Relearning` (3).
3. **Storage & Serialization**:
   - State persistence relies on `py-fsrs` built-in serialization: `Card.to_dict()` / `Card.to_json()` and `Card.from_dict()` / `Card.from_json()`.
   - In PostgreSQL, the authoritative state is stored in a structured JSONB column (`fsrs_card_data`) on the card/item table, with key query dimensions mirrored into indexed columns (`due_at`, `state`, `stability`, `difficulty`, `reps`, `lapses`, `last_review_at`) for sub-millisecond retrieval of due items.

## Consequences

### Positive
- **State-of-the-Art Retention**: FSRS-6 consistently outperforms legacy algorithms (SM-2, Leitner) in predicting memory retrievability, reducing review overload while sustaining desired target retention.
- **Battle-Tested at Scale**: Validated across millions of review logs by the global spaced repetition and Anki research community.
- **Deterministic & Python-Native**: Pure Python implementation with zero C-extensions or external services required, making unit testing deterministic and fast.
- **Configurable Workload**: Adjusting `desired_retention` allows dynamic optimization between aggressive retention (closer to exam date) and manageable daily review volume.
- **Zero-Loss Serialization**: First-class JSON dictionary export and import enables robust persistence in PostgreSQL.

### Negative
- **Two-Dimensional Mastery Overhead**: IELTS vocabulary demands a distinction between passive recognition (Reading/Listening) and active production (Writing/Speaking). FSRS tracks single cards by default, requiring the application layer to maintain separate recognition and production review cards or a composite mapping.
- **Atomization Required**: Spaced repetition only functions effectively when learning items are properly atomized into clear stimulus-response cards, requiring clean parsing and extraction from diagnostic feedback.

### Risks
- **Algorithm Upstream Changes**: Minor or major version updates in `py-fsrs` may alter scheduling curves or parameter specifications.  
  *Mitigation*: Pin exact version `py-fsrs==6.3.2` in `pyproject.toml`. Store full review history and raw card state as JSONB in PostgreSQL to enable recalculation or migration scripts if an algorithm upgrade occurs.
- **Over-Review Fatigue**: If the agent creates too many FSRS cards from every essay or speaking attempt, the learner may experience review debt.  
  *Mitigation*: Establish strict generation caps (e.g., maximum 5–7 high-priority cards per diagnostic attempt) prioritized by the pedagogical analyzer.
