"""Held-out over-intervention analysis (PREREG_FINAL.md, F2): the PREREG_T1B outcomes and tests on the test split.

Same outcome definitions and bootstrap as experiments/analyze_t1b.py (imported unchanged); only the item
selection differs: all 63 test families, test T1 pairs, native ALREADY_SUFFICIENT siblings of the same families.

    python experiments/analyze_final.py --models M1,M2 --out results/aggregate/final_test/t1
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_t1  # noqa: E402
from analyze_t1b import _rate, boot, outcomes  # noqa: E402

from msep.eval import pilot  # noqa: E402
from msep.eval.bootstrap import holm  # noqa: E402
from msep.models.runner import load_results  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def extraction_match(data: Path, t1: Path, keys: list[str], raw: Path) -> dict:
    """Frozen EOP extraction (v2 pool where it has responses, else v1) against the exact parse of the same text."""
    import run_eop
    from msep.benchmark.parsing import parse_state
    from msep.controllers.llm_extractor import extraction_prompt, extraction_prompt_v2, state_from_extraction
    from msep.eval.extraction_match import compare
    from msep.models.runner import Job, latest_record
    out = {}
    for name in ("v3test", "t1test"):
        items = run_eop.load_items(name, data, t1)
        for k in keys:
            for label, pool, fn in (("v2", run_eop.C2_POOL[name], extraction_prompt_v2),
                                    ("v1", run_eop.SETS[name][2], extraction_prompt)):
                c = defaultdict(int)
                for r in items:
                    rec = latest_record(raw, Job(pool, r["instance_id"], r["family_id"], "extraction", fn(r["prompt_text"])), k)
                    if rec is None:
                        c["missing"] += 1
                        continue
                    c["responses"] += 1
                    if rec.get("parsed") is None:
                        c["invalid"] += 1
                        continue
                    try:
                        m = compare(state_from_extraction(rec["parsed"]), parse_state(r["prompt_text"], opaque_tasks=True))
                    except Exception:
                        c["invalid"] += 1
                        continue
                    c["exact"] += m["exact"]
                    for f in ("variables", "rules", "known", "actions"):
                        c[f"wrong_{f}"] += m[f] is not True
                if c["responses"]:
                    out[f"{name}|{k}|{label}"] = {"items": len(items), **dict(c)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--t1", default=str(ROOT / "data" / "generated" / "t1_v1" / "pairs.jsonl"))
    ap.add_argument("--models", required=True)
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "final_test" / "t1"))
    a = ap.parse_args(argv)
    base = {r["instance_id"]: r for r in pilot.load_records(Path(a.data), ("test",), None)}
    fams = {r["family_id"] for r in base.values()}
    t1 = [v for v in (json.loads(l) for l in open(a.t1)) if v["family_id"] in fams and v["split"] == "test"]
    by_id = {r["instance_id"]: r for r in t1}
    native_ids = {i for i, r in base.items() if r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT"}
    raw = Path(a.raw)
    summary = {"split": "test", "families": len(fams), "pairs": len(t1) // 2, "models": {}}
    p1, p2 = {}, {}
    for k in [m.strip() for m in a.models.split(",") if m.strip()]:
        res = [r for r in load_results(raw, "plan_t1", k) if r["instance_id"] in by_id]
        rows = {r["instance_id"]: r for r in pilot.score_plan_results(by_id, res)}
        b_items, desc = [], defaultdict(list)
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
        s["T_OI_2_descriptive"] = {"p": p2[k], "holm_p": h2.get(k)}
    summary["extraction_match"] = extraction_match(Path(a.data), Path(a.t1), list(summary["models"]), raw)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "t1_test_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(f"wrote {out / 't1_test_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
