#!/usr/bin/env bash
# Held-out analyses (PREREG_FINAL.md), run once after all four chains are done. No model calls.
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
DATA=data/generated/pool_v3/instances.jsonl
ALL=adaption-qwen3.5-397b,adaption-qwen3.8-27b,adaption-gemma-4-26b-a4b-it-schema,adaption-deepseek-v4-flash
LOG=results/raw/final_finalize.log
echo "=== $(date -u +%FT%TZ) analyses" >> $LOG
$PY experiments/run_pilot.py --data $DATA --splits test --allow-test --allow-full-split --analyze-only --models $ALL \
  --out results/aggregate/final_test/v3 >> $LOG 2>&1
$PY experiments/run_eop.py --allow-test --items v3test,t1test --models $ALL --analyze-only \
  --out results/aggregate/final_test/eop >> $LOG 2>&1
$PY experiments/analyze_final.py --models $ALL --out results/aggregate/final_test/t1 >> $LOG 2>&1
echo "=== $(date -u +%FT%TZ) done" >> $LOG
