---
name: ielts-reading
version: 1.1.0
description: Practice, scanning/skimming strategies, and passage drills for IELTS Academic Reading.
tags: [ielts, reading, skimming, scanning, academic]
dependencies: [ielts-core]
---

# IELTS Academic Reading Skill

## 1. When to Use
Activate when:
- The learner requests a reading practice, reading drill, or test in Telegram.
- Practicing specific question types: True/False/Not Given, Heading Matching, Summary Completion, Multiple Choice.
- Teaching scanning for numbers/names and skimming for topic sentences.

---

## 2. Core Workflow & Rules

### Rule #1: In-Chat Delivery (Strictly Enforced)
- **DO NOT** use `browser_exec` or attempt to open external websites (such as ieltsbuddy, etc.) for reading practice.
- Always provide the reading passage and questions directly inside the Telegram message using clean markdown formatting.

### Rule #2: Exercise Structure
1. **Passage Excerpt**: Present an authentic academic passage excerpt (250–400 words) on topics like science, environment, history, or education.
2. **Questions**: Present 3–4 targeted questions (e.g., True / False / Not Given, or Multiple Choice).
3. **Format**:
   ```markdown
   📖 **IELTS Academic Reading Drill**

   **Passage: [Title]**
   [Passage text...]

   ---
   **Questions 1–3:**
   Do the following statements agree with the information in the passage?
   Write:
   • **TRUE** if the statement agrees with the information
   • **FALSE** if the statement contradicts the information
   • **NOT GIVEN** if there is no information on this

   1. [Statement 1]
   2. [Statement 2]
   3. [Statement 3]

   👉 پاسخ‌های خود را به سادگی به صورت (مثلاً: 1. TRUE, 2. FALSE, 3. NOT GIVEN) ارسال کنید.
   ```

### Rule #3: Evaluation & Feedback
When the learner submits their answers:
1. Score the answers (e.g. 3/3).
2. For any incorrect answer, quote the exact sentence from the passage and explain why the answer was False or Not Given.
3. If MCP tools are active, record the attempt using `create_attempt(skill="reading", task_type="passage_drill")`.
