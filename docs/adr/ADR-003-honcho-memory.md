# ADR-003: Honcho + Built-in Hermes Memory

## Status
Accepted

## Date
2026-09-19

## Context
An effective personal IELTS tutor requires deep, continuous understanding of the learner across months of preparation. The system must track not just static facts (e.g., target band 7.5, test date in November), but also evolving cognitive patterns, learning styles, emotional responses to feedback, test anxiety triggers, and recurrent strategic habits (e.g., tendency to write over-elaborate introductions in Task 2 or rushing through Reading Passage 3).

Hermes Agent provides built-in markdown memory files:
- `SOUL.md`: Agent persona, pedagogical tone, and invariant behavior guidelines.
- `USER.md`: Compact profile of stable user facts and personal constraints.
- `MEMORY.md`: Long-term curated notes and high-level summaries.

While these built-in files are ideal for fast, deterministic, compact user context, they are not designed for dialectic user modeling, automatic cross-session extraction of psychological tendencies, or reasoning about the learner's evolving mental model (Theory-of-Mind). Relying solely on manual updates to `USER.md` or `MEMORY.md` would either bloat the agent prompt or miss subtle behavioral observations.

Conversely, offloading all state to an external LLM memory service would obscure immediate, hard-coded learner facts that must always guide the agent prompt.

## Decision
We will adopt a hybrid memory architecture combining **Honcho v3 (v3.0.6)** alongside **Hermes built-in memory**:

1. **Division of Memory Responsibilities**:
   - **Hermes Built-in Memory (`SOUL.md`, `USER.md`, `MEMORY.md`)**: Retains compact, deterministic, stable facts and active priorities. This includes target band scores, registered exam dates, target academic modules, and current weekly focus areas.
   - **Honcho v3**: Acts as the dynamic cross-session user modeling and Theory-of-Mind (ToM) platform. Honcho ingests conversation messages asynchronously, derives psychological and pedagogical insights via its background workers (Deriver and Dreamer), and produces dynamic learner representations (peer cards and context views) retrieved during session bootstrap.
   - **PostgreSQL Database**: Serves as the authoritative source of truth for all quantitative, structured learner records (scores, attempts, error frequencies, FSRS scheduling states), ensuring memory layers never fabricate test records.

2. **Self-Hosted Deployment**:
   - Deploy Honcho v3 via Docker Compose alongside our application stack to ensure complete data privacy and sovereignty over learner conversations and profiles.

3. **Infrastructure Isolation (Redis)**:
   - Honcho internally requires Redis for its background Deriver and Dreamer task queues. This Redis service is isolated strictly inside Honcho's Docker Compose boundary.
   - The core IELTS Learning Service will **not** connect to or depend on this Redis instance, maintaining full compliance with ADR-008 (No Redis in MVP learning service).

## Consequences
### Positive
- **Theory-of-Mind and dialectic modeling**: Enables the agent to maintain an empathetic, adaptive tutoring style informed by the learner's stress levels, cognitive tendencies, and conceptual blind spots.
- **Dynamic peer cards**: Honcho generates synthesized cards representing the learner's traits, strengths, and weaknesses that can be injected into the agent's context window on demand.
- **Clean separation of concerns**: Pedagogical psychology lives in Honcho; deterministic user configuration lives in Hermes markdown files; verifiable performance data lives in PostgreSQL.
- **Privacy and data sovereignty**: Self-hosting Honcho ensures full control over sensitive learner logs and analysis.

### Negative
- **Additional infrastructure overhead**: Running Honcho requires maintaining the Honcho API server, background worker processes, and an internal Redis container within Docker Compose.
- **Asynchronous LLM API costs**: Honcho's Deriver and Dreamer processes invoke background LLM calls to distill insights from sessions, increasing overall token usage and API costs.

### Risks
- **Honcho API evolution and version instability**: Honcho is an actively developing framework, and future updates could introduce breaking changes to its Python SDK or REST endpoints.
  - *Mitigation*: Pin Honcho container image to `v3.0.6`, isolate all Honcho interactions within a dedicated adapter module, and design the agent to gracefully continue tutoring using Hermes built-in memory if Honcho is temporarily unavailable.
- **Operational complexity of background workers**: Failure of Deriver/Dreamer workers could lead to stale user models.
  - *Mitigation*: Configure Docker health checks and auto-restart policies; expose Honcho health metrics to monitoring scripts.
