#!/usr/bin/env bash
set -euo pipefail

# PostgreSQL backup on Aliyun core host.
# - Uses pg_dump from container hr-postgres
# - Outputs compressed .sql.gz files
# - Keeps only latest N local backups
# - Optionally syncs to Tencent after backup

PROJECT_DIR="${PROJECT_DIR:-/opt/hr_system}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-hr-postgres}"
SYNC_AFTER_BACKUP="${SYNC_AFTER_BACKUP:-1}"

ENV_FILE="${ENV_FILE:-${PROJECT_DIR}/.env}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

POSTGRES_DB="${POSTGRES_DB:-hr_system}"
POSTGRES_USER="${POSTGRES_USER:-hr_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change_me}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
HOSTNAME_SHORT="$(hostname -s)"
OUT_FILE="${BACKUP_DIR}/pg_${POSTGRES_DB}_${HOSTNAME_SHORT}_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[backup] start: ${OUT_FILE}"
docker exec "${POSTGRES_CONTAINER}" sh -lc "PGPASSWORD='${POSTGRES_PASSWORD}' pg_dump -U '${POSTGRES_USER}' -d '${POSTGRES_DB}' --clean --if-exists --no-owner --no-privileges" \
  | gzip -c > "${OUT_FILE}"

echo "[backup] done: $(du -h "${OUT_FILE}" | awk '{print $1}')"

echo "[backup] cleanup: keep ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -type f -name '*.sql.gz' -mtime +"${RETENTION_DAYS}" -print -delete || true

if [[ "${SYNC_AFTER_BACKUP}" == "1" ]]; then
  if [[ -x "${PROJECT_DIR}/scripts/backup/sync_backups_to_tencent.sh" ]]; then
    "${PROJECT_DIR}/scripts/backup/sync_backups_to_tencent.sh"
  else
    echo "[backup] skip sync: sync script not found"
  fi
fi

echo "[backup] finished"
