# ADR-004: PostgreSQL 18 + pgvector

## Status
Accepted

## Date
2026-09-19

## Context
The IELTS learning agent requires persistence for two distinct data modalities:
1. **Structured relational learner data**: Diagnostic band scores, detailed rubric criteria evaluations (Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy), granular attempt histories, itemized grammatical/lexical error frequencies, FSRS-6 spaced repetition parameters (stability, difficulty, due dates, review logs), and longitudinal progress tracking.
2. **Semantic content and embeddings**: Official public IELTS band descriptors, curated practice questions, reading passages, sample band-9 essays, collocations lexicons, and past learner error patterns for similarity retrieval (RAG).

We evaluated several data persistence and retrieval architectures:
- **Relational / Document DB + Separate Dedicated Vector DB (e.g., PostgreSQL/SQLite + Qdrant/Chroma/Pinecone)**: Provides specialized vector indexing features, but introduces dual-system complexity: two database engines to host, backup, and monitor; two connection pools; distributed transactions; and the constant risk of synchronization lag between relational entities and their corresponding vector representations.
- **SQLite + sqlite-vec**: Lightweight and single-file, but lacks robust multi-process concurrency, enterprise-grade tooling, and advanced indexing features for production deployment on a VPS.
- **MongoDB + Atlas Vector Search**: Adds document-store complexity and external cloud dependencies, unsuited for self-hosted local-first architecture.
- **Unified PostgreSQL 18 with pgvector 0.8.x**: Combines transactional ACID guarantees with native vector similarity search inside a single, highly mature open-source relational database.

## Decision
We will use **PostgreSQL 18** with the **pgvector 0.8.x** extension as the authoritative, single source of truth for all relational learner data and vector content retrieval.

Key implementation policies:
1. **Authoritative Single Source of Truth**:
   - The LLM context window and agent memory files (`USER.md`, `MEMORY.md`, Honcho) must never be treated as the source of truth for quantitative facts.
   - All diagnostic band scores, attempt timestamps, error frequencies, mastery levels, FSRS scheduling states, and completion milestones reside strictly in PostgreSQL.
2. **Native Vector Search via pgvector**:
   - Use `pgvector` columns and HNSW (Hierarchical Navigable Small World) / IVFFlat indexes directly inside PostgreSQL tables to power semantic retrieval for IELTS rubrics, reference materials, and similar past mistakes.
   - No dedicated external vector database (such as Qdrant, Pinecone, or ChromaDB) will be introduced in the MVP.
3. **Database Migrations & Tooling**:
   - Manage all database schemas and pgvector extension activations strictly via **SQLAlchemy 2.x** and **Alembic** migrations.
   - Run PostgreSQL 18 via official Docker containers with pgvector pre-installed.

## Consequences
### Positive
- **Single data infrastructure**: One database engine to configure, secure, back up, and monitor in Docker Compose, drastically simplifying operations and recovery runbooks.
- **Strict ACID transactional integrity**: Vector embeddings and their relational parent records (e.g., an IELTS essay submission and its semantic chunk vectors) are stored and updated within atomic database transactions.
- **Robust relational ecosystem**: Decades of proven reliability, advanced SQL querying, comprehensive indexing (B-tree, GIN, HNSW), and rich Python tooling (SQLAlchemy 2.x asyncpg, Alembic).
- **Zero data synchronization drift**: Eliminates out-of-sync states between relational IDs and external vector database collections.

### Negative
- **Specialized vector optimization limits**: pgvector does not have some of the niche filtering and sharding optimizations available in dedicated distributed vector engines (e.g., Qdrant).
- **Shared memory resource contention**: RAM is shared between PostgreSQL relational buffer pools and pgvector HNSW index graphs.

### Risks
- **Indexing and query latency with large embedding collections**: High memory usage during HNSW index construction or vector searches under very large collections.
  - *Mitigation*: In a single-user personal IELTS tutor context, the total corpus (rubrics, practice prompts, user mistake history) consists of tens of thousands of items, not tens of millions. pgvector HNSW easily delivers sub-millisecond retrieval latencies at this scale with negligible memory footprint.
