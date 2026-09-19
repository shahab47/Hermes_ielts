# ADR-005: MCP as Learning Service Boundary

## Status
Accepted

## Date
2026-09-19

## Context
The IELTS preparation system requires a distinct boundary between the conversational agent orchestration layer (Hermes Agent) and the deterministic domain logic layer (the Learning Service). The Learning Service is responsible for diagnostic band scoring, FSRS-6 spaced repetition state updates, rubric retrieval, attempt logging, and longitudinal analytics.

We evaluated four candidate integration mechanisms to expose learning service capabilities to Hermes:
1. **Direct in-process Python imports**: Running the learning service inside the same process as Hermes. This tightly couples the services, introduces Python package dependency conflicts, complicates isolated testing, and prevents independent scaling or deployment.
2. **Generic REST API calls**: Having Hermes call arbitrary REST endpoints via HTTP client skills or scripts. While decoupled, this lacks standardized tool-calling schemas, automatic parameter validation, and first-class LLM introspection capabilities.
3. **gRPC with Protocol Buffers**: High-performance binary RPC, but over-engineered for our needs and unsupported natively by Hermes Agent without custom client wrappers.
4. **Model Context Protocol (MCP)**: The open standard developed for connecting LLM applications to external tools and data sources. Hermes provides native, first-class support for MCP clients.

## Decision
We will use the **Model Context Protocol (MCP)** as the primary integration boundary between Hermes Agent and the Learning Service.

Architectural details:
1. **System Topology**:
   ```text
   Hermes Agent (Orchestration)
       │
       ▼ (MCP stdio or SSE)
   Learning Service (MCP Server & FastAPI)
       │
       ├── Domain Services (Diagnostic Evaluation, FSRS Planner, Rubric Engine)
       ├── PostgreSQL 18 + pgvector (Authoritative Persistence & RAG)
       └── Rule-based & LLM Analyzers
   ```
2. **Narrow, Strictly Typed MCP Tools**:
   - The Learning Service will expose specific, task-oriented tools with strict JSON schemas (validated via Pydantic 2.x).
   - Examples include: `record_practice_attempt`, `get_due_flashcards`, `submit_fsrs_review`, `get_current_learner_profile`, `evaluate_writing_criterion`, and `search_official_rubrics`.
   - Complex state transitions and database mutations occur deterministically inside the Learning Service, not within the agent prompt.
3. **Dual Interface via FastAPI**:
   - While Hermes interacts exclusively via the MCP server interface, the Learning Service will also expose an internal HTTP API using FastAPI for:
     - Health checks (`/healthz`, `/readyz`)
     - Developer administrative inspection and CLI tooling
     - Test harnesses and CI automated verification
     - Metrics and telemetry collection

## Consequences
### Positive
- **Clean separation of concerns**: The agent remains a pure conversational orchestrator, while educational algorithms, IELTS rubric rules, and database schemas remain fully encapsulated inside the Learning Service.
- **Hermes-native integration**: Hermes natively connects to MCP servers without custom adapter code or third-party wrappers.
- **Type safety and schema validation**: MCP tools enforce strong schema definitions via Pydantic models, rejecting malformed tool calls before execution.
- **Deterministic and auditable operations**: Every mutation to learner state passes through typed functions with explicit parameters, logging, and audit records.
- **Independent testability**: The entire learning engine can be verified through standard unit and integration tests (via pytest or internal HTTP endpoints) without launching an LLM or Hermes session.

### Negative
- **Serialization overhead**: Inter-process communication via JSON-RPC/MCP adds minor latency compared to direct in-memory Python calls (negligible for conversational tutoring workflows).
- **Request-response paradigm**: MCP is fundamentally request-response driven; spontaneous asynchronous event pushes from the Learning Service to Hermes must rely on Hermes cron or scheduled poll triggers.
- **Dual API definition**: Requires maintaining MCP tool definitions alongside internal FastAPI endpoint routes for administrative/testing tasks.

### Risks
- **Evolving MCP standard**: The Model Context Protocol specification is evolving, which could lead to API updates in future SDK releases.
  - *Mitigation*: Pin the official Python MCP SDK version, encapsulate tool definitions cleanly within `apps/learning-service/app/mcp/`, and back all tools with robust unit tests.
- **Debugging opacity**: Troubleshooting MCP payload exchange between Hermes and the server can be harder than debugging monolithic application logs.
  - *Mitigation*: Enable structured JSON logging for all incoming MCP tool calls and responses; maintain the internal HTTP endpoints for direct manual verification.
