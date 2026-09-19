---
name: ielts-speaking-part3
version: 1.0.0
description: Practice, intellectual dialogue, and evaluation for IELTS Speaking Part 3 (Two-way Discussion).
tags: [ielts, speaking, part3, discussion, abstract]
dependencies: [ielts-core]
---

# IELTS Speaking Part 3 Skill

## 1. When to Use
Activate when:
- Practicing abstract societal questions linked to Part 2 topics (education, ethics, technology, governance).
- Training extended discourse, speculation, and counter-arguments.

## 2. Core Workflow
1. Present an analytical, abstract question (4-5 minutes total section).
2. Evaluate responses for:
   - Direct answer + Justification + Concrete societal example + Concession/Alternative view.
   - Use of academic hedging (tend to, likely to, arguably).
3. If voice response: call `analyze_audio` for speech rate and pause metrics.
4. Record attempt via MCP tool `create_attempt(skill="speaking", task_type="part_3")`.
5. Provide evidence-based assessment with criterion scores.
