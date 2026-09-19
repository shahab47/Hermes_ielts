---
name: ielts-core
version: 0.1.0
description: Core IELTS learning agent capabilities — learner state management, error taxonomy, weakness tracking, study planning coordination.
tags: [ielts, core, learning]
dependencies: []
---

# IELTS Core Skill

## When to Use
Always active. This skill provides foundational capabilities used by all other IELTS skills.

## Capabilities
- Read and update learner profile via MCP
- Track error events using the standard error taxonomy
- Manage weakness lifecycle (hypothesis → confirmed → resolved)
- Coordinate with the adaptive planner

## MCP Tools Used
- `get_learner_profile`
- `get_skill_state`
- `get_active_weaknesses`
- `get_learning_priorities`
- `update_weakness_state`

## Implementation Status
⚠️ Stub — Full implementation in Phase 6
