---
name: ielts-speaking-part2
version: 0.1.0
description: IELTS Speaking Part 2 (Long Turn) practice and assessment. Manages cue card delivery, preparation timing, response timing, and multi-criteria evaluation.
tags: [ielts, speaking, part2, assessment]
dependencies: [ielts-core]
---

# IELTS Speaking Part 2 — Long Turn

## When to Use
Activate when the learner requests Speaking Part 2 practice or when the planner schedules it.

## Workflow
1. Present cue card topic
2. Start 1-minute preparation timer
3. Prompt learner to begin speaking (voice message)
4. Enforce 1-2 minute response window
5. Transcribe audio via STT
6. Compute basic speech metrics (duration, speech rate, pause ratio)
7. Assess against Speaking criteria
8. Record attempt, assessment, and errors via MCP
9. Provide structured feedback

## Speaking Criteria
| Criterion | Notes |
|-----------|-------|
| Fluency & Coherence | Speech rate, pause patterns, topic development |
| Lexical Resource | Range, precision, collocation |
| Grammatical Range & Accuracy | Complexity, accuracy, control |
| Pronunciation | **Only assessed when audio analysis is available** |

## Pronunciation Policy
- Transcript-only evaluation: pronunciation = UNASSESSED
- Never infer pronunciation quality from spelling/transcript
- Phase 1: basic acoustic metrics only
- Phase 3: phoneme alignment via MFA

## Implementation Status
⚠️ Stub — Full implementation in Phase 6
