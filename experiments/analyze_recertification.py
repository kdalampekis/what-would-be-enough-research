"""Exploratory: when a model acts on a state that is already sufficient, what do its actions target?

Motivation (dev, 2026-11-14): the benchmark text says of every computational fact that "its certified value
is not yet known", while the "Known so far" line can list a computational fact, and most such states still
offer the computation action for it. A model that re-runs that computation may be following the header,
not failing to see that the question is settled. This script splits over-intervention on ALREADY_SUFFICIENT
states by whether the proposed actions reveal only values the text already lists as known.

Specified and committed before the held-out analysis; exploratory on both splits (no test, no threshold).

    python experiments/analyze_recertification.py --split dev  --out results/aggregate/recertification_dev
    python experiments/analyze_recertification.py --split test --out results/aggregate/final_test/recertification
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from msep.benchmark.schemas import instance_from_record  # noqa: E402
from msep.eval import pilot  # noqa: E402
from msep.models.runner import load_results  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-deepseek-v4-flash",
          "adaption-gemma-4-26b-a4b-it-schema")


def audit(items: dict, results: list[dict]) -> dict:
    scored = {r["instance_id"]: r for r in pilot.score_plan_results(items, results)}
    c = Counter({k: 0 for k in ("already_sufficient_items", "no_response", "unparsed", "empty_plan", "non_empty_plan",
                                "every_action_reveals_only_known_values", "some_action_reveals_an_unknown_value",
                                "a_computation_on_an_already_known_computational_fact", "plan_is_computation_only")})
    for i, rec in items.items():
        c["already_sufficient_items"] += 1
        s = scored.get(i)
        if s is None:
            c["no_response"] += 1
            continue
        if not s["valid"]:
            c["unparsed"] += 1
            continue
        if not s["plan_formal"]:
            c["empty_plan"] += 1
            continue
        c["non_empty_plan"] += 1
        st = instance_from_record(rec).state
        known = set(st.known)
        acts = [st.action_index[a] for a in s["plan_formal"] if a in st.action_index]
        only_known = bool(acts) and all(set(a.reveals) <= known for a in acts)
        c["every_action_reveals_only_known_values"] += only_known
        c["some_action_reveals_an_unknown_value"] += not only_known
        c["a_computation_on_an_already_known_computational_fact"] += any(
            a.resource.value == "computation" and set(a.reveals) <= known for a in acts)
        c["plan_is_computation_only"] += bool(acts) and all(a.resource.value == "computation" for a in acts)
    n = c["already_sufficient_items"]
    c = dict(c)
    c["rate_non_empty_plan"] = c.get("non_empty_plan", 0) / n if n else None
    c["rate_acting_on_an_unknown_value"] = c.get("some_action_reveals_an_unknown_value", 0) / n if n else None
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=("dev", "test"))
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--t1", default=str(ROOT / "data" / "generated" / "t1_v1" / "pairs.jsonl"))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    base = pilot.load_records(Path(a.data), (a.split,), None)
    fams = sorted({r["family_id"] for r in base})
    keep = set(fams[30:]) if a.split == "dev" else set(fams)  # dev: the T1B families, as registered there
    native = {r["instance_id"]: r for r in base if r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT"}
    into = {v["instance_id"]: v for v in (json.loads(l) for l in open(a.t1))
            if v["split"] == a.split and v["family_id"] in keep and v["t1"]["role"] == "B"
            and v["t1"]["class_b"] == "ALREADY_SUFFICIENT"}
    offered = sum(any(x.resource.value == "computation" and set(x.reveals) <= set(st.known) for x in st.actions)
                  for st in (instance_from_record(r).state for r in [*native.values(), *into.values()]))
    out = {"split": a.split, "exploratory": True,
           "states_offering_a_computation_for_a_known_computational_fact": {"n": offered, "of": len(native) + len(into)},
           "models": {}}
    raw = Path(a.raw)
    for k in MODELS:
        nat = [r for r in load_results(raw, "plan", k) if r["instance_id"] in native and r["mode"] == "end_to_end"]
        t1r = [r for r in load_results(raw, "plan_t1", k) if r["instance_id"] in into]
        out["models"][k] = {"native_already_sufficient": audit(native, nat),
                            "edited_into_already_sufficient": audit(into, t1r)}
    dst = Path(a.out)
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "recertification.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: {s: {x: v[s].get(x) for x in ("already_sufficient_items", "non_empty_plan",
                                                        "every_action_reveals_only_known_values",
                                                        "some_action_reveals_an_unknown_value")} for s in v}
                      for k, v in out["models"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
