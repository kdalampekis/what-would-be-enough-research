"""Supplement to Study 3 (PREREG_REPAIR.md section 3): the paired interval of the change in the accepted-but-wrong
rate with repair. The registration names this interval; the frozen analysis script reports the two rates but not
the interval of their difference. Written after the frozen analysis had been run; it reads the same records
through the same functions and changes nothing else.

    python experiments/repair_supplement.py > results/aggregate/repair/repair_supplement.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_repair as rr  # noqa: E402
from msep.benchmark.parsing import parse_state  # noqa: E402
from msep.controllers.llm_extractor import state_from_extraction  # noqa: E402
from msep.eval.bootstrap import paired_diff_ci  # noqa: E402
from msep.eval.extraction_match import compare  # noqa: E402
from msep.models.runner import latest_record  # noqa: E402

RAW = rr.ROOT / "results" / "raw" / "pilot"
MODELS = ("adaption-gemma-4-26b-a4b-it-schema", "adaption-deepseek-v4-flash")


def wrong(d, ref) -> float:
    if d is None:
        return 0.0
    try:
        return float(not compare(state_from_extraction(d), ref)["exact"])
    except Exception:
        return 1.0


out = {}
its = rr.items()
for key in MODELS:
    for arm in rr.ARMS:
        pairs = []
        for r in its:
            ref = parse_state(r["canonical_text"], opaque_tasks=True)
            d1, _ = rr.read(latest_record(RAW, rr.job1(arm, key, r), key))
            d2 = d1
            if d1 is None and (j := rr.job2(arm, key, r, RAW)) is not None:
                d2, _ = rr.read(latest_record(RAW, j, key))
            pairs.append((r["family_id"], wrong(d2, ref), wrong(d1, ref)))
        out[f"{key} | {arm}"] = {"rise_in_accepted_but_wrong_with_repair": paired_diff_ci(pairs),
                                 "items_wrong_first": int(sum(b for _, _, b in pairs)),
                                 "items_wrong_with_repair": int(sum(a for _, a, _ in pairs))}
print(json.dumps(out, indent=1))
