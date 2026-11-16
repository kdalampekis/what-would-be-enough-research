#!/usr/bin/env bash
# One follow-up study for one model (PREREG_FOLLOWUP.md). Resumable; completed jobs are never re-requested;
# a job is tried at most 3 times in total (two passes here, one fill pass if needed).
# Usage: experiments/chain_followup.sh MODEL_KEY STUDY CONCURRENCY BUDGET_CAP      STUDY = clarity | cost
set -u
M="$1"; STUDY="$2"; C="$3"; CAP="$4"
cd "$(dirname "$0")/.."
LOG=results/raw/followup_chain_${STUDY}_${M}.log
for pass in 1 2; do
  echo "=== $(date -u +%FT%TZ) $STUDY pass $pass" >> "$LOG"
  PYTHONUNBUFFERED=1 .venv/bin/python experiments/run_followup.py --study "$STUDY" --models "$M" \
    --max-calls 1000 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
done
echo "=== $(date -u +%FT%TZ) chain done" >> "$LOG"
