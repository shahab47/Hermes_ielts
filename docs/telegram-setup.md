# Telegram Gateway Setup & Verification Guide (Phase 3)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P3-TELEGRAM`  
**Date:** 2026-09-19  
**Status:** PRODUCTION READY  

---

## 1. Architecture Overview

Hermes Agent connects directly to Telegram using long-polling via the native Telegram Gateway adapter (`hermes gateway`). 

Key architectural properties:
- **No public IP / Webhook required:** Uses HTTPS long-polling (`getUpdates`), allowing seamless deployment behind NAT or firewalls.
- **Single-User Security Lock:** Strict allowlist filtering by numeric Telegram User ID (`allow_from` in `config.yaml` or `TELEGRAM_ALLOWED_USERS` in `.env`). Unauthorized users are dropped before message ingestion or event building.
- **Multi-Modal Ingestion:** Natively routes text, voice notes (`.ogg` Opus routed to STT), photos/images (essay photos sent to OCR/vision), and documents (`.pdf`, `.txt`, `.docx`).
- **Autonomous Cron Delivery:** Background scheduler tasks push scheduled morning drills, spaced repetition reminders, and weekly summaries directly to the learner's chat ID.

---

## 2. BotFather Configuration Instructions

Follow these exact steps in Telegram with [@BotFather](https://t.me/BotFather):

### Step 1: Create the Bot
1. Send `/newbot` to `@BotFather`.
2. Enter a friendly display name (e.g., `My IELTS & Coding Assistant`).
3. Enter a unique bot username ending in `bot` (e.g., `my_ielts_personal_bot`).
4. Save the HTTP API token provided by BotFather (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`).

### Step 2: Configure Bot Privacy & Inline Settings
1. Send `/setprivacy` to `@BotFather`.
2. Select your bot.
3. Choose **ENABLED** (ensures that if added to any group, the bot only sees messages directed to it, though private DM is the recommended mode).
4. Send `/setjoingroups` -> **DISABLED** (enforces private 1-on-1 usage only).

### Step 3: Register Bot Commands
Send `/setcommands` to `@BotFather`, select your bot, and paste the following command menu:

```text
start - Initialize or resume study session
help - Display available capabilities and commands
today - Fetch today's personalized study plan
essay - Submit an IELTS Writing Task 1 or Task 2 essay
drill - Launch a targeted micro-drill on your current bottleneck
vocab - Review due vocabulary items (FSRS spaced repetition)
grammar - Review error patterns and grammar rules
stats - View current diagnostic band levels and progress
plan - View or adjust weekly preparation schedule
export - Export all personal learning data (JSON)
reset - Clear current chat context while preserving memory
```

---

## 3. Finding Your Numeric Telegram User ID

The single-user security model requires your unique 64-bit integer Telegram ID (NOT your `@username`):

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot) or [@raw_data_bot](https://t.me/raw_data_bot).
2. Start the bot. It will respond with your account details, e.g.:
   ```text
   Id: 987654321
   First: Ali
   Username: @ali_developer
   ```
3. Copy the numeric `Id` (e.g., `987654321`).

---

## 4. Configuring Hermes Profile

In `~/.hermes/profiles/ielts-tutor/config.yaml`:

```yaml
platforms:
  telegram:
    enabled: true
    reply_to_mode: "first"
    extra:
      allow_from: [987654321]  # <--- YOUR NUMERIC TELEGRAM USER ID
      allowed_chats: [987654321]

messaging:
  telegram:
    allowed_users: [987654321]
```

In `~/.hermes/profiles/ielts-tutor/.env`:

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USERS=987654321
```

---

## 5. Gateway Operation & Lifecycle

### Starting the Gateway in Foreground (Testing)
```bash
hermes -p ielts-tutor gateway run
```

### Starting as a Background Service (Production)
```bash
# Install as systemd service
hermes -p ielts-tutor gateway install

# Start and inspect status
hermes -p ielts-tutor gateway start
hermes -p ielts-tutor gateway status
```

---

## 6. Functional Verification Scenarios

| Scenario | User Input in Telegram | Expected Bot Behavior |
|---|---|---|
| **Unauthorized User** | Message from unlisted ID | Dropped silently at adapter boundary (`test_telegram_auth_check.py` rule). |
| **General Assistant** | `"How do I configure Caddy reverse proxy on Ubuntu?"` | Answers directly with Caddy configuration. Zero IELTS mentions. |
| **Coding Question** | `"Write a Python script to parse JSON lines and aggregate errors"` | Outputs clean, type-hinted Python script. No IELTS tutoring triggered. |
| **IELTS Writing** | `"Here is my Task 2 essay on remote work: ..."` | Evaluates TR, CC, LR, GRA, identifies primary bottleneck, computes diagnostic band. |
| **Voice Note** | User speaks a 45-second Part 2 monologue (`.ogg`) | Ingests audio, transcribes with `faster-whisper`, analyzes WPM/pauses, delivers feedback. |
| **Cron Reminder** | Automated morning trigger (08:30) | Pushes daily plan and FSRS review words to Telegram chat. |
