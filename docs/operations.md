# Operations & Maintenance Guide (Phase 26)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P26-OPERATIONS`  
**Date:** 2026-09-19  
**Status:** ACTIVE  

---

## 1. Daily Operations & Service Monitoring

### 1.1 Service Status & Logs
```bash
# Check service status
sudo systemctl status hermes-gateway
sudo systemctl status ielts-learning

# Follow real-time gateway logs
sudo journalctl -u hermes-gateway -f

# Follow backend structured JSON logs
sudo journalctl -u ielts-learning -f --output=cat
```

### 1.2 Restarting Services
```bash
# Safe restart of Telegram gateway
sudo systemctl restart hermes-gateway

# Safe restart of Learning Backend
sudo systemctl restart ielts-learning
```

---

## 2. Maintenance Schedules & Automated Jobs

### 2.1 Crontab Configuration (`crontab -e`)
Add the following operational routines to the host user's crontab:

```bash
# 1. Daily PostgreSQL Backup at 03:00 UTC
0 3 * * * /home/ubuntu/ielts-hermes/infra/scripts/backup_db.sh >> /var/log/ielts-backup.log 2>&1

# 2. Weekly Audio Asset TTL Cleanup (prune > 14 days) on Sunday at 04:00 UTC
0 4 * * 0 /home/ubuntu/ielts-hermes/apps/learning-service/.venv/bin/python /home/ubuntu/ielts-hermes/infra/scripts/purge_user_data.py --cleanup-audio --days 14 >> /var/log/ielts-cleanup.log 2>&1

# 3. Weekly Sunday Learner Memory Archive at 05:00 UTC
0 5 * * 0 /home/ubuntu/ielts-hermes/apps/learning-service/.venv/bin/python /home/ubuntu/ielts-hermes/infra/scripts/export_learner_memory.py --output-dir /home/ubuntu/ielts-hermes/backups >> /var/log/ielts-export.log 2>&1
```

---

## 3. Storage & Disk Usage Monitoring

```bash
# Check disk usage of database volume and audio directory
df -h
du -sh /var/lib/docker/volumes/*
du -sh /home/ubuntu/ielts-hermes/audio_storage
du -sh /home/ubuntu/ielts-hermes/backups
```
