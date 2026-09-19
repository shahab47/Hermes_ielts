---
name: ielts-weekly-review
version: 1.0.0
description: Statistical trend analysis, resolved weakness verification, and weekly diagnostic reporting.
tags: [ielts, weekly, review, diagnostic, analytics]
dependencies: [ielts-core]
---

# IELTS Weekly Review Skill

## 1. When to Use
Activate when:
- Weekly Friday Cron routine fires (`0 10 * * 5`).
- Learner requests a progress check or weekly summary.

## 2. Core Workflow
1. **Fetch Analytics Data:**
   - Call MCP tool `get_progress_summary(learner_id)`.
   - Call `get_skill_trend` for Writing, Speaking, Reading, Listening.
   - Call `get_error_heatmap_data` to visualize recurrence distribution.
   - Call `get_weekly_diagnostic` for aggregated highlights.
2. **Review Weakness Lifecycle:**
   - Identify weaknesses marked `resolved` in the past 7 days.
   - Highlight active bottlenecks requiring continued remediation.
3. **Deliver Comprehensive Report:**
   - Use the prompt template in `hermes/routines/weekly_routine.prompt.md`.
   - Deliver findings in Persian with clear progress indicators.
