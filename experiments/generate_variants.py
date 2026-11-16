"""Generate E10 (cost), E11 (risk) and E12 (shift) variants from a family pool. No model calls.

    python experiments/generate_variants.py --pool data/generated/pool_v2/instances.jsonl \
        --out data/generated/variants_v2

Each variant keeps its source family's id and split. Labels come from the oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from msep.benchmark import variants

ROOT = Path(__file__).resolve().parents[1]
RISK_SIBLINGS = ("ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=str(ROOT / "data" / "generated" / "pool_v2" / "instances.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data" / "generated" / "variants_v2"))
    ap.add_argument("--max-families", type=int, default=None)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.pool)]
    if a.max_families:
        keep = sorted({r["family_id"] for r in recs})[: a.max_families]
        recs = [r for r in recs if r["family_id"] in set(keep)]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    files = {k: open(out / f"{k}.jsonl", "w") for k in ("cost", "risk", "shift")}
    for r in recs:
        for v in variants.cost_sweep(r):
            files["cost"].write(json.dumps(v) + "\n")
            counts["cost"] += 1
        if r["sibling_type"] in RISK_SIBLINGS:
            for v in variants.risk_variants(r, seed=0):
                files["risk"].write(json.dumps(v) + "\n")
                counts["risk"] += 1
        for fn in (variants.shift_width, variants.shift_depth, variants.shift_skin):
            v = fn(r)
            if v is not None:
                files["shift"].write(json.dumps(v) + "\n")
                counts[f"shift_{v['variant']['axis']}"] += 1
    for f in files.values():
        f.close()
    manifest = {"pool": a.pool, "counts": dict(counts),
                "sha256": {k: hashlib.sha256((out / f"{k}.jsonl").read_bytes()).hexdigest() for k in files}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
