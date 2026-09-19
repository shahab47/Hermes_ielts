---
name: ielts-study-planner
version: 1.0.0
description: Generates balanced, deterministic daily and weekly study schedules.
tags: [ielts, planner, study_plan, schedule, adaptive]
dependencies: [ielts-core]
---

# IELTS Study Planner Skill

## 1. When to Use
Activate when:
- Morning Cron routine triggers (`0 8 * * *`).
- Learner requests a new daily study plan or adjust study duration.
- Generating a weekly preparation trajectory.

## 2. Core Workflow
1. **Fetch Current State:**
   - Call MCP tool `get_learner_profile` to retrieve target band and exam date.
   - Call `get_learning_priorities` to identify the top bottleneck.
   - Call `get_due_reviews` to count overdue FSRS cards.
2. **Generate Balanced Plan:**
   - Call MCP tool `generate_daily_plan(available_minutes=user_minutes)`.
   - Enforce balanced distribution: ~40% bottleneck, ~30% spaced review, ~30% integrated practice.
3. **Format Schedule:**
   - Deliver morning briefing using `hermes/routines/morning_routine.prompt.md`.
