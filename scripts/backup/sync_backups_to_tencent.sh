#!/usr/bin/env bash
set -euo pipefail

# Sync backup files from Aliyun to Tencent entry host.

PROJECT_DIR="${PROJECT_DIR:-/opt/hr_system}"
LOCAL_BACKUP_DIR="${LOCAL_BACKUP_DIR:-${PROJECT_DIR}/backups/postgres}"

TENCENT_HOST="${TENCENT_HOST:-159.75.138.185}"
TENCENT_USER="${TENCENT_USER:-ubuntu}"
TENCENT_DIR="${TENCENT_DIR:-/home/ubuntu/hr-backups/postgres}"
TENCENT_RETENTION_DAYS="${TENCENT_RETENTION_DAYS:-30}"
SSH_KEY="${SSH_KEY:-/root/.ssh/id_ed25519_backup}"

SSH_OPTS=(
  -o StrictHostKeyChecking=accept-new
  -o ConnectTimeout=10
  -i "${SSH_KEY}"
)

mkdir -p "${LOCAL_BACKUP_DIR}"

echo "[sync] prepare remote dir"
ssh "${SSH_OPTS[@]}" "${TENCENT_USER}@${TENCENT_HOST}" "mkdir -p '${TENCENT_DIR}'"

if command -v rsync >/dev/null 2>&1; then
  echo "[sync] rsync -> ${TENCENT_USER}@${TENCENT_HOST}:${TENCENT_DIR}"
  rsync -az --delete \
    -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10" \
    --include='*/' --include='*.sql.gz' --exclude='*' \
    "${LOCAL_BACKUP_DIR}/" "${TENCENT_USER}@${TENCENT_HOST}:${TENCENT_DIR}/"
else
  echo "[sync] rsync not found, fallback to scp"
  shopt -s nullglob
  files=("${LOCAL_BACKUP_DIR}"/*.sql.gz)
  if (( ${#files[@]} > 0 )); then
    scp "${SSH_OPTS[@]}" "${files[@]}" "${TENCENT_USER}@${TENCENT_HOST}:${TENCENT_DIR}/"
  fi
fi

echo "[sync] remote retention: keep ${TENCENT_RETENTION_DAYS} days"
ssh "${SSH_OPTS[@]}" "${TENCENT_USER}@${TENCENT_HOST}" \
  "find '${TENCENT_DIR}' -type f -name '*.sql.gz' -mtime +${TENCENT_RETENTION_DAYS} -print -delete || true"

echo "[sync] finished"
