# Disaster Recovery & Restore Drill Runbook (Phase 27)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P27-DR`  
**Date:** 2026-09-19  
**Status:** ACTIVE  

---

## 1. Disaster Recovery Objective (RTO & RPO)

- **Recovery Point Objective (RPO):** Maximum 24 hours of learning events (governed by daily automated database backups at 03:00 UTC).
- **Recovery Time Objective (RTO):** Under 30 minutes from a completely destroyed VPS to restored learner interaction on Telegram.

---

## 2. Emergency Recovery Protocol (Step-by-Step)

In the event of total server loss or hardware failure:

### Step 1: Provision Clean VPS
1. Deploy Ubuntu 24.04 LTS on new server.
2. Clone repository:
   ```bash
   git clone https://github.com/YourUser/ielts-hermes.git /home/ubuntu/ielts-hermes
   cd /home/ubuntu/ielts-hermes
   ```

### Step 2: Install Core Runtimes
```bash
# Install Docker, Python 3.13, uv, Hermes
bash infra/scripts/bootstrap_host.sh # or follow docs/setup.md
```

### Step 3: Fetch Most Recent Offsite Backup Archive
```bash
scp user@backup-storage:backups/learner_memory_export_*.zip ./
scp user@backup-storage:backups/ielts_db_*.sql.gz ./
```

### Step 4: Restore PostgreSQL Database Container
```bash
docker compose up -d postgres
# Wait for container health check
docker compose ps

# Run database restore
chmod +x infra/scripts/restore_db.sh
./infra/scripts/restore_db.sh ielts_db_*.sql.gz

# Run Alembic to verify migrations are at head
cd apps/learning-service
uv run alembic upgrade head
```

### Step 5: Restore Hermes Profile Memory & Config
```bash
python infra/scripts/import_learner_memory.py \
    --archive learner_memory_export_*.zip \
    --profile-dir ~/.hermes/profiles/ielts-tutor
```

### Step 6: Start Gateway & Verify Learner Identity
```bash
sudo systemctl enable --now hermes-gateway
```
Send `/start` in Telegram. Confirm that the bot immediately recognizes your target band (7.5), past error history, and scheduled plan.

---

## 3. Scheduled Recovery Drills
- Run the restore drill every 30 days into an isolated local container or staging environment to verify backup archive non-corruption.
