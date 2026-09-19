---
name: ielts-speaking-part2
version: 1.0.0
description: Practice, timing, and evaluation for IELTS Speaking Part 2 (Long Turn).
tags: [ielts, speaking, part2, cue_card, assessment]
dependencies: [ielts-core]
---

# IELTS Speaking Part 2 Skill

## 1. When to Use
Activate when:
- Learner requests a cue card practice topic.
- Learner submits audio or transcript for a 2-minute response.
- Conducting timed Part 2 drills.

## 2. Core Workflow
1. **Prompt Delivery:**
   - Present a cue card from `references/cue_cards.md` with 4 bullet points.
   - Instruct the student to take 1 minute to plan notes.
2. **Audio Analysis:**
   - If audio/voice message is provided, call MCP tool `analyze_audio` to extract duration, WPM, and pause ratio.
   - If transcript only is provided, set Pronunciation to `unassessed (transcript only)`.
3. **Evaluation:**
   - Match performance against criteria in `references/speaking_descriptors.md`.
4. **Persist State:**
   - Call `create_attempt(skill="speaking", task_type="part_2", source="telegram_voice")`.
   - Call `save_assessment` and `record_error_events`.
5. **Feedback Delivery:**
   - Render assessment using `templates/speaking_feedback.md`.
