---
name: ielts-listening
version: 1.0.0
description: Practice, note-taking drills, and distractor detection for IELTS Listening.
tags: [ielts, listening, note_taking, audio]
dependencies: [ielts-core]
---

# IELTS Listening Skill

## 1. When to Use
Activate when:
- Practicing Sections 1 through 4 of IELTS Listening.
- Training distractor detection, signposting phrases, and spelling precision under auditory constraints.

## 2. Core Workflow
1. Present task questions (form filling, map labeling, or multiple choice).
2. Deliver the audio transcript/speech via TTS or audio file.
3. Evaluate learner answers:
   - Check strict spelling accuracy and word-limit compliance (e.g., NO MORE THAN TWO WORDS).
4. For errors: highlight auditory distractors (self-corrections by the speaker, synonyms).
5. Record attempt and score via MCP tool `create_attempt(skill="listening")`.
