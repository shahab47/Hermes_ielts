# ADR-001: Hermes Agent as Orchestration Layer

## Status
Accepted

## Date
2026-09-19

## Context
A personal IELTS Academic preparation agent requires an orchestration runtime capable of handling multi-turn conversational tutoring, multi-modal I/O (text and voice), structured tool invocation, proactive scheduling, and persona consistency. The system must coordinate diagnostic assessments, deliver bite-sized practice, monitor user state, and provide personalized feedback aligned with IELTS band descriptors.

We evaluated four architectural approaches for the agent runtime:
1. **Custom bespoke agent framework**: Building a custom agent loop from scratch using raw Python, LLM API SDKs (OpenAI/Anthropic), and custom dispatcher logic. While offering complete control, this requires reinventing core agent primitives—session state, tool dispatch, memory integration, message buffering, voice handling, and gateway connections.
2. **LangChain / LangGraph**: Provides modular graphs and workflow management, but introduces significant framework churn, heavy abstraction layers, and requires substantial custom glue code for chat platform gateways and voice processing pipelines.
3. **CrewAI**: Designed primarily for multi-agent role-playing simulations rather than a high-performance single-agent personalized tutor with tight Telegram integration and fine-grained tool calling.
4. **NousResearch Hermes Agent (v0.21.3)**: A production-oriented autonomous agent runtime with native messaging gateways (including Telegram), first-class Model Context Protocol (MCP) client support, extensible skills architecture, built-in scheduling/cron, local speech-to-text (faster-whisper), and text-to-speech (Edge TTS) integrations.

## Decision
We will use **Hermes Agent v0.21.3** as the primary orchestration layer for the IELTS learning agent.

To preserve upstream maintainability and cleanly separate concerns:
1. **Do not fork Hermes**: We will not fork or modify the Hermes Agent core codebase.
2. **Use supported extension points only**:
   - **Configuration**: Declarative setup via `config.yaml` and environment variables.
   - **Profile & Persona**: Custom agent behavior steered via `SOUL.md`, `USER.md`, and `MEMORY.md`.
   - **Skills System**: Procedural domain guidance, prompting strategies, and IELTS assessment guidelines implemented as Hermes skills.
   - **Model Context Protocol (MCP)**: All domain logic, database operations, spaced repetition scheduling, and analytics accessed via MCP servers.
   - **Plugins & Built-in Providers**: Native gateway, voice (faster-whisper), and TTS (Edge TTS) configurations.
3. **Pin version & runtime**: Lock Hermes Agent to version `0.21.3` on Python 3.13 (within Hermes' supported range of `>=3.11, <3.14`).
4. **Any deviation requires an ADR**: If a required capability cannot be achieved through supported extension points, an ADR must document the limitation before any upstream modification or fork is considered.

## Consequences
### Positive
- **Native Telegram integration**: Out-of-the-box bidirectional text and voice messaging without custom gateway services.
- **Built-in multi-modal voice processing**: Zero-overhead integration of local faster-whisper STT and Edge TTS for IELTS Speaking practice.
- **Standardized tool integration via MCP**: Decouples conversational agent orchestration from backend learning business logic.
- **Scheduled tutoring sessions**: Built-in cron capabilities allow the agent to proactively prompt the student for scheduled reviews, daily drills, and retention sessions.
- **Profile and memory separation**: Clean separation of agent persona (`SOUL.md`), learner profile facts (`USER.md`), and historical context (`MEMORY.md`).
- **Reduced maintenance burden**: Avoids developing and maintaining custom gateway, memory injection, and tool-dispatch infrastructure.

### Negative
- **Dependency on upstream maintenance**: Bound to the development pace, architectural decisions, and release lifecycle of NousResearch.
- **Python version constraints**: Restricted to the Python `>=3.11, <3.14` support envelope (standardized on Python 3.13).
- **Framework conventions**: Architectural choices must conform to Hermes' configuration schema, skill formats, and tool execution lifecycle.

### Risks
- **Upstream breaking changes**: Minor or patch updates to Hermes Agent could introduce configuration schema changes or alter skill loading mechanisms.
  - *Mitigation*: Pin exact commit/tag `v0.21.3` in package dependencies and Docker configurations; verify upgrades in an isolated test environment before updating.
- **Feature gap in extension points**: A critical IELTS tutoring feature might not be natively supported by Hermes' plugin or skills mechanism.
  - *Mitigation*: Implement complex logic within the external Learning Service exposed through MCP tools; keep Hermes strictly as an orchestrator.
