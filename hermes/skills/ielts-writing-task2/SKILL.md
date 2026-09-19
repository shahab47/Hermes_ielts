---
name: ielts-writing-task2
version: 1.0.0
description: Practice, verification, and evidence-first evaluation for IELTS Academic Writing Task 2.
tags: [ielts, writing, task2, essay, assessment]
dependencies: [ielts-core]
---

# IELTS Writing Task 2 Skill

## 1. When to Use
Activate when:
- Learner submits an essay or paragraph for IELTS Writing Task 2.
- Learner asks for essay prompts, brainstorming assistance, or model outlines.
- Evaluating Task 2 essays or providing paragraph-level rewrites.

## 2. Core Workflow
1. **Preflight Verification:**
   - Call MCP tool `preflight_writing(task_type="task_2", text=user_submission)`.
   - Verify word count >= 250 words and detect position markers.
   - If under 250 words, note penalty on Task Response.
2. **Criterion Evaluation:**
   - Score the 4 criteria against `references/band_descriptors.md`.
   - Ensure the prompt type is classified using `references/prompt_types.md`.
   - Extract at least one positive quote and one limiting quote per criterion.
3. **Persist State:**
   - Call `create_attempt(skill="writing", task_type="task_2", raw_input=text)`.
   - Call `record_error_events` for all grammatical, lexical, and structural slips.
   - Call `save_assessment` with the 4 criterion scores and evidence JSON.
4. **Deliver Feedback:**
   - Render the response using `templates/writing_feedback.md`.
   - Explanations in Persian, quotes and models in English.
