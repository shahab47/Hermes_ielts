# ADR-007: Local-First Speech Pipeline

## Status
Accepted

## Date
2026-09-19

## Context
IELTS Speaking preparation requires ingesting, transcribing, and evaluating spoken English across Parts 1, 2, and 3. The system must process learner audio messages sent via Telegram, extract verbatim transcripts for grammatical and lexical analysis, and progressively assess fluency, pacing, and pronunciation.

Three architectural approaches were evaluated:
1. **Cloud-Only APIs (e.g., OpenAI Whisper API, Google Cloud Speech-to-Text, Deepgram)**:
   - *Advantages*: Zero local compute burden; access to the largest models without local hardware demands.
   - *Disadvantages*: Audio leaves the user's infrastructure, raising serious privacy concerns for personal voice recordings; continuous per-minute API costs; dependency on external network latency and third-party API availability.
2. **Hybrid Cloud/Local**:
   - *Advantages*: Local processing for quick checks, cloud for heavy analysis.
   - *Disadvantages*: Increases architectural complexity, dual-path failure modes, and inconsistent transcription artifacts between local and remote models.
3. **Local-First Pipeline (faster-whisper on host/container)**:
   - *Advantages*: Complete user privacy (audio data never leaves the server); zero per-minute cloud transcription fees; low latency on dedicated hardware; native integration with Hermes Agent's voice subsystem.
   - *Disadvantages*: Processing is bound to local server CPU/GPU resources; model size and precision must be balanced against available RAM and CPU cores.

## Decision
We will implement a **local-first speech processing pipeline** structured across three evolutionary phases:

### Phased Roadmap
1. **MVP (Phase 1 & Phase 2)**:
   - Ingest Telegram voice messages directly via Hermes native Telegram gateway.
   - Transcribe audio locally using **`faster-whisper`** (CTranslate2-accelerated implementation of Whisper).
   - Use language hinting fixed or biased to English (`language="en"`).
   - Default model size: `small` (optimized for fast CPU execution on standard VPS hosting); support configurable upgrade to `medium` or `large-v3` if host hardware permits.
   - Preserve raw audio files on persistent storage (`infra/storage/audio/`) with immutable file hashes and links to learner attempt records to allow retroactive re-processing.
2. **Phase 2 (Fluency and Acoustic Metrics)**:
   - Extract word-level and segment-level timestamps using `faster-whisper` detailed output.
   - Compute deterministic acoustic and temporal metrics: speech rate (words per minute), articulation rate (words per phonation second), pause frequency, average pause duration, and pause distribution (distinguishing grammatical juncture pauses from disfluent mid-clause hesitations).
3. **Phase 3 (Phoneme-Level Alignment & Pronunciation)**:
   - Integrate **Montreal Forced Aligner (MFA)** or an equivalent benchmarked local acoustic aligner against standard phonetic dictionaries (e.g., CMUdict or BEEP).
   - Derive acoustic phonemic boundaries, vowel formant stability, and word stress markers for granular pronunciation diagnostic feedback.

### Strict Pronunciation Assessment Policy
To preserve scientific validity and pedagogical integrity:
- **Never claim that Whisper transcript quality alone measures pronunciation**: Speech-to-text models like Whisper are trained to decode semantic intent and inherently normalize or hallucinate standard spelling over non-standard pronunciations.
- **Never output an invented or simulated phoneme score**: The system will never hallucinate or prompt an LLM to generate pseudo-phonetic scores from text transcripts.
- **Explicit unassessed labeling**: In MVP (and prior to Phase 3 acoustic phoneme alignment), the IELTS Speaking criterion **Pronunciation** must be explicitly marked as `unassessed (transcript only)` or evaluated solely on verifiable rhythm/pacing heuristics, rather than generating unverified phonetic accuracy marks.

## Consequences

### Positive
- **Guaranteed Privacy**: Learner voice samples and practice recordings remain strictly on the private host; zero biometric or voice data is transmitted to external vendors.
- **Zero Cloud Operating Cost**: No recurring billing per minute of audio transcribed.
- **Low Latency & Resilience**: Completely independent of third-party cloud API rate limits, outages, or network throttling.
- **Hermes-Native Compatibility**: Aligns directly with Hermes Agent v0.21.3's built-in support for `faster-whisper` STT and Edge TTS.
- **Auditable & Future-Proof**: Storing raw audio files guarantees that when Phase 2 and Phase 3 aligners come online, all historical practice attempts can be retroactively analyzed.

### Negative
- **CPU-Bound Processing**: Standard VPS configurations without dedicated GPUs will experience noticeable transcription latency if models larger than `small` are selected.
- **Model Size vs. Accuracy Trade-Off**: `small` models may occasionally mistranscribe heavily accented speech or quiet utterances compared to cloud `large-v3` endpoints.
- **No Real-Time Streaming**: Audio is processed as complete voice notes rather than continuous bidirectional low-latency streaming.

### Risks
- **Hardware Resource Starvation**: Concurrent execution of `faster-whisper` inference and LLM orchestration on a 2-vCPU VPS could cause CPU spikes and brief responsiveness drops.  
  *Mitigation*: Benchmark `small` with `compute_type="int8"` on the target hardware. Limit worker thread allocation and configure process priorities.
- **Complexity of Montreal Forced Aligner in Phase 3**: MFA introduces non-trivial system dependencies (Kaldi/acoustic models/lexicons) and container overhead.  
  *Mitigation*: Isolate MFA into an optional Phase 3 microservice container or batch job worker, keeping the core MVP lightweight.
