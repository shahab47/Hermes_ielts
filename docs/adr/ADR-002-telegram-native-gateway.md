# ADR-002: Native Telegram Gateway

## Status
Accepted

## Date
2026-09-19

## Context
The IELTS learning agent requires a primary interface that enables seamless, daily mobile interactions. Preparing for IELTS requires frequent micro-practice sessions, prompt responses to writing challenges, audio voice note exchanges for Speaking practice, and automated proactive reminders. Telegram is the ideal client due to its cross-platform availability, robust voice messaging capabilities, and rich bot API.

We evaluated two architectural approaches for connecting Telegram to our system:
1. **Separate custom Telegram gateway**: Building an independent service using `python-telegram-bot` or `aiogram` that handles Telegram webhooks/polling, manages user sessions, routes audio messages to transcription services, and forwards structured events to the agent or learning engine.
2. **Hermes Agent native Telegram gateway**: Utilizing the built-in Telegram gateway provided directly by Hermes Agent.

A custom gateway would allow arbitrary Telegram UI widgets (inline keyboards, multi-step callback buttons, mini-apps), but introduces significant engineering overhead: audio downloading and transcoding, conversation state synchronisation, authentication, rate limiting, and dual maintenance of bot logic alongside agent logic.

## Decision
We will use **Hermes Agent's native Telegram gateway** configured in long-polling mode for our primary user interface.

Implementation principles:
1. **Single authorized user**: Restrict bot access strictly to the owner's numeric Telegram User ID via configuration (`TELEGRAM_ALLOWED_USERS`). All unauthorized messages must be dropped immediately.
2. **Long-polling operational mode**: Deploy using long-polling for local development and target VPS hosting, avoiding the operational overhead of public domain/SSL webhook registration during MVP. Webhook mode through a Caddy reverse proxy remains an option if latency or infrastructure requirements dictate.
3. **Native voice message ingestion**: Rely on Hermes' built-in audio pipeline to receive Telegram voice notes, route them to local STT (faster-whisper), and deliver transcriptions to the agent context while retaining audio paths for downstream pronunciation analysis.
4. **Native scheduled delivery**: Leverage Hermes' proactive scheduling capabilities to dispatch study reminders and review sessions directly to the authorized Telegram chat.

## Consequences
### Positive
- **Zero custom gateway code**: Eliminates the need to build, test, and maintain an intermediate gateway service and its associated message routing boilerplate.
- **Native voice support**: Seamless handling of voice messages from Telegram into the agent's transcription pipeline without custom audio conversion scripts.
- **Built-in proactive messaging**: Scheduled reviews and cron notifications route straight to the user's Telegram chat without an external message broker or push notification service.
- **Strict single-user security**: Enforces hard user ID whitelisting at the gateway ingress, guaranteeing complete privacy for personal learning data and preventing unauthorized access.

### Negative
- **Interface restricted to Hermes gateway capabilities**: The interaction model is limited to standard Telegram text, voice messages, media/document attachments, and native command formats supported by Hermes.
- **No complex custom Telegram UI widgets**: Specialized UI components like multi-level inline keyboard callback menus, persistent custom reply markups, or Telegram Web Apps cannot be easily managed without upstream gateway modifications.

### Risks
- **Hermes gateway may lack specific Telegram Bot API features**: Advanced Telegram features (such as fine-grained typing indicators, message reaction handling, or interactive inline query results) may not be exposed by Hermes.
  - *Mitigation*: Design pedagogical interactions around natural dialogue, concise markdown cards, standard numbered options, and command shortcuts; re-evaluate a dedicated gateway only if a confirmed user-experience bottleneck arises in Phase 2/3.
