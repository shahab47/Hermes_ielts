---
name: ielts-writing-task1
version: 1.0.0
description: Practice, data analysis, and evaluation for IELTS Academic Writing Task 1.
tags: [ielts, writing, task1, charts, assessment]
dependencies: [ielts-core]
---

# IELTS Writing Task 1 Skill

## 1. When to Use
Activate when:
- Learner submits a response describing a graph, chart, table, map, or process.
- Learner requests practice prompts, vocabulary for trends, or overview guidance.

## 2. Core Workflow
1. **Preflight Check:**
   - Call MCP tool `preflight_writing(task_type="task_1", text=user_submission)`.
   - Verify word count >= 150 words.
   - Verify detection of an overview sentence or paragraph.
2. **Evaluation:**
   - Evaluate against criteria using `references/task1_visual_types.md`.
   - Ensure the student highlighted key features and made comparisons where relevant.
3. **Persist State:**
   - Call `create_attempt(skill="writing", task_type="task_1", raw_input=text)`.
   - Record errors via `record_error_events`.
   - Save assessment via `save_assessment`.
4. **Respond:**
   - Use `templates/task1_feedback.md`.
