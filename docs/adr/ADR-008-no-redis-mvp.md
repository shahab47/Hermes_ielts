# ADR-008: No Redis, Celery, or Kafka in MVP

## Status
Accepted

## Date
2026-09-19

## Context
Contemporary software engineering architectures routinely include distributed caching layers (Redis/Memcached), asynchronous task queues (Celery/RQ/Dramatiq), and event streaming brokers (Kafka/RabbitMQ). While these components are indispensable for high-concurrency multi-tenant platforms, the IELTS Personal Learning Agent is designed as a **single-user, private personal tutor**.

Introducing message brokers and distributed task systems into the learning service at the outset introduces significant liabilities:
- Additional long-running Docker containers and host memory consumption on a single VPS.
- Operational complexity (broker configuration, persistent volume mounts, connection pooling, monitoring, Dead Letter Queues).
- Distributed state failure modes, race conditions, and complex debugging workflows.
- Heavier onboarding, CI/CD pipelines, and local developer environment prerequisites.

## Decision
We will **strictly exclude Redis, Celery, and Kafka from the Learning Service core MVP**.

### Operational Architecture for MVP
Instead of distributed infrastructure, we will use lightweight, built-in alternatives tailored to single-user requirements:
1. **Scheduled User Routines**:
   - Use **Hermes native cron** engine for periodic user-facing interactions (e.g., daily spaced repetition review nudges, morning practice prompts, weekly diagnostic retrospectives).
2. **Standard Learning Operations**:
   - Use **synchronous FastAPI and MCP tool invocations** for normal interactive learning operations (e.g., submitting practice answers, scoring short exercises, updating FSRS cards, retrieving learner mastery summaries).
3. **Durable Background Processing**:
   - If asynchronous or durable background execution is required (e.g., multi-pass essay grading, acoustic metric computation, bulk content indexing), use **PostgreSQL transactional job tables** (`SELECT ... FOR UPDATE SKIP LOCKED` pattern) with simple background runner coroutines.

### Explicit Honcho Exception
- The self-hosted **Honcho v3.0.6 stack** (Plastic Labs) internally utilizes Redis for orchestrating its background Deriver and Dreamer memory workers.
- This Redis instance is completely encapsulated within Honcho's isolated Docker Compose network and container definition.
- It does **not** count as our learning service adopting Redis: the learning service communicates with Honcho exclusively over Honcho's clean HTTP/REST SDK boundary, and neither Hermes nor the Learning Service connects to Honcho's internal Redis.

### Expansion Gateway
Redis will only be considered for the learning service if documented, measured latency profiling or queue saturation demonstrates a bottleneck that PostgreSQL and in-process async coroutines cannot resolve.

## Consequences

### Positive
- **Streamlined Operations**: Fewer containers to run, monitor, restart, and maintain in production.
- **Lower Memory & Compute Footprint**: Leaves maximum VPS RAM and CPU headroom for PostgreSQL, vector similarity search, and local `faster-whisper` inference.
- **Transactional Atomicity**: State changes, job status, and learner records remain in a single ACID-compliant database (PostgreSQL), eliminating distributed transaction and split-brain states.
- **Simplified Developer Experience**: Fast local bootstrapping without needing multiple background service workers.

### Negative
- **Blocking Latency Risk**: Long-running synchronous evaluations (e.g., a comprehensive 4-criterion essay grading pass) tie up the immediate HTTP/MCP request thread until completion.
- **Lack of In-Memory Caching Layer**: Frequent read-heavy queries hit PostgreSQL directly, relying entirely on PostgreSQL's internal buffer pool and effective indexing.

### Risks
- **Assessment Latency Exceeding Request Timeouts**: If a thorough diagnostic evaluation takes 15–30 seconds, Telegram gateway HTTP requests could time out or cause UX pauses.  
  *Mitigation*: Configure generous gateway client timeouts (60s+); implement optimistic progress responses; if necessary, use transactional job records in PostgreSQL where the agent initiates an evaluation job and polls or waits for completion via simple status checks.
