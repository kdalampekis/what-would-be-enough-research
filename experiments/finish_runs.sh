#!/usr/bin/env bash
# Runbook for the end of the held-out and robustness runs. Each stage is safe to repeat.
#   experiments/finish_runs.sh status    what is done, what is still open, attempts used
#   experiments/finish_runs.sh fill      one more resumable pass for every model (same settings; a job is never
#                                        tried more than 3 times in total; completed jobs are not re-requested)
#   experiments/finish_runs.sh analyze   frozen analyses, exploratory split, figures, tables (no model calls)
#   experiments/finish_runs.sh archive   compress the raw responses of these runs, by pool, for the repository
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
CAP=519.4324
MODELS="adaption-qwen3.5-397b adaption-qwen3.8-27b adaption-deepseek-v4-flash adaption-gemma-4-26b-a4b-it-schema"
ALL=$(echo $MODELS | tr ' ' ',')
case "${1:-status}" in
status)
  $PY - <<'PY'
import glob, json, os, collections
ref = os.path.getmtime("data/FREEZE_FINAL.json")
done, att = collections.Counter(), collections.Counter()
for f in glob.glob("results/raw/pilot/*/adaption-*/*.json"):
    if os.path.getmtime(f) < ref:
        continue
    pool, model, name = f.split("/")[-3:]
    if ".attempt" in name:
        att[(model, name.split(".")[0], pool)] += 1
    else:
        done[model] += 1
final = {(f.split("/")[-2], os.path.basename(f).split(".")[0], f.split("/")[-3])
         for f in glob.glob("results/raw/pilot/*/adaption-*/*.json") if ".attempt" not in f}
open_jobs = collections.Counter()
for (model, job, pool), n in att.items():
    if (model, job, pool) not in final:
        open_jobs[(model, n)] += 1
for m in sorted(done):
    print(m.replace("adaption-", ""), "completed", done[m], "of", 5567 + 2192,
          "| still failed after 1/2/3 attempts:", [open_jobs[(m, k)] for k in (1, 2, 3)])
PY
  grep -h "chain done" results/raw/final_chain_*.log results/raw/robust_chain_*.log | wc -l | xargs echo "chains finished (of 8):"
  ;;
fill)
  for M in $MODELS; do
    (experiments/chain_final.sh "$M" 8 $CAP; experiments/chain_robust.sh "$M" 6 $CAP) &
  done
  wait
  ;;
analyze)
  experiments/final_finalize.sh
  $PY experiments/run_robust.py --models $ALL --analyze-only --out results/aggregate/robust_dev
  $PY experiments/analyze_recertification.py --split test --out results/aggregate/final_test/recertification
  $PY experiments/render_eop.py results/aggregate/final_test/eop/eop_summary.json > results/aggregate/final_test/eop/eop_tables.md
  $PY experiments/make_figures.py --eop results/aggregate/final_test/eop/eop_summary.json --set v3test --t1-set t1test --label test
  $PY experiments/make_figures.py --robust results/aggregate/robust_dev/robust_summary.json
  $PY experiments/make_figures.py --eop results/aggregate/eop_dev/eop_summary.json --set v3dev --t1-set t1b --label dev --architecture
  ;;
archive)
  for d in results/raw/pilot/*/; do
    pool=$(basename "$d")
    n=$(find "$d" -name '*.json' -newer data/FREEZE_FINAL.json | wc -l | tr -d ' ')
    [ "$n" = 0 ] && continue
    out=results/raw/final_runs_${pool}_2026-11-15.tar.gz
    find "$d" -name '*.json' -newer data/FREEZE_FINAL.json | sort | tar -czf "$out" -T -
    echo "$out: $n files, $(du -h "$out" | cut -f1)"
  done
  tar -czf results/raw/final_runs_logs_ledger_2026-11-15.tar.gz results/raw/pilot/run_log.jsonl results/raw/pilot/spend_ledger_credits.jsonl
  ;;
esac
