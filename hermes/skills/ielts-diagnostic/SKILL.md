---
name: ielts-diagnostic
version: 1.1.0
description: Onboarding, baseline calibration, and initial 7-day study plan generation.
tags: [ielts, diagnostic, onboarding, baseline]
dependencies: [ielts-core]
---

# IELTS Diagnostic Skill

## 1. When to Use
Activate when:
- A new learner sends `/start` or greets the Telegram bot for the first time.
- The learner profile has `baseline_status: pending`.
- The user requests an onboarding reset, level assessment, or diagnostic evaluation.

---

## 2. Core Workflow & Rules

### Rule #1: Read-Only Skills (Strictly Enforced)
- **DO NOT** call `skill_manage` or attempt to edit, patch, or write to skill files. Skill files are immutable system prompts, NOT storage for learner profiles.
- Never output internal tool errors, failed patch messages, or raw status messages like "پیدا نشد".

### Rule #2: Intake Processing
When the user responds to the 4 intake questions:
1. **Extract & Acknowledge**: Extract the target band (e.g., 7.5), timeline (e.g., 3 months), daily study commitment (e.g., 60 minutes), and prior testing experience.
2. **Store Facts**: If the `memory` tool is available, record learner facts (e.g., target band, timeline, daily commitment).
3. **Warm Confirmation**: Reply warmly in Persian, summarizing their learning profile.

### Rule #3: Administer Diagnostic Baseline Task
Immediately invite the learner to take an initial baseline diagnostic test to calibrate their current level. Provide options:
- ✍️ **Writing Task 2 Mini-Essay**: Write an introduction and one body paragraph (approx. 120 words) for a given academic topic in 15 minutes.
- 🎙️ **Speaking Part 2 Task**: Record a 1.5–2 minute voice message answering a Cue Card with 1-minute prep.
- 📖 **Reading Baseline Drill**: Read a 300-word academic excerpt and answer 3 True/False/Not Given questions.

Once the learner chooses their preferred skill or sends their diagnostic attempt, evaluate it against IELTS public band descriptors, determine their starting baseline, and generate their initial weekly study schedule.
