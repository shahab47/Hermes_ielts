---
name: ielts-core
version: 1.0.0
description: Core IELTS assessment standards, taxonomy classification, and feedback patterns.
tags: [ielts, assessment, rubric, core]
---

# IELTS Core Knowledge & Pedagogical Standard

## 1. When to Use
Activate this skill whenever:
- Evaluating any IELTS practice output (Writing Task 1/2, Speaking Parts 1/2/3, Reading, Listening)
- Formulating diagnostic band score estimates
- Classifying errors into the standard taxonomy
- Interacting with the Learning Service via MCP tools

## 2. Mandatory Rules
1. **Never claim to be an official examiner.** State clearly that all scores are diagnostic estimates based on official public criteria.
2. **Evidence-first scoring:** Never give a score without at least one positive quote and one limiting quote from the student's submission.
3. **Focus over flood:** Address the ONE primary bottleneck limiting the score, rather than enumerating 20 minor issues.
4. **Never infer pronunciation from transcripts alone.**
5. **Always synchronize state via MCP:** Use `create_attempt`, `save_assessment`, and `record_error_events`.

## 3. Workflow
1. **Observe:** Inspect input format, count words/duration, check preflight conditions using `preflight_writing` or `analyze_audio`.
2. **Evaluate:** Match text against criteria in `references/scoring_rubrics.md`.
3. **Classify:** Tag specific error snippets using `references/error_taxonomy.md`.
4. **Persist:** Invoke MCP tools to store attempt, scores, and error events.
5. **Communicate:** Render the assessment using `templates/feedback_response.md`.
