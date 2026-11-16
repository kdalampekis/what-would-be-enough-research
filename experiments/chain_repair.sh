#!/usr/bin/env bash
# Study 3 for one model (PREREG_REPAIR.md): first answers (two passes), then repair calls (two passes).
# Resumable; completed jobs are never re-requested; a job is tried at most 3 times in total.
# Usage: experiments/chain_repair.sh MODEL_KEY CONCURRENCY BUDGET_CAP
set -u
M="$1"; C="$2"; CAP="$3"
cd "$(dirname "$0")/.."
LOG=results/raw/repair_chain_${M}.log
for stage in 1 1 2 2; do
  echo "=== $(date -u +%FT%TZ) stage $stage" >> "$LOG"
  PYTHONUNBUFFERED=1 .venv/bin/python experiments/run_repair.py --stage "$stage" --models "$M" \
    --max-calls 800 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
done
echo "=== $(date -u +%FT%TZ) chain done" >> "$LOG"
