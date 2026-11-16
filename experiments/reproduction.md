# Reproduction

This page says what can be reproduced without any model call, how, and what we observed when we did it ourselves.

## What we checked, and when

On 2026-11-16 (UTC) we exported this repository into an empty directory, created a fresh Python environment, and ran every step below from the exported files only. Python 3.14 on macOS.

| Step | Result |
|---|---|
| Install (`pip install -e ".[dev]" matplotlib markdown`) | succeeded |
| Rebuild all datasets (benchmark, variants, counterfactual pairs, rewordings, follow-up items) | succeeded, about one minute |
| Freeze checks: benchmark v3, T1, FINAL, ROBUST, FOLLOWUP, REPAIR | all pass (in our first trial ROBUST failed because we had moved a pinned file; the export now keeps every pinned file in place and checks this) |
| Test suite | 777 passed, 2 skipped |
| Unpack the raw model responses | 83,892 response files |
| Re-run every analysis: held-out, rewording, exploratory re-certification split, follow-up Studies 1–3, the Study 3 supplement, tables, figures, report tables | all succeeded, about 16 minutes |

**What changed on re-running:** nothing that is reported. The only differences from the committed files were:

- three planner timing fields (`planner_seconds_mean`, wall-clock milliseconds) in `results/aggregate/robust_dev/robust_summary.json` and `results/aggregate/repair/repair_summary.json`;
- the SVG versions of the figures, which embed a creation time; every PNG figure was byte-identical;
- run logs that the analysis appends to.

Every result table, test outcome, interval and PNG figure came out identical.

## How to do it

Needs Python 3.11 or newer.

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]" matplotlib markdown
```

Rebuild the datasets and verify them against the freeze records:

```bash
PY=.venv/bin/python
$PY experiments/generate_benchmark.py --template v3 --families 300 --out data/generated/pool_v3
$PY experiments/generate_variants.py --pool data/generated/pool_v3/instances.jsonl --out data/generated/variants_v3
$PY experiments/generate_t1.py
$PY experiments/generate_robust.py
$PY experiments/generate_followup.py
$PY experiments/run_repair.py --generate
$PY experiments/freeze_benchmark.py --verify
$PY experiments/freeze_t1.py --verify
for n in FINAL ROBUST FOLLOWUP REPAIR; do $PY experiments/freeze_protocol.py --name $n --verify; done
$PY -m pytest -q
```

Unpack the raw model responses. Some archives store paths from the repository root, older ones from `results/raw`:

```bash
for a in results/raw/*.tar.gz; do
  if tar -tzf "$a" | head -n 1 | grep -q '^results/'; then tar -xzf "$a"; else tar -xzf "$a" -C results/raw; fi
done
```

Re-run the analyses:

```bash
experiments/finish_runs.sh analyze          # held-out, rewording, re-certification split, figures, result tables
$PY experiments/run_followup.py --analyze-only --models adaption-qwen3.5-397b,adaption-qwen3.8-27b,adaption-gemma-4-26b-a4b-it-schema
$PY experiments/run_repair.py --analyze-only --models adaption-gemma-4-26b-a4b-it-schema,adaption-deepseek-v4-flash
$PY experiments/repair_supplement.py > results/aggregate/repair/repair_supplement.json
(cd paper && ../$PY fill_report.py && ../$PY build_report.py)   # report tables; the PDF build needs Google Chrome
```

Then `git status` shows what changed. Expect only the items listed above.

The development-split analyses are reproduced the same way; the commands are in the [experiment registry](experiment_registry.md) next to each experiment.

## What cannot be reproduced offline

Re-running the models themselves needs an API key and spends provider credits, and hosted models can change. The served model identifier is recorded in every raw response. Instructions: [`docs/RUNNING.md`](../docs/RUNNING.md). Results of a new run are new evidence, not a reproduction of ours.

## Raw responses

The archives in `results/raw/` hold every response we received, including failed attempts, with the prompt hash, settings, served model, token counts and cost. Local file paths in the logs were replaced by `PROJECT_ROOT`. The model outputs are not licensed by us; the provider's terms apply ([`DATA_LICENSE.md`](../LICENSES/DATA_LICENSE.md)).
