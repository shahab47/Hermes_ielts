# Risk Register

This document tracks technical, architectural, pedagogical, and operational risks identified for the **IELTS Personal Learning Agent (`ielts-hermes`)**.

Each risk is assigned a severity score based on its Probability and Impact, along with explicit mitigations, owners, and monitoring strategies.

---

## 1. Risk Evaluation Framework

| Severity Rating | Description | Action Required |
|---|---|---|
| **Critical** (High Impact + High/Med Probability) | Severe disruption to tutor operations, data loss, or legal liability | Immediate mitigation before production deployment |
| **Moderate** (Med Impact + Med Probability, or High Impact + Low Probability) | Degradation of learning quality, latency spikes, or integration friction | Active monitoring and pre-planned architectural fallbacks |
| **Low** (Low Impact / Low Probability) | Minor operational inconvenience or edge-case divergence | Periodic review during release milestones |

---

## 2. Master Risk Register

| ID | Risk Description | Probability | Impact | Mitigation Strategy | Owner | Status |
|---|---|---|---|---|---|---|
| **R001** | **Hermes breaking API changes between versions** | Med | High | Pin exact version (`0.21.3`); maintain `docs/hermes-compatibility.md`; run full integration test suite before any version bump. | Agent Architect | Active |
| **R002** | **Honcho Redis requirement conflicts with no-Redis MVP** | Low | Med | Encapsulate Redis strictly within Honcho's isolated Docker network; learning service communicates solely via HTTP/SDK without touching Redis. | Backend Lead | Mitigated |
| **R003** | **Pronunciation analysis accuracy limitations** | High | Med | Implement phased rollout (transcript → acoustic timestamps → MFA alignment); enforce policy never to claim false precision or invent phoneme scores. | Speech / NLP Lead | Active |
| **R004** | **LLM scoring inconsistency across model changes** | Med | High | Version-control evaluator prompts; maintain golden evaluation regression dataset; perform automated A/B evaluations before deploying prompt updates. | Pedagogy / Evaluation Lead | Active |
| **R005** | **Single point of failure (one server, one user)** | Med | Med | Configure Docker Compose restart policies; establish daily encrypted automated PostgreSQL backups to offsite S3-compatible storage; document disaster recovery runbook. | DevOps / SRE | Active |
| **R006** | **FSRS state migration on algorithm updates** | Low | Med | Persist raw FSRS card state as structured JSONB alongside standard query indices; implement versioned deserialization compatibility adapters. | Backend Lead | Mitigated |
| **R007** | **faster-whisper CPU performance on VPS** | Med | Med | Default to `small` INT8 quantized model; make model and quantization fully configurable; benchmark latency and CPU load during setup. | Speech / Infra Lead | Active |
| **R008** | **Hermes cron reliability for scheduled learning** | Low | High | Instrument heartbeat logging for cron jobs; implement missed-schedule detection and fallback via PostgreSQL durable job records. | Backend Lead | Active |
| **R009** | **Copyright/licensing of IELTS preparation content** | Med | High | Restrict knowledge base exclusively to official public band descriptors, open-access lexicons, user-provided texts, and synthetically generated prompts. | Compliance / Content Lead | Mitigated |
| **R010** | **Honcho LLM costs for Deriver/Dreamer workers** | Med | Med | Configure Honcho background memory workers to use cost-effective small models (e.g., GPT-4o-mini / Haiku); track and alert on token consumption spikes. | Agent Architect | Active |

---

## 3. Detailed Risk Analysis & Treatment Plans

### R001: Hermes Breaking API Changes Between Versions
- **Context**: NousResearch Hermes Agent undergoes rapid feature development, with potential changes in skill schemas, MCP client interfaces, or memory protocols across minor releases.
- **Detailed Mitigation**:
  - Pin `hermes-agent==0.21.3` in all lockfiles.
  - Maintain an explicit compatibility matrix (`docs/hermes-compatibility.md`) cross-referencing every YAML config key and CLI invocation.
  - Never execute unvetted automatic upgrades; test candidate updates in a staging environment against all end-to-end smoke tests.

### R002: Honcho Redis Requirement Conflicts with No-Redis MVP
- **Context**: ADR-008 dictates a no-Redis architecture for the learning service, while Honcho v3.0.6 uses Redis internally for worker queues.
- **Detailed Mitigation**:
  - Isolate Honcho's internal Redis inside `infra/docker/honcho-compose.yml` on a private bridge network (`honcho-net`).
  - Learning service containers share no network interface with Honcho's Redis and connect only via Honcho's external HTTP REST API port.

