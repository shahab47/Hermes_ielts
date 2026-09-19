---
name: ielts-writing-task2
version: 0.1.0
description: IELTS Academic Writing Task 2 assessment and practice. Evaluates essays against official public band descriptors for Task Response, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy.
tags: [ielts, writing, task2, assessment]
dependencies: [ielts-core]
---

# IELTS Writing Task 2

## When to Use
Activate when the learner submits a Writing Task 2 essay or requests Writing Task 2 practice.

## Prerequisites
- Learner profile exists in database
- Writing Task 2 prompt/question available

## Workflow
1. Receive essay text from learner
2. Verify: word count ≥250, task type identified, all instruction components addressed
3. Assess against four criteria using official public band descriptors
4. Record attempt and assessment via MCP
5. Classify and record error events
6. Identify primary bottleneck
7. Provide structured feedback (8-step response pattern)
8. Schedule targeted follow-up practice

## Scoring Criteria
| Criterion | Weight |
|-----------|--------|
| Task Response | 25% |
| Coherence & Cohesion | 25% |
| Lexical Resource | 25% |
| Grammatical Range & Accuracy | 25% |

## Evidence Requirements
Every criterion score MUST include:
- Numeric score (0.5 increments)
- Confidence level (low/medium/high)
- Positive evidence (specific excerpts)
- Limiting evidence (specific excerpts)
- Evaluator version

## Implementation Status
⚠️ Stub — Full implementation in Phase 6
