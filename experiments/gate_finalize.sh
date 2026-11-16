#!/usr/bin/env bash
# Dev decision gate: one more resumable fill pass for every model/condition, then all registered analyses.
# No new conditions; failed jobs are retried within the runner's 3-attempt cap.
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DATA=data/generated/pool_v3/instances.jsonl
T1=data/generated/t1_v1/pairs.jsonl
CAP=519.4324
LOG=results/raw/gate_finalize.log
MODELS="adaption-qwen3.5-397b adaption-qwen3.8-27b adaption-gemma-4-26b-a4b-it-schema adaption-deepseek-v4-flash"
echo "=== $(date -u +%FT%TZ) fill pass" >> $LOG
for M in $MODELS; do
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits dev --allow-full-split --models $M --max-calls 2200 \
    --concurrency 6 --budget $CAP --out results/aggregate/v3dev_by_model/$M >> $LOG 2>&1
  PYTHONUNBUFFERED=1 $PY experiments/run_pilot.py --data $DATA --splits dev --skip-families 10 --allow-full-split \
    --experiments t1 --t1 $T1 --models $M --max-calls 900 --concurrency 6 --budget $CAP >> $LOG 2>&1
  for S in v3dev t1b t1pilot; do
    PYTHONUNBUFFERED=1 $PY experiments/run_eop.py --items $S --conditions s3,s1 --models $M --max-calls 1100 \
      --concurrency 6 --budget $CAP >> $LOG 2>&1
    if [ "$M" != "adaption-gemma-4-26b-a4b-it-schema" ]; then
      PYTHONUNBUFFERED=1 $PY experiments/run_eop.py --items $S --conditions s3v2 --models $M --max-calls 600 \
        --concurrency 6 --budget $CAP >> $LOG 2>&1
    fi
  done
done
echo "=== $(date -u +%FT%TZ) analyses" >> $LOG
ALL=$(echo $MODELS | tr ' ' ',')
$PY experiments/run_pilot.py --data $DATA --splits dev --allow-full-split --analyze-only --models $ALL \
  --out results/aggregate/v3dev >> $LOG 2>&1
$PY experiments/analyze_t1b.py --models $ALL --out results/aggregate/t1b_dev >> $LOG 2>&1
$PY experiments/run_eop.py --items v3dev,t1b,t1pilot --models $ALL --analyze-only --out results/aggregate/eop_dev >> $LOG 2>&1
echo "=== $(date -u +%FT%TZ) gate finalize done" >> $LOG
