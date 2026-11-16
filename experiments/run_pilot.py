"""Phase 2 pilot driver for E1, E3, E5, E7 (shared job pools, one call per prompt per model).

    # count calls and estimate cost; no API calls
    python experiments/run_pilot.py --data data/generated/pool_v1/instances.jsonl --splits dev --dry-run
    # one real call per model; stops on any error
    python experiments/run_pilot.py --data ... --splits dev --smoke
    # run (resumable) and analyse
    python experiments/run_pilot.py --data ... --splits dev --max-calls 3000
    # re-analyse saved raw responses only
    python experiments/run_pilot.py --data ... --splits dev --analyze-only

The test split is refused unless --allow-test is given (frozen final evaluation only).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from msep.eval import pilot
from msep.models.prompts import PROMPT_VERSION
from msep.eval.report import write_report
from msep.eval.summary import ALL_EXPERIMENTS, analyze_model
from msep.models.runner import MAX_ERROR_ATTEMPTS, estimate, latest_record, load_models, raw_path, run_jobs
from msep.envfile import load_env
from msep.models.config_check import currency
from msep.models.spend import Ledger

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ("e1", "e3", "e5", "e7")
POOLS_FOR = {"e1": {"plan", "decision"}, "e3": {"plan"}, "e5": {"plan", "judgment"}, "e7": {"plan"},
             "e14": {"plan", "capability"},  # e14 (computation-capability control) is opt-in
             "e10": {"plan_cost"},  # e10 (cost sweeps) is opt-in and needs --variants
             "t1": {"plan_t1"}}  # T1 counterfactual flips (Challenge Tier v4) is opt-in and needs --t1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--splits", default="dev")
    ap.add_argument("--max-families", type=int, default=None)
    ap.add_argument("--models", default="gpt-5.6-sol,claude-sonnet-5-5")
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--experiments", default=",".join(EXPERIMENTS))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate"))
    ap.add_argument("--max-calls", type=int, default=0, help="hard cap on new API calls per model")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--assumed-output-tokens", type=int, default=4000)
    ap.add_argument("--dry-run", action="store_true", help="count calls and estimate cost only")
    ap.add_argument("--dry-run-mock", default=None, metavar="AGENT",
                    help="run the whole pipeline with a SYNTHETIC mock agent instead of the models; no network")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    ap.add_argument("--allow-test", action="store_true")
    ap.add_argument("--allow-full-split", action="store_true")
    ap.add_argument("--budget-usd", "--budget", dest="budget_usd", type=float, default=0.0,
                    help="hard stop on cumulative estimated spend across all models and runs (ledger). "
                         "Default 0: no real call is possible until a budget is explicitly authorised")
    ap.add_argument("--override", action="append", default=[], metavar="MODEL.FIELD=VALUE",
                    help="per-model setting override, e.g. claude-sonnet-5-5.settings.max_tokens=4000 "
                         "or gpt-5.6-sol.settings.reasoning_effort=low (recorded in the summary)")
    ap.add_argument("--rerun-of", default=None, metavar="MODEL_KEY",
                    help="diagnostic subset: run only the jobs whose saved result under MODEL_KEY has a status in "
                         "--rerun-status. Writes raw results under the new model keys only; skips the analysis "
                         "and report (use experiments/analyze_calibration.py)")
    ap.add_argument("--rerun-status", default="truncated",
                    help="comma list of ok, truncated, error, refusal, parse_error (parse_error = saved result has a "
                         "parse error, any status)")
    ap.add_argument("--limit-jobs", type=int, default=None, help="with --rerun-of: keep only the first N selected jobs")
    ap.add_argument("--variants", default=None, metavar="DIR",
                    help="variant directory (e.g. data/generated/variants_v3); required by --experiments e10")
    ap.add_argument("--t1", default=None, metavar="PAIRS_JSONL",
                    help="T1 pairs file (data/generated/t1_v1/pairs.jsonl); required by --experiments t1")
    ap.add_argument("--skip-families", type=int, default=0,
                    help="skip the first N families (sorted ids) of the split before --max-families; "
                         "e.g. 10 skips the 10 dev calibration families")
    ap.add_argument("--e10-items", choices=("all", "flip"), default="all",
                    help="flip = only cost variants whose swept action is strictly cheaper than at the boundary "
                         "(relation 'below'): the only items where the base item's cheapest plan stops being cheapest")
    a = ap.parse_args(argv)
    loaded = load_env(ROOT / ".env")
    if loaded:
        print(f"loaded from .env: {sorted(loaded)}")

    splits = tuple(s.strip() for s in a.splits.split(","))
    if "test" in splits and not a.allow_test:
        print("refusing to touch the test split (frozen final evaluation); pass --allow-test only for that run")
        return 2
    exps = [e.strip() for e in a.experiments.split(",")]
    pools = set().union(*[POOLS_FOR[e] for e in exps])
    records = pilot.load_records(Path(a.data), splits, a.max_families)
    if a.skip_families:
        allr = pilot.load_records(Path(a.data), splits, None)
        fams = sorted({r["family_id"] for r in allr})[a.skip_families:]
        keep = set(fams[:a.max_families] if a.max_families is not None else fams)
        records = [r for r in allr if r["family_id"] in keep]
    by_id = {r["instance_id"]: r for r in records}
    jobs = [j for j in pilot.build_jobs(records) if j.pool in pools]
    if "capability" in pools:
        from msep.eval.experiments import build_capability_jobs
        jobs += build_capability_jobs(records)
    if "plan_cost" in pools:
        if not a.variants or not (Path(a.variants) / "cost.jsonl").exists():
            print("--experiments e10 needs --variants DIR containing cost.jsonl "
                  "(python experiments/generate_variants.py; check with freeze_benchmark.py --verify)")
            return 2
        from msep.eval.experiments import build_variant_jobs
        fams = {r["family_id"] for r in records}
        cost = [v for v in (json.loads(l) for l in open(Path(a.variants) / "cost.jsonl"))
                if v["family_id"] in fams and v.get("split") in splits]
        if a.e10_items == "flip":
            cost = [v for v in cost if v["variant"]["relation"] == "below"]
        by_id.update({v["instance_id"]: v for v in cost})
        jobs += build_variant_jobs(cost, "cost")
        print(f"E10 cost variants ({a.e10_items}): {len(cost)} items from {len({v['family_id'] for v in cost})} families")
    if "plan_t1" in pools:
        if not a.t1 or not Path(a.t1).exists():
            print("--experiments t1 needs --t1 PAIRS_JSONL (python experiments/generate_t1.py; check freeze_t1.py --verify)")
            return 2
        from msep.eval.experiments import build_variant_jobs
        fams = {r["family_id"] for r in records}
        t1 = [v for v in (json.loads(l) for l in open(a.t1)) if v["family_id"] in fams and v.get("split") in splits]
        by_id.update({v["instance_id"]: v for v in t1})
        jobs += build_variant_jobs(t1, "t1")
        print(f"T1 pairs: {len(t1) // 2} pairs ({len(t1)} items) from {len({v['family_id'] for v in t1})} families")
    models = load_models(Path(a.models_config))
    for ov in a.override:  # model-specific output-token / reasoning settings, without editing the config
        path, _, value = ov.partition("=")
        key, *fields = path.split(".")
        node = models[key]
        for f in fields[:-1]:
            node = node.setdefault(f, {})
        try:
            node[fields[-1]] = json.loads(value)
        except json.JSONDecodeError:
            node[fields[-1]] = value
    keys = [k.strip() for k in a.models.split(",")]
    raw = Path(a.raw)
    if a.rerun_of:
        if a.rerun_of in keys:
            print("--rerun-of must name the earlier condition, not one of the --models being run")
            return 2
        wanted = {s.strip() for s in a.rerun_status.split(",")}

        def selected(job) -> bool:
            rec = latest_record(raw, job, a.rerun_of)
            return rec is not None and (rec["status"] in wanted or ("parse_error" in wanted and bool(rec["parse_error"])))
        jobs = [j for j in jobs if selected(j)][:a.limit_jobs]
        print(f"--rerun-of {a.rerun_of} status in {sorted(wanted)}: {len(jobs)} jobs selected")
        if not jobs:
            return 2
    if a.dry_run_mock:
        # Same path as a real run (jobs, runner, ledger, analysis, report), with every model
        # replaced by a SYNTHETIC mock agent. No network. Output goes to a separate directory.
        import hashlib
        lookup = {hashlib.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in jobs}
        models = {f"dryrun-{k}": {"provider": "mock", "model_id": f"mock:{a.dry_run_mock}",
                                  "settings": {"agent": a.dry_run_mock, "lookup": lookup,
                                               "max_tokens": models[k]["settings"]["max_tokens"]},
                                  "prices": {"input_per_mtok": 0.0, "output_per_mtok": 0.0}} for k in keys}
        keys = list(models)
        raw = Path(a.out) / "dryrun" / "raw"
        a.out = str(Path(a.out) / "dryrun")
        a.max_calls = max(a.max_calls, len(jobs))
        print(f"DRY RUN with mock agent '{a.dry_run_mock}': no network, results marked SYNTHETIC")
    print(f"{len(records)} instances, {len({r['family_id'] for r in records})} families, "
          f"{len(jobs)} jobs per model; pools {dict(Counter(j.pool for j in jobs))}")

    if a.dry_run:
        for k in keys:
            print(k, estimate(jobs, models[k].get("prices") or {}, models[k]["settings"]["max_tokens"]),
                  "(output assumed at the cap: an upper bound)")
        return 0
    if not a.analyze_only and not a.dry_run_mock and a.budget_usd <= 0:
        print("real-model budget is $0 until explicitly authorised: pass --budget-usd (no calls made)")
        return 2
    if not a.analyze_only:
        if a.max_families is None and not a.allow_full_split:
            print("refusing to run a full split; pass --max-families N (authorised: calibration subset only)")
            return 2
        if a.max_calls <= 0 and not a.smoke:
            print("set --max-calls (hard cap on new calls per model); use --dry-run to see the count")
            return 2
        if not a.dry_run_mock:
            from msep.models.config_check import check_all
            errs, warns = check_all(models, keys)
            for w in warns:
                print("WARNING", w)
            if errs:
                for e in errs:
                    print("ERROR", e)
                print("configuration check failed: no calls made")
                return 2
        for k in keys:
            if not models[k].get("prices"):
                print(f"{k}: no prices configured, so the budget cannot be enforced; not running")
                return 2
        cur = currency(models[keys[0]])
        unit = "$" if cur == "usd" else "credits "
        ledger = Ledger(raw / ("spend_ledger.jsonl" if cur == "usd" else f"spend_ledger_{cur}.jsonl"), a.budget_usd)
        print(f"budget {unit}{a.budget_usd:.2f}; already spent {unit}{ledger.spent:.2f}")
        # smoke gate: one plan job per model through the same accounted path
        probe = next(j for j in jobs if j.pool.split("_")[0] == "plan")
        for k in keys:
            counts = run_jobs([probe], k, models[k], raw, max_calls=1, ledger=ledger)
            rec = latest_record(raw, probe, k)
            ok = rec is not None and rec["status"] == "ok" and rec["parsed"] is not None
            if a.rerun_of and rec is not None and rec["status"] == "truncated":
                # a re-run of items selected because they failed before: a repeat failure is a result,
                # not a connector fault, so the gate only requires that the call came back
                print("  (re-run subset: a truncated probe passes the gate; the connector returned a response)")
                ok = True
            print(f"smoke {k}: status={rec and rec['status']} parse_error={rec and rec['parse_error']} "
                  f"tokens={rec and rec['tokens']} cost={unit}{(rec and rec['cost_usd']) or 0:.4f} "
                  f"served={rec and rec['served_model']} seconds={rec and rec['seconds']}")
            if rec is not None and rec["status"] == "error":
                print(f"  error: {str(rec['error'])[:300]}")
            if counts.get("retry_cap_reached"):
                print(f"  this job already failed {MAX_ERROR_ATTEMPTS} times; not retried")
            if not ok:
                print("smoke test failed: stopping before any further calls")
                return 1
        if a.smoke:
            print(f"smoke passed; spent so far {unit}{ledger.spent:.4f}")
            return 0
        for k in keys:
            print(k, run_jobs(jobs, k, models[k], raw, max_calls=a.max_calls, concurrency=a.concurrency, ledger=ledger))
        print(f"cumulative estimated spend {unit}{ledger.spent:.4f} of {unit}{a.budget_usd:.2f}")
    if a.rerun_of:
        print("diagnostic subset run: analysis and report skipped")
        return 0
    if exps == ["t1"]:
        print("T1 run: analysis is experiments/analyze_t1.py (pair metrics); the v3 report is not written")
        return 0

    summary = {"splits": list(splits), "families": len({r["family_id"] for r in records}),
               "prompt_version": PROMPT_VERSION, "models": keys, "experiments": exps, "overrides": a.override,
               "model_settings": {k: models[k].get("settings", {}) for k in keys
                                  if k in models and "lookup" not in models[k].get("settings", {})},
               "by_model": {}}
    train = pilot.load_records(Path(a.data), ("train",), None)
    for k in keys:
        summary["by_model"][k] = analyze_model(raw, k, by_id, experiments=[e for e in ALL_EXPERIMENTS if e in exps
                                                                           or e in ("e2", "e4", "e6", "e8", "e9")],
                                               train_records=train)
    # Shallow heuristic baselines on the same instances (deterministic, no network, no cost)
    import hashlib as _hl
    from msep.agents.heuristics import HEURISTICS
    from msep.eval import experiments as _ex
    from msep.models.runner import load_results as _lr
    hraw = raw / "heuristics"
    hjobs = [j for j in jobs if j.pool in ("plan", "judgment", "decision")]
    lookup = {_hl.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in hjobs}
    # visible-only fixed policies (no model, no oracle): simple intervention baselines
    policies = [(f"heuristic-{h}", h) for h in HEURISTICS] + [
        (f"policy-{p}", p) for p in ("always_answer", "always_ask", "always_compute", "always_abstain")]
    for hk, agent in policies:
        run_jobs(hjobs, hk, {"provider": "mock", "model_id": hk, "settings": {"agent": agent, "lookup": lookup, "max_tokens": 1},
                             "prices": {"input_per_mtok": 0.0, "output_per_mtok": 0.0}},
                 hraw, max_calls=len(hjobs), concurrency=1, log=lambda *_: None)
        summary["by_model"][hk] = analyze_model(hraw, hk, by_id, experiments=[e for e in ALL_EXPERIMENTS if e in
                                                                              ("e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9")],
                                                train_records=train)
        if hk.startswith("policy-"):  # visible-only deterministic policies: real baselines, not synthetic fixtures
            summary["by_model"][hk]["synthetic"] = False
    base_rows = pilot.score_plan_results(by_id, _lr(hraw, "plan", "heuristic-h1pp"))
    for k in keys:
        model_rows = pilot.score_plan_results(by_id, [r for r in _lr(raw, "plan", k) if r["instance_id"] in by_id])
        summary["by_model"][k]["versus_h1pp"] = _ex.versus_baseline(model_rows, base_rows)
    out = Path(a.out)
    tag = ("calibration_" if a.max_families else "pilot_") + "_".join(splits)
    report_dir = out / tag
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    write_report(summary, report_dir, title=f"Model results: {tag}")
    print(f"wrote {report_dir}/summary.json and report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
