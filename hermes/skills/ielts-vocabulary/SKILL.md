---
name: ielts-vocabulary
version: 1.0.0
description: Active recall, collocations, and FSRS spaced repetition for high-yield IELTS vocabulary.
tags: [ielts, vocabulary, fsrs, collocations, review]
dependencies: [ielts-core]
---

# IELTS Vocabulary & Spaced Repetition Skill

## 1. When to Use
Activate when:
- Daily review routine triggers via Cron or user request.
- Extracting new vocabulary from errors or high-value academic essays.
- Conducting active recall vocabulary drills.

## 2. Core Workflow
1. **Fetch Due Items:**
   - Call MCP tool `get_due_reviews(learner_id=id, limit=10)`.
2. **Present Card:**
   - Format each review item using `templates/review_card.md` and `references/academic_word_list.md`.
3. **Record Performance:**
   - On student answer, evaluate accuracy and call `submit_review(learning_item_id=id, rating=1..4)`.
   - Ratings: 1 (Again), 2 (Hard), 3 (Good), 4 (Easy).
4. **Create New Learning Items:**
   - When remediating a lexical error, call `create_learning_item(canonical_form=word, meaning=def)`.
