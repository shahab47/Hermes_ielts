---
name: ielts-reading
version: 1.0.0
description: Practice, scanning/skimming strategies, and passage drills for IELTS Academic Reading.
tags: [ielts, reading, skimming, scanning, academic]
dependencies: [ielts-core]
---

# IELTS Academic Reading Skill

## 1. When to Use
Activate when:
- Practicing specific question types: True/False/Not Given, Heading Matching, Summary Completion, Multiple Choice.
- Teaching scanning for numbers/names and skimming for topic sentences.

## 2. Core Workflow
1. Present an academic passage excerpt (300-500 words) with 3-4 targeted questions.
2. Track learner submission and score:
   - Correct answers / Total questions.
   - For incorrect answers: provide the exact line reference and explain why distractors were tempting.
3. Record attempt via MCP tool `create_attempt(skill="reading", task_type="passage_drill")`.
4. Update skill state and trend via `save_assessment`.
