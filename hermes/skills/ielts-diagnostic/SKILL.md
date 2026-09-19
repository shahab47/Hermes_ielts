---
name: ielts-diagnostic
version: 1.0.0
description: Onboarding, baseline calibration, and initial 7-day study plan generation.
tags: [ielts, diagnostic, onboarding, baseline]
dependencies: [ielts-core]
---

# IELTS Diagnostic Skill

## 1. When to Use
Activate when:
- A new user sends `/start` or greets the Telegram bot for the first time.
- The learner profile has `baseline_status: pending`.
- The user requests a comprehensive reset or diagnostic re-evaluation.

## 2. Core Workflow
1. **Intake Questions:** Present the 4 onboarding questions using `templates/diagnostic_intake.md`.
2. **Call Onboarding API:** POST profile to `/diagnostic/onboard` or via MCP `get_learner_profile`.
3. **Administer Baseline Mini-Task:**
   - Offer a 15-minute Task 2 essay prompt or 2-minute Speaking prompt.
4. **Calibrate & Generate Schedule:**
   - Call `generate_daily_plan` and `generate_weekly_plan`.
   - Update user profile and confirm starting baseline band.