### R003: Pronunciation Analysis Accuracy Limitations
- **Context**: General-purpose STT models (such as Whisper) tend to autocorrect mispronounced words into standard dictionary words, masking phonological errors and leading to misleading pronunciation assessments.
- **Detailed Mitigation**:
  - Enforce ADR-007 pronunciation policy in code and prompt schemas: mark pronunciation as `unassessed (transcript only)` in MVP.
  - In Phase 2, incorporate objective acoustic metrics (pause ratio, articulation rate).
  - In Phase 3, deploy Montreal Forced Aligner (MFA) with explicit phoneme distance modeling before issuing phone-level feedback.

### R004: LLM Scoring Inconsistency Across Model Changes
- **Context**: Upstream changes in foundation LLM weights, decoding temperatures, or prompt structure can alter diagnostic band score distributions for identical student essays.
- **Detailed Mitigation**:
  - Maintain a versioned evaluation regression test suite containing 30+ benchmark essays with consensus human examiner scores.
  - Anchor LLM evaluators with explicit few-shot band descriptor citations and structured rubric scoring schemas (JSON mode).
  - Require automated regression test runs with delta variance thresholds (`|delta| <= 0.5 band`) prior to merging prompt modifications.

### R005: Single Point of Failure (One Server, One User)
- **Context**: Hosting the personal learning agent on a single VPS creates a risk of catastrophic data loss if the VPS instance terminates or suffers storage failure.
- **Detailed Mitigation**:
  - Configure `restart: unless-stopped` on all Docker Compose service containers.
  - Automate nightly `pg_dump` jobs with GPG encryption and push to offsite S3-compatible cold storage.
  - Provide a tested disaster recovery runbook (`docs/runbooks/disaster-recovery.md`) enabling full restoration from a cold clone in under 15 minutes.

### R006: FSRS State Migration on Algorithm Updates
- **Context**: Upgrades to `py-fsrs` or future FSRS algorithm iterations (e.g., FSRS-7) may modify card state schemas or transition matrices.
- **Detailed Mitigation**:
  - Store full FSRS card objects in PostgreSQL as raw JSONB (`fsrs_card_data`).
  - Maintain an append-only `fsrs_review_logs` table containing complete input ratings and elapsed durations, enabling historical state recalculation if a model migration is needed.

### R007: faster-whisper CPU Performance on VPS
- **Context**: Transcribing longer voice messages (e.g., 2-minute Speaking Part 2 monologues) using CPU inference on a 2-4 vCPU VPS might cause high CPU spikes and user response delays.
- **Detailed Mitigation**:
  - Set default Whisper model to `small` with `compute_type="int8"` and thread capping.
  - Cache loaded model weights in memory; avoid re-initializing models per request.
  - If latency exceeds 5 seconds for 60-second clips, allow seamless switching to `base` model or enabling an external GPU worker.

### R008: Hermes Cron Reliability for Scheduled Learning
- **Context**: If the Hermes process restarts, crashes, or encounters cron scheduling drift, daily review reminders and check-in routines could fail to fire.
- **Detailed Mitigation**:
  - Emit heartbeat records to PostgreSQL on each scheduled cron execution.
  - Include an internal watchdog check in the Learning Service that detects if expected morning/evening routines have missed their scheduled execution window by >30 minutes.

### R009: Copyright/Licensing of IELTS Preparation Content
- **Context**: Ingesting copyrighted commercial IELTS prep books or proprietary test questions introduces legal risks and ethical violations.
- **Detailed Mitigation**:
  - Strictly enforce ADR-009: only official public band descriptors, Cambridge format guidelines, and open linguistic resources (Academic Word List) are included in the repository.
  - Store user-provided study materials in isolated private directories flagged as personal user data.
  - Implement programmatic synthetic task generators that construct original practice prompts conforming to public exam format structures.

### R010: Honcho LLM Costs for Deriver/Dreamer Workers
- **Context**: Honcho's autonomous cognitive workers (Deriver and Dreamer) execute background LLM passes to extract psychological traits, cognitive load, and theory-of-mind representations, potentially accumulating unexpected API costs.
- **Detailed Mitigation**:
  - Configure Honcho to route background worker tasks to cost-effective, high-throughput models (e.g., `gpt-4o-mini`, `claude-3-5-haiku`).
  - Set strict daily token budgets and threshold alarms in the LLM provider dashboard.
  - Tune Honcho derive intervals to trigger only after meaningful conversational sessions rather than on every single short interaction.

---

## 4. Governance & Review Cadence
- **Weekly Review**: Review active risks (R001, R003, R004, R007) during sprint planning.
- **Milestone Gate**: Every phase transition (Phase 0 -> Phase 1 -> Phase 2) requires a complete risk audit verifying that all required mitigations are actively in place.
