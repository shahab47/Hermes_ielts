#!/usr/bin/env bash
# PostgreSQL Restore Drill Script (Phase 27)
# Usage: ./restore_db.sh /path/to/backup.sql.gz

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_file.sql.gz>" >&2
    exit 1
fi

BACKUP_FILE="$1"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-ielts-postgres}"
DB_NAME="${DB_NAME:-ielts_learning}"
DB_USER="${DB_USER:-ielts}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "[!] Backup file not found: ${BACKUP_FILE}" >&2
    exit 1
fi

echo "[*] Restoring database ${DB_NAME} from ${BACKUP_FILE}..."

# Decompress and stream directly into psql inside Docker container
gunzip -c "${BACKUP_FILE}" | docker exec -i "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}"

echo "[OK] Database successfully restored from ${BACKUP_FILE} at $(date)."
