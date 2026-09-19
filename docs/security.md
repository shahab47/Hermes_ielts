# Security Architecture & Single-User Access Control (Phase 19)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P19-SECURITY`  
**Date:** 2026-09-19  
**Status:** PRODUCTION READY  

---

## 1. Threat Model & Security Posture

The **IELTS Personal Learning Agent** is designed as a **single-user private assistant** with execution access to local filesystem tools and terminal commands. Because the agent possesses code-execution capabilities, a defense-in-depth security model is enforced across all ingress and execution surfaces.

```text
[ Incoming Telegram Message ]
             |
             v
+------------------------------------------+
| 1. Ingress Gate: Telegram ID Whitelist   |  --> Unauthorized ID:
|    (fail-closed drop before event loop)  |      SILENT DROP (Zero compute/token spend)
+------------------------------------------+
             | Authorized User ID
             v
+------------------------------------------+
| 2. Secrets & Token Redaction             |  --> Sanitizes environment & logs
|    (Regex scrub of API keys & tokens)    |
+------------------------------------------+
             |
             v
+------------------------------------------+
| 3. Execution Boundary                    |  --> Terminal commands scoped to
|    (Scoped workspace, no host root)      |      project workspace root
+------------------------------------------+
             |
             v
+------------------------------------------+
| 4. Database Access (Least Privilege)     |  --> Standard app user has DML only;
|    (PostgreSQL role isolation)           |      Alembic uses migration role
+------------------------------------------+
```

---

## 2. Ingress Security: Telegram Single-User Allowlist

### 2.1 Fail-Closed Authorization Policy
Hermes Gateway enforces early authorization checking (`test_telegram_auth_check.py`):
1. Every update received via Telegram long-polling contains `from_user.id`.
2. The numeric ID is matched against `platforms.telegram.extra.allow_from` and `TELEGRAM_ALLOWED_USERS`.
3. If the ID is missing or not in the allowlist:
   - The message is **dropped immediately** at the gateway boundary.
   - No session is created.
   - No prompt is tokenized or dispatched to the LLM.
   - No webhook or callback response is sent.

### 2.2 Privacy Mode & Group Blocking
- Group chats are strictly disabled via BotFather (`/setjoingroups -> DISABLED`).
- If the bot is inadvertently added to a channel or supergroup, `allowed_chats` filtering ensures messages outside the private user chat are discarded.

---

## 3. Database Security & Least Privilege

1. **Role Segregation:**
   - `ielts_app`: Operational application user granted `SELECT`, `INSERT`, `UPDATE`, `DELETE` on domain tables. Prohibited from `DROP TABLE`, `ALTER TABLE`, or database creation.
   - `ielts_admin` / `alembic`: Migration runner role granted DDL privileges for schema migrations.
2. **Network Isolation:**
   - PostgreSQL container listens only on `127.0.0.1:5432` (or internal Docker network `ielts-net`), never on public `0.0.0.0`.
3. **SQL Injection Defense:**
   - Strictly parameterized queries via SQLAlchemy 2.x Core & ORM. Raw string formatting in SQL is prohibited.

---

## 4. Secrets Management & Zero-Commit Policy

1. **Gitignore Strict Enforcement:**
   - `.env`, `.env.*` (except `.env.example`) are blocked in root `.gitignore`.
   - Local sqlite state (`*.db`, `*.sqlite3`) and Hermes state directories (`.hermes/`) are ignored.
2. **Secret Scrubber:**
   - Logging middleware and error handlers redact sensitive headers (`Authorization`, `X-Telegram-Bot-Token`, API keys) before emission.

---

## 5. Tool Execution & Workspace Scoping

1. **Local Terminal Scoping:**
   - Terminal tool execution defaults to the repository root directory (`cwd: "."`).
   - Sudo execution without explicit authorization is prohibited.
2. **Web Content Ingestion:**
   - Content fetched via RAG or web tools is treated as untrusted plain text.
   - Never execute arbitrary downloaded scripts or shell code from external web sources.
