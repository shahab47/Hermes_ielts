---
name: ielts-vocabulary
version: 0.1.0
description: IELTS vocabulary learning and spaced repetition. Extracts high-value items from learner output, manages FSRS-based review scheduling, and tracks two-dimensional mastery (recognition vs production).
tags: [ielts, vocabulary, fsrs, review]
dependencies: [ielts-core]
---

# IELTS Vocabulary

## When to Use
- During scheduled vocabulary review sessions
- When extracting vocabulary from learner essays/speech
- When the learner explicitly requests vocabulary work

## Item Extraction Rules
An item becomes review-worthy ONLY if:
- Repeated relevance across multiple contexts
- Learner error (misuse, wrong form, wrong collocation)
- High task value (academic word list, topic-specific)
- Explicit learner request

Do NOT automatically add every word encountered.

## Two-Dimensional Mastery
Track separately:
- **Recognition**: Can identify meaning in context
- **Production**: Can use correctly in own writing/speech
- **Contextual use**: Can deploy appropriately for IELTS tasks

## FSRS Integration
- Rating: Again (1) / Hard (2) / Good (3) / Easy (4)
- Desired retention: 0.9 (configurable)
- Review types: recognition quiz, production prompt, contextual usage

## Implementation Status
⚠️ Stub — Full implementation in Phase 9
