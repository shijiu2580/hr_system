#!/usr/bin/env bash
set -euo pipefail

# Restore Aliyun PostgreSQL from latest backup on Tencent host.
# Usage:
#   ./restore_from_tencent_backup.sh                # restore latest
#   BACKUP_FILE=pg_xxx.sql.gz ./restore_from_tencent_backup.sh

PROJECT_DIR="${PROJECT_DIR:-/opt/hr_system}"
RESTORE_DIR="${RESTORE_DIR:-${PROJECT_DIR}/backups/restore}"

TENCENT_HOST="${TENCENT_HOST:-159.75.138.185}"
TENCENT_USER="${TENCENT_USER:-ubuntu}"
TENCENT_DIR="${TENCENT_DIR:-/home/ubuntu/hr-backups/postgres}"
SSH_KEY="${SSH_KEY:-/root/.ssh/id_ed25519_backup}"

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-hr-postgres}"
ENV_FILE="${ENV_FILE:-${PROJECT_DIR}/.env}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi
POSTGRES_DB="${POSTGRES_DB:-hr_system}"
POSTGRES_USER="${POSTGRES_USER:-hr_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change_me}"

SSH_OPTS=(
  -o StrictHostKeyChecking=accept-new
  -o ConnectTimeout=10
  -i "${SSH_KEY}"
)

mkdir -p "${RESTORE_DIR}"

if [[ -z "${BACKUP_FILE:-}" ]]; then
  echo "[restore] find latest backup on Tencent"
  BACKUP_FILE="$(ssh "${SSH_OPTS[@]}" "${TENCENT_USER}@${TENCENT_HOST}" "ls -1t '${TENCENT_DIR}'/*.sql.gz 2>/dev/null | head -n 1")"
  if [[ -z "${BACKUP_FILE}" ]]; then
    echo "[restore] no backup file found"
    exit 1
  fi
fi

LOCAL_FILE="${RESTORE_DIR}/$(basename "${BACKUP_FILE}")"

echo "[restore] download ${BACKUP_FILE}"
scp "${SSH_OPTS[@]}" "${TENCENT_USER}@${TENCENT_HOST}:${BACKUP_FILE}" "${LOCAL_FILE}"

echo "[restore] importing to ${POSTGRES_DB}"
gunzip -c "${LOCAL_FILE}" | docker exec -i "${POSTGRES_CONTAINER}" sh -lc "PGPASSWORD='${POSTGRES_PASSWORD}' psql -U '${POSTGRES_USER}' -d '${POSTGRES_DB}'"

echo "[restore] done"
