"""Offline end-to-end run with SYNTHETIC mock agents. No network, no API, no cost.

    python experiments/run_offline.py --max-families 10

Runs every job pool (E1-E12) for every mock agent through the real runner,
writes raw records under results/synthetic/raw/, analyses them with the same
code the real pilot uses, and writes results/synthetic/{summary.json,report.md}
and figures. Everything produced is labelled SYNTHETIC: these are pipeline
tests, not research results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from msep.agents.heuristics import HEURISTICS
from msep.agents.mock import AGENTS, DESCRIPTIONS
from msep.eval import experiments as ex
from msep.eval import pilot
from msep.eval.summary import analyze_model
from msep.models.runner import run_jobs
from msep.models.spend import Ledger

ROOT = Path(__file__).resolve().parents[1]


def load_variants(directory: Path, families: set[str]) -> dict[str, list[dict]]:
    out = {}
    for kind in ("cost", "risk", "shift"):
        f = directory / f"{kind}.jsonl"
        out[kind] = [r for r in (json.loads(l) for l in open(f)) if r["family_id"] in families] if f.exists() else []
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=str(ROOT / "data" / "generated" / "pool_v2" / "instances.jsonl"))
    ap.add_argument("--variants", default=str(ROOT / "data" / "generated" / "variants_v2"))
    ap.add_argument("--splits", default="dev")
    ap.add_argument("--max-families", type=int, default=10)
    ap.add_argument("--agents", default=",".join(AGENTS))
    ap.add_argument("--out", default=str(ROOT / "results" / "synthetic"))
    ap.add_argument("--baselines-only", action="store_true",
                    help="run only the shallow heuristic baselines (real, non-LLM results; no SYNTHETIC banner)")
    a = ap.parse_args(argv)
    splits = tuple(a.splits.split(","))
    if "test" in splits:
        print("the offline run does not use the test split")
        return 2
    records = pilot.load_records(Path(a.pool), splits, a.max_families)
    fams = {r["family_id"] for r in records}
    train = [r for r in pilot.load_records(Path(a.pool), ("train",), None)]
    variants = load_variants(Path(a.variants), fams)
    all_records = records + [v for vs in variants.values() for v in vs]
    by_id = {r["instance_id"]: r for r in all_records}
    jobs = pilot.build_jobs(records) + ex.build_capability_jobs(records)
    for kind, recs in variants.items():
        jobs += ex.build_variant_jobs(recs, kind)
    out = Path(a.out)
    raw = out / "raw"
    print(f"SYNTHETIC offline run: {len(records)} instances + {len(all_records) - len(records)} variants, "
          f"{len(jobs)} jobs per agent")
    ledger = Ledger(raw / "spend_ledger.jsonl", budget_usd=0.0)
    agents = list(HEURISTICS) if a.baselines_only else a.agents.split(",")
    desc = {**DESCRIPTIONS, "h1": "HEURISTIC baseline: act on unknown variables in the rule defining Q (text only)",
            "h1p": "HEURISTIC baseline: h1 + aliases + NEITHER when an action is missing (text only)",
            "h1pp": "HEURISTIC baseline: h1p + one level of definition expansion (text only)"}
    summary = {"splits": list(splits), "families": len(fams), "agents": {},
               "agent_descriptions": {k: v for k, v in desc.items() if k in agents}, "by_model": {}}
    if any(x not in HEURISTICS for x in agents):
        summary["SYNTHETIC"] = "Mock agents (test fixtures). Not research results."
    lookup = {hashlib.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in jobs}
    for agent in agents:
        cfg = {"provider": "mock", "model_id": f"mock:{agent}", "settings": {"agent": agent, "lookup": lookup, "max_tokens": 1000},
               "prices": {"input_per_mtok": 0.0, "output_per_mtok": 0.0}}
        key = f"heuristic-{agent}" if agent in HEURISTICS else f"mock-{agent}"
        counts = run_jobs(jobs, key, cfg, raw, max_calls=len(jobs), concurrency=1, ledger=ledger,
                          log=lambda *_: None)
        summary["agents"][agent] = counts
        summary["by_model"][key] = analyze_model(raw, key, by_id, train_records=train)
        print(f"  {agent}: {counts['ok']} new, {counts['skipped_done']} cached")
    summary["spend_usd"] = ledger.spent
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    from msep.eval.report import write_report
    write_report(summary, out, title="SYNTHETIC offline run (mock agents)" if "SYNTHETIC" in summary
                 else "Shallow heuristic baselines (deterministic, no language model)")
    print(f"wrote {out / 'summary.json'} and {out / 'report.md'}; spend ${ledger.spent:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
