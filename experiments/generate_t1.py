"""Generate and validate T1 (single-edit counterfactual flips) from the frozen v3 pool. No model calls.

    python experiments/generate_t1.py --pool data/generated/pool_v3/instances.jsonl --out data/generated/t1_v1

Writes pairs.jsonl (A then B for every pair) and validation.json. Exits non-zero if any check fails:
- A's prompt is byte-identical to the v3 record it comes from;
- A and B prompts differ in exactly one line (the "known" line) and have identical action menus;
- the SAT oracle and the brute-force oracle agree on every member;
- the optimal-plan set or the class differs between A and B (by construction).
"""

from __future__ import annotations

import argparse
import difflib
import json
from collections import Counter
from pathlib import Path

from msep.benchmark import t1_flips
from msep.benchmark.schemas import instance_from_record
from msep.oracle import solver
from msep.oracle.brute_force import BruteForce

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data" / "generated" / "t1_v1"))
    a = ap.parse_args(argv)
    recs = [json.loads(l) for l in open(a.pool)]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    v = Counter()
    stats: dict[str, Counter] = {k: Counter() for k in ("split", "edit_x_transition", "class_transition", "class_a",
                                                         "class_b", "diff_lines", "len_delta_chars", "drop_rule_ok")}
    problems: list[str] = []
    with open(out / "pairs.jsonl", "w") as fh:
        for r in recs:
            pair = t1_flips.make_pair(r)
            if not pair:
                v["base_without_flip"] += 1
                continue
            A, B = pair
            t = B["t1"]
            v["pairs"] += 1
            if A["prompt_text"] != r["prompt_text"]:
                problems.append(f"{t['pair_id']}: A prompt differs from v3")
            al, bl = A["prompt_text"].splitlines(), B["prompt_text"].splitlines()
            changed = [l for l in difflib.ndiff(al, bl) if l[:1] in "+-"]
            if len(changed) != 2 or len(al) != len(bl):
                problems.append(f"{t['pair_id']}: prompts differ in {len(changed)} diff lines")
            menu = lambda rec: sorted(x["name"] for x in rec["state"]["info_actions"] + rec["state"]["comp_actions"])  # noqa: E731
            if menu(A) != menu(B):
                problems.append(f"{t['pair_id']}: action menus differ")
            for m in (A, B):
                st = instance_from_record(m).state
                if solver.analyze(st).key() != BruteForce(st).analyze().key():
                    problems.append(f"{m['instance_id']}: SAT and brute-force oracles disagree")
            if ({frozenset(p) for p in A["oracle"]["optimal_plans"]} == {frozenset(p) for p in B["oracle"]["optimal_plans"]}
                    and A["oracle"]["resource_class"] == B["oracle"]["resource_class"]):
                problems.append(f"{t['pair_id']}: no change in optimal plans")
            stats["split"][r["split"]] += 1
            stats["edit_x_transition"][f"{t['edit']}|{t['transition']}"] += 1
            stats["class_transition"][f"{t['class_a']}->{t['class_b']}"] += 1
            stats["class_a"][t["class_a"]] += 1
            stats["class_b"][t["class_b"]] += 1
            stats["diff_lines"][len(changed)] += 1
            stats["len_delta_chars"][len(B["prompt_text"]) - len(A["prompt_text"])] += 1
            stats["drop_rule_ok"][t["drop_rule_ok"]] += 1
            fh.write(json.dumps(A) + "\n")
            fh.write(json.dumps(B) + "\n")
    report = {"generator": t1_flips.GENERATOR_VERSION, "base_records": len(recs), **v,
              "families_with_pairs": None, "checks_failed": len(problems), "problems": problems[:50],
              **{k: dict(sorted(c.items(), key=lambda kv: str(kv[0]))) for k, c in stats.items()}}
    fams = {json.loads(l)["family_id"] for l in open(out / "pairs.jsonl")}
    report["families_with_pairs"] = len(fams)
    (out / "validation.json").write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: report[k] for k in ("pairs", "base_without_flip", "families_with_pairs", "checks_failed",
                                             "split", "edit_x_transition")}, default=str))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
