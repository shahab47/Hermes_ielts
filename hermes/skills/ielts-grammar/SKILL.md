---
name: ielts-grammar
version: 1.0.0
description: Focused micro-skill practice and remediation for IELTS grammatical range and accuracy.
tags: [ielts, grammar, accuracy, micro-skills]
dependencies: [ielts-core]
---

# IELTS Grammar Skill

## 1. When to Use
Activate when:
- Remediating confirmed grammatical weaknesses (clause structure, tense, articles, subordination).
- Delivering 3-minute evening drills via Hermes Cron.
- Providing sentence-combining and complex structure exercises.

## 2. Core Workflow
1. Identify the targeted weakness using `references/grammar_patterns.md`.
2. Present a short 2-question drill using `templates/grammar_drill.md`.
3. Check learner response for exact syntactic accuracy.
4. Record progress and update weakness status via MCP tool `update_weakness_state`.
