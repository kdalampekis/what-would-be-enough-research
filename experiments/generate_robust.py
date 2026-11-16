"""Build and validate the linguistic robustness set (PREREG_ROBUST.md).

Items: v3 dev families at positions 0, 4, 8, ... of the sorted family ids (18 of 72), every state, four
variants each (benchmark/rephrase.py). A variant record is the base record with a new id and prompt text;
state, oracle labels, handles and action names are the base record's.

Validation, for every variant: (1) the inverse parser recovers a state equal to the canonical one
(eval/extraction_match.py); (2) every handle and every action name of the canonical text occurs in the
variant; (3) generation is deterministic. Also recorded (no model involved): whether the benchmark's own
deterministic parser still recovers the state from the variant text.

    python experiments/generate_robust.py            # writes data/generated/robust_v1/
    python experiments/generate_robust.py --split train --check-only   # development check, writes nothing
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from msep.benchmark.parsing import parse_state
from msep.benchmark.rendering import render_state, rendering_from_json
from msep.benchmark.rephrase import GENERATOR_VERSION, KINDS, parse_blocks, render_variant
from msep.benchmark.schemas import instance_from_record
from msep.eval.extraction_match import compare

ROOT = Path(__file__).resolve().parents[1]
STEP = 4


def variants_of(rec: dict) -> list[dict]:
    state = instance_from_record(rec).state
    r = rendering_from_json(rec["rendering"])
    if render_state(state, r) != rec["prompt_text"]:
        raise ValueError(f"{rec['instance_id']}: canonical text not reproduced")
    out = []
    for kind in KINDS:
        text, blocks = render_variant(state, r, kind, rec["instance_id"])
        v = {**rec, "instance_id": f"{rec['instance_id']}-rb-{kind}", "prompt_text": text,
             "robust": {"of": rec["instance_id"], "kind": kind, "generator": GENERATOR_VERSION}}
        out.append((v, blocks))
    return out


def check(rec: dict, v: dict, blocks) -> dict:
    ref = parse_state(rec["prompt_text"], opaque_tasks=True)
    res = {"inverse_exact": compare(parse_blocks(blocks), ref)["exact"]}
    names = set(re.findall(r"\b(?:[FK]\d+|Q)\b", rec["prompt_text"])) | {a for a in rec["rendering"]["action_alias"].values()}
    res["names_present"] = all(re.search(rf"(?<![A-Za-z0-9_]){re.escape(n)}(?![A-Za-z0-9_])", v["prompt_text"]) for n in names)
    res["differs_from_canonical"] = v["prompt_text"] != rec["prompt_text"]
    try:
        res["benchmark_parser_exact"] = compare(parse_state(v["prompt_text"], opaque_tasks=True), ref)["exact"]
    except Exception:
        res["benchmark_parser_exact"] = False
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data" / "generated" / "robust_v1"))
    ap.add_argument("--split", default="dev", choices=("dev", "train"))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    recs = [r for r in (json.loads(l) for l in open(a.data)) if r["split"] == a.split]
    fams = sorted({r["family_id"] for r in recs})
    keep = set(fams[::STEP]) if a.split == "dev" else set(fams)
    recs = [r for r in recs if r["family_id"] in keep]
    items, stats, failures = [], defaultdict(Counter), []
    for rec in recs:
        again = [v["prompt_text"] for v, _ in variants_of(rec)]
        for (v, blocks), text2 in zip(variants_of(rec), again):
            c = check(rec, v, blocks)
            c["deterministic"] = v["prompt_text"] == text2
            kind = v["robust"]["kind"]
            stats[kind]["n"] += 1
            for k, ok in c.items():
                stats[kind][k] += bool(ok)
            if not (c["inverse_exact"] and c["names_present"] and c["deterministic"] and c["differs_from_canonical"]):
                failures.append({"instance_id": v["instance_id"], **c})
            items.append(v)
    summary = {"generator": GENERATOR_VERSION, "split": a.split, "families": len(keep), "base_items": len(recs),
               "variants": len(items), "by_kind": {k: dict(v) for k, v in stats.items()}, "failures": failures[:20],
               "n_failures": len(failures)}
    print(json.dumps({k: v for k, v in summary.items() if k != "failures"}, indent=1))
    for f in failures[:5]:
        print("FAIL", f)
    if a.check_only or failures:
        return 1 if failures else 0
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "items.jsonl", "w") as f:
        for v in items:
            f.write(json.dumps(v, sort_keys=True) + "\n")
    (out / "validation.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"wrote {out / 'items.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
