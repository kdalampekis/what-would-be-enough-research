"""T1B analysis (PREREG_T1B.md): over-intervention after an intervention makes the state sufficient.

No API calls. Reads T1 responses (pool plan_t1) for dev families ranked 31–72 and the v3 dev End-to-End
responses (pool plan) for the native ALREADY_SUFFICIENT contrast.

    python experiments/analyze_t1b.py --models adaption-qwen3.5-397b,adaption-qwen3.8-27b,\
adaption-gemma-4-26b-a4b-it-schema,adaption-deepseek-v4-flash --out results/aggregate/t1b_dev
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_t1  # noqa: E402

from msep.eval import pilot  # noqa: E402
from msep.eval.bootstrap import holm  # noqa: E402
from msep.models.runner import load_results  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SKIP = 30
REPS, SEED, THRESH = 10_000, 0, 0.05


def outcomes(row: dict, rec: dict) -> dict:
    v = row.get("valid", False)
    plan = row.get("plan_formal") or []
    said = row.get("state_sufficient_said")
    kinds = {p.split("_")[0] for p in plan}
    truth = rec["true_target_value"]
    return {"family_id": rec["family_id"], "parsed": v,
            "O1": (not v) or bool(plan),  # unparsed counts as failure on the all-attempted basis
            "O2": v and said is True and not plan and row.get("decision") == ("true" if truth else "false"),
            "O3": v and said is True and bool(plan),
            "O4": v and "COMPUTE" in kinds, "O5": v and "ASK" in kinds,
            "O6": len(plan) if v else None, "O7": v and not plan}


def _rate(items, key):
    xs = [x[key] for x in items if x[key] is not None]
    return sum(xs) / len(xs) if xs else None


def boot(b_items: list[dict], n_items: list[dict]) -> dict:
    fams = sorted({x["family_id"] for x in b_items} | {x["family_id"] for x in n_items})
    bf, nf = defaultdict(list), defaultdict(list)
    for x in b_items:
        bf[x["family_id"]].append(x)
    for x in n_items:
        nf[x["family_id"]].append(x)
    rng = random.Random(SEED)
    o1, diff = [], []
    for _ in range(REPS):
        s = [rng.choice(fams) for _ in fams]
        b = [x for f in s for x in bf[f]]
        n = [x for f in s for x in nf[f]]
        rb, rn = _rate(b, "O1"), _rate(n, "O1")
        if rb is not None:
            o1.append(rb)
        if rb is not None and rn is not None:
            diff.append(rb - rn)
    q = lambda d, p: sorted(d)[int(p * (len(d) - 1))] if d else None  # noqa: E731
    pb, pn = _rate(b_items, "O1"), _rate(n_items, "O1")
    return {"O1_into_AS": {"mean": pb, "lo95": q(o1, 0.025), "hi95": q(o1, 0.975), "one_sided_lo95": q(o1, 0.05),
                           "p_T_OI_1": sum(v <= THRESH for v in o1) / len(o1) if o1 else None},
            "O1_native_AS": pn,
            "diff_into_minus_native": {"mean": None if pb is None or pn is None else pb - pn,
                                       "lo95": q(diff, 0.025), "hi95": q(diff, 0.975),
                                       "p_T_OI_2": sum(v <= 0 for v in diff) / len(diff) if diff else None},
            "n_into_AS": len(b_items), "n_native_AS": len(n_items), "families": len(fams)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--t1", default=str(ROOT / "data" / "generated" / "t1_v1" / "pairs.jsonl"))
    ap.add_argument("--models", required=True)
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "t1b_dev"))
    a = ap.parse_args(argv)
    t1 = analyze_t1.select_t1(Path(a.data), Path(a.t1), ("dev",), SKIP, None)
    by_id = {r["instance_id"]: r for r in t1}
    fams = {r["family_id"] for r in t1}
    base = {r["instance_id"]: r for r in pilot.load_records(Path(a.data), ("dev",), None) if r["family_id"] in fams}
    native_ids = {i for i, r in base.items() if r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT"}
    raw = Path(a.raw)
    summary = {"families": len(fams), "pairs": len(t1) // 2, "models": {}}
    p1, p2 = {}, {}
    for k in [m.strip() for m in a.models.split(",") if m.strip()]:
        res = [r for r in load_results(raw, "plan_t1", k) if r["instance_id"] in by_id]
        rows = {r["instance_id"]: r for r in pilot.score_plan_results(by_id, res)}
        b_items = []
        desc = defaultdict(list)
        for r in t1:
            if r["t1"]["role"] != "B" or r["t1"]["class_b"] != "ALREADY_SUFFICIENT":
                continue
            o = outcomes(rows.get(r["instance_id"], {"valid": False}), r)
            b_items.append(o)
            desc[f"edit={r['t1']['edit']}"].append(o)
            desc[f"class_a={r['t1']['class_a']}"].append(o)
        nres = [r for r in load_results(raw, "plan", k) if r["instance_id"] in native_ids and r["mode"] == "end_to_end"]
        nrows = {r["instance_id"]: r for r in pilot.score_plan_results(base, nres)}
        n_items = [outcomes(nrows.get(i, {"valid": False}), base[i]) for i in sorted(native_ids)]
        s = boot(b_items, n_items)
        s["descriptive_into_AS"] = {key: _rate(b_items, key) for key in ("O1", "O2", "O3", "O4", "O5", "O6", "O7")}
        s["by_stratum_O1"] = {kk: {"n": len(v), "O1": _rate(v, "O1")} for kk, v in sorted(desc.items())}
        s["missing_into_AS_responses"] = sum(1 for r in t1 if r["t1"]["role"] == "B" and r["t1"]["class_b"] ==
                                             "ALREADY_SUFFICIENT" and r["instance_id"] not in rows)
        s["missing_native_responses"] = len(native_ids) - len(nrows)
        prs = analyze_t1.pair_rows(t1, res)
        s["pairs_all"] = analyze_t1.bootstrap(prs)
        s["pairs_into_AS"] = analyze_t1.bootstrap([p for p in prs if p["into_AS"]])
        p1[k], p2[k] = s["O1_into_AS"]["p_T_OI_1"], s["diff_into_minus_native"]["p_T_OI_2"]
        summary["models"][k] = s
    h1 = holm({k: v for k, v in p1.items() if v is not None})
    h2 = holm({k: v for k, v in p2.items() if v is not None})
    for k, s in summary["models"].items():
        s["T_OI_1"] = {"p": p1[k], "holm_p": h1.get(k), "supported": h1.get(k) is not None and h1[k] < 0.05}
        s["T_OI_2"] = {"p": p2[k], "holm_p": h2.get(k), "supported": h2.get(k) is not None and h2[k] < 0.05}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "t1b_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: {"O1": v["O1_into_AS"], "native": v["O1_native_AS"], "diff": v["diff_into_minus_native"],
                          "T_OI_1": v["T_OI_1"], "T_OI_2": v["T_OI_2"]} for k, v in summary["models"].items()},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
