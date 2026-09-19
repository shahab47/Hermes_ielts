---
name: ielts-pronunciation
version: 1.0.0
description: Acoustic pronunciation diagnostics, word stress, rhythm, and phonological drills.
tags: [ielts, pronunciation, phonology, stress, intonation]
dependencies: [ielts-core]
---

# IELTS Pronunciation Skill

## 1. When to Use
Activate when:
- Analyzing learner voice messages with acoustic audio analysis.
- Teaching word stress placement in multisyllabic academic words.
- Practicing connected speech, sentence stress, and thought chunking.

## 2. Mandatory Policy
> [!CAUTION]
> Never assess pronunciation from text/transcript alone.
> If only text is available, state that pronunciation cannot be evaluated without audio.

## 3. Core Workflow
1. When voice note is received:
   - Call MCP tool `analyze_audio` to check speech rate and pause ratio.
   - Inspect acoustic features: primary word stress on key lexical items, sentence stress patterns.
2. Deliver targeted drill:
   - Present minimal pairs or stress-contrast sentences (e.g., `ECOnomy` vs `ecoNOMic` vs `ecoNOmist`).
3. Instruct learner to repeat via voice note.
4. Record metrics via `save_assessment` with pronunciation criterion evaluated.
