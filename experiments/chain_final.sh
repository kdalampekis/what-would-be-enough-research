#!/usr/bin/env bash
# Held-out (test split) evaluation chain for one model (PREREG_FINAL.md). All steps resumable: completed
# jobs are cached by job id and never re-requested; failed jobs are retried up to 3 attempts in total.
# Order = priority: v3 native, EOP on v3, T1 native, EOP extraction on T1, structured prompt on T1; then a fill pass.
# Usage: experiments/chain_final.sh MODEL_KEY CONCURRENCY BUDGET_CAP
set -u
M="$1"; C="$2"; CAP="$3"
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DATA=data/generated/pool_v3/instances.jsonl
T1=data/generated/t1_v1/pairs.jsonl
LOG=results/raw/final_chain_${M}.log
# frozen EOP extraction per model: v2 prompt; gemma +schema keeps the registered v1 prompt under its forced schema
if [ "$M" = "adaption-gemma-4-26b-a4b-it-schema" ]; then EX=s3; else EX=s3v2; fi
step() { echo "=== $(date -u +%FT%TZ) $*" >> "$LOG"; }
eop() { PYTHONUNBUFFERED=1 $PY experiments/run_eop.py --allow-test --items "$1" --conditions "$2" --models "$M" \
          --max-calls 1000 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1; }
for pass in 1 2; do
  step "pass $pass: v3 test native (E1-E9, three modes)"
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits test --allow-test --allow-full-split --models "$M" \
    --max-calls 2000 --concurrency "$C" --budget "$CAP" --out "results/aggregate/final_test/by_model/$M" >> "$LOG" 2>&1
  step "pass $pass: EOP v3 test extraction"; eop v3test $EX
  step "pass $pass: EOP v3 test structured prompt"; eop v3test s1
  step "pass $pass: T1 test native"
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits test --allow-test --allow-full-split \
    --experiments t1 --t1 $T1 --models "$M" --max-calls 900 --concurrency "$C" --budget "$CAP" >> "$LOG" 2>&1
  step "pass $pass: EOP T1 test extraction"; eop t1test $EX
  step "pass $pass: EOP T1 test structured prompt"; eop t1test s1
done
step "chain done"
