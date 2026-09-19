# ADR-009: Official IELTS Public Sources as Rubric Authority

## Status
Accepted

## Date
2026-09-19

## Context
A diagnostic IELTS learning system must evaluate student essays, spoken responses, and language practice against authentic and reliable standards. Scoring rubrics can be sourced from various options:
1. **Third-Party Prep Books & Commercial Materials (Cambridge IELTS past papers, Barron's, Kaplan, Magoosh)**:
   - *Advantages*: Extensive variety of sample prompts, model answers, and examiner commentary.
   - *Disadvantages*: Heavily copyrighted and proprietary; scraping or embedding commercial materials violates licensing terms and exposes the project to legal liability.
2. **Proprietary or Black-Box LLM Training**:
   - *Advantages*: Quick to prototype using naive conversational prompting (e.g., "grade this IELTS essay from 1 to 9").
   - *Disadvantages*: Yields inconsistent, unanchored, and hallucinatory scores; lacks standardized explanatory feedback mapped to authentic criteria.
3. **Official IELTS Public Descriptors & Specifications**:
   - *Advantages*: Published directly by the official test partners (British Council, IDP: IELTS Australia, and Cambridge University Press & Assessment); legally accessible for public educational use; establishes an indisputable source of ground truth for scoring dimensions.
   - *Disadvantages*: Public descriptors are formulated at whole-band increments and condense certain granular operational notes reserved for certified examiners.

## Decision
We will establish **official IELTS public band descriptors, assessment criteria, and test format specifications as the sole scoring rubric authority** for the system.

### Core Scoring Policies
1. **Diagnostic & Estimated Status Only**:
   - All scores and feedback emitted by the system are strictly classified and explicitly presented as **diagnostic/estimated evaluations**.
   - The system will never present, label, or market any diagnostic assessment as an "official", "certified", or "guaranteed" IELTS band score.
2. **Authoritative Rubric Criteria**:
   - **Writing (Task 1 and Task 2)**:
     1. *Task Achievement* (Task 1) / *Task Response* (Task 2)
     2. *Coherence and Cohesion*
     3. *Lexical Resource*
     4. *Grammatical Range and Accuracy*
   - **Speaking (Parts 1, 2, and 3)**:
     1. *Fluency and Coherence*
     2. *Lexical Resource*
     3. *Grammatical Range and Accuracy*
     4. *Pronunciation* (subject to the empirical measurement constraints defined in ADR-007)
3. **Content Provenance and Copyright Compliance**:
   - The system will **never** scrape, ingest, or store copyrighted commercial prep books, proprietary mock exams, or paywalled materials without explicit, documented user ownership or licensing.
   - Seed content and RAG knowledge bases will consist strictly of:
     - Official public band descriptors and test format outlines published by IELTS.org, British Council, and Cambridge.
     - Open-access linguistic datasets (e.g., Academic Word List, CEFR vocabulary profiles).
     - User-provided study materials uploaded directly for private personal analysis.
     - Internally generated practice tasks engineered to match official format specifications without replicating copyrighted test prompts.

## Consequences

### Positive
- **Complete Legal and Copyright Safety**: Eliminates risks of copyright infringement or takedown liabilities by strictly using public domain or official public documentation.
- **Authentic Alignment**: Grounded directly in the published standards established by the exam creators, ensuring student feedback directly targets authentic IELTS evaluation criteria.
- **Explainable & Transparent Diagnostic Feedback**: Every diagnostic score can be explicitly anchored to specific band descriptor statements, allowing the learner to see exactly why an essay scored a 6.0 versus a 7.0 on Lexical Resource or Coherence & Cohesion.

### Negative
- **Public Descriptor Granularity**: Public band descriptors provide descriptions at whole band levels (Band 5, 6, 7, 8, 9), requiring careful calibration prompts to accurately classify borderline half-band performances (e.g., 6.5).
- **Nuance Limitations**: Lacks internal examiner training clarifications regarding specific penalty rules (e.g., memorized scripts, non-standard layout penalties).

### Risks
- **Subjective LLM Evaluation Drift**: Because LLM evaluations are probabilistic, identical student submissions could receive slightly divergent criterion scores across different evaluation runs.  
  *Mitigation*: Implement deterministic evaluator prompts with structured JSON schemas, few-shot calibrated examples, criterion-by-criterion evidence citations, and a version-controlled regression evaluation test suite to verify scoring consistency before deploying prompt changes.
