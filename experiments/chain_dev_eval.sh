#!/usr/bin/env bash
# Dev evaluation chain for one model (all steps resumable; completed jobs are cached by job id):
#   1. v3 dev controlled evaluation (E1-E9, all three modes)         -> run_pilot.py
#   2. T1B prospective follow-up (dev families 31-72, End-to-End)    -> run_pilot.py --experiments t1
#   3. T1 pilot items, native (condition A for the EOP comparison)   -> run_pilot.py --experiments t1
#   4. EOP conditions C (extraction) and B (S1 prompt) on all sets   -> run_eop.py
#   5. one fill-in pass of 1-4 for transient failures (same settings; retry cap 3 attempts per job)
# Usage: experiments/chain_dev_eval.sh MODEL_KEY CONCURRENCY BUDGET_CAP
set -u
M="$1"; C="$2"; CAP="$3"
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DATA=data/generated/pool_v3/instances.jsonl
T1=data/generated/t1_v1/pairs.jsonl
LOG=results/raw/chain_${M}.log
step() { echo "=== $(date -u +%FT%TZ) $*" >> "$LOG"; }
for pass in 1 2; do
  step "pass $pass: v3 dev"
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits dev --allow-full-split --models "$M" \
    --max-calls 2200 --concurrency "$C" --budget "$CAP" --out "results/aggregate/v3dev_by_model/$M" >> "$LOG" 2>&1
  step "pass $pass: T1B"
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits dev --skip-families 30 --allow-full-split \
    --experiments t1 --t1 $T1 --models "$M" --max-calls 600 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
  step "pass $pass: T1 pilot native"
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits dev --skip-families 10 --max-families 20 \
    --experiments t1 --t1 $T1 --models "$M" --max-calls 300 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
  step "pass $pass: EOP"
  PYTHONUNBUFFERED=1 $PY experiments/run_eop.py --items v3dev,t1b,t1pilot --conditions s3,s1 --models "$M" \
    --max-calls 3500 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
done
step "chain done"
