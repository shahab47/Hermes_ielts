#!/usr/bin/env bash
# Automated PostgreSQL Backup Script (Phase 27)
# Runs daily via cron: 0 3 * * * /home/ubuntu/ielts-hermes/infra/scripts/backup_db.sh

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/home/ubuntu/ielts-hermes/backups}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-ielts-postgres}"
DB_NAME="${DB_NAME:-ielts_learning}"
DB_USER="${DB_USER:-ielts}"
RETENTION_DAYS=14

mkdir -p "${BACKUP_DIR}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/ielts_db_${TIMESTAMP}.sql.gz"

echo "[*] Starting PostgreSQL backup for ${DB_NAME} at $(date)..."

# Execute pg_dump inside Docker container and pipe to gzip
if docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    docker exec "${POSTGRES_CONTAINER}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"
    echo "[OK] Backup successfully written to: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"
else
    echo "[!] Container ${POSTGRES_CONTAINER} is not running! Backup aborted." >&2
    exit 1
fi

# Rotate backups older than RETENTION_DAYS
echo "[*] Pruning database backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "ielts_db_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "[OK] Backup completed successfully at $(date)."
