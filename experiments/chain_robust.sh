#!/usr/bin/env bash
# Linguistic robustness chain for one model (PREREG_ROBUST.md). Resumable; completed jobs are never re-requested.
# Usage: experiments/chain_robust.sh MODEL_KEY CONCURRENCY BUDGET_CAP
set -u
M="$1"; C="$2"; CAP="$3"
cd "$(dirname "$0")/.."
LOG=results/raw/robust_chain_${M}.log
for pass in 1 2; do
  echo "=== $(date -u +%FT%TZ) pass $pass" >> "$LOG"
  PYTHONUNBUFFERED=1 .venv/bin/python experiments/run_robust.py --models "$M" --conditions frozen,s3v3,a,s1 \
    --max-calls 2300 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
done
echo "=== $(date -u +%FT%TZ) chain done" >> "$LOG"
