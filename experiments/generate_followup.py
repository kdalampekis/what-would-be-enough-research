"""Datasets for the two follow-up studies (PREREG_FOLLOWUP.md). No model is involved in any choice made here.

clarity  the same states in two wordings: the benchmark's own (W0) and one that removes an ambiguity about
         which computational values are already known (W1). Only two lines of explanatory text differ.
cost     E10: cost sweeps across the exact price at which the cheapest sufficient plan changes, taken from
         the frozen variant file and re-verified here with the oracle.

Both use train-split families only; no train family was ever sent to a model.

    python experiments/generate_followup.py            # writes data/generated/followup_v1/ and a manifest
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from msep.benchmark.schemas import instance_from_record
from msep.oracle import minimal_plan

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data/generated/pool_v3/instances.jsonl"
T1 = ROOT / "data/generated/t1_v1/pairs.jsonl"
COST = ROOT / "data/generated/variants_v3/cost.jsonl"
OUT = ROOT / "data/generated/followup_v1"

CLARITY_FAMILIES = 60     # the first 60 train families in sorted order
COST_FAMILIES = 60        # the next train families in sorted order that have a complete cost sweep
CLASS_SIBLINGS = ("ALREADY_SUFFICIENT", "COMPUTATION_ONLY", "BOTH", "NEITHER")

HEADER_W0 = "Computational facts (each is fully determined by inputs shown here; its certified value is not yet known):"
HEADER_W1 = ("Computational facts (each is fully determined by inputs shown here; its certified value is unknown "
             "unless it is listed under \"Known so far\"):")
KNOWN_W0 = "Known so far: "
KNOWN_W1 = "Known so far (established values, including certified results of computations already run): "


def clarified(text: str) -> str:
    """W1: the same text with the two explanatory lines replaced. Nothing else changes."""
    assert text.count(HEADER_W0) <= 1 and text.count("\n" + KNOWN_W0) == 1
    out = text.replace(HEADER_W0, HEADER_W1).replace("\n" + KNOWN_W0, "\n" + KNOWN_W1)
    a, b = text.splitlines(), out.splitlines()
    changed = [x for x, y in zip(a, b) if x != y]
    assert len(a) == len(b) and all(x == HEADER_W0 or x.startswith(KNOWN_W0) for x in changed)
    return out


def exposed(rec: dict) -> bool:
    """The state offers a computation whose results are all listed as known already (where W0 is ambiguous)."""
    st = instance_from_record(rec).state
    known = set(st.known)
    return any(a.resource.value == "computation" and set(a.reveals) <= known for a in st.actions)


def check_oracle(rec: dict) -> None:
    st = instance_from_record(rec).state
    new, o = minimal_plan.solve(st).to_json(st), rec["oracle"]
    assert all(new[k] == o[k] for k in ("resource_class", "optimal_cost", "optimal_plans")), rec["instance_id"]


def clarity(train: list[dict], t1: list[dict]) -> tuple[list[dict], dict]:
    fams = sorted({r["family_id"] for r in train})[:CLARITY_FAMILIES]
    base = [r for r in train if r["family_id"] in fams and r["sibling_type"] in CLASS_SIBLINGS]
    into = [r for r in t1 if r["family_id"] in fams and r["t1"]["role"] == "B"
            and r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT"]
    out, n = [], Counter()
    for rec, group in [(r, "sibling") for r in base] + [(r, "edited_into_sufficient") for r in into]:
        check_oracle(rec)
        ex = exposed(rec)
        n[(group, rec["oracle"]["resource_class"], "exposed" if ex else "not_exposed")] += 1
        for w, text in (("W0", rec["prompt_text"]), ("W1", clarified(rec["prompt_text"]))):
            out.append({**rec, "instance_id": f"{rec['instance_id']}-{w}", "prompt_text": text,
                        "followup": {"study": "clarity", "of": rec["instance_id"], "wording": w, "group": group,
                                     "exposed": ex}})
    return out, {"families": len(fams), "states": len(out) // 2, "items": len(out),
                 "states_by_group_class_exposure": {" | ".join(k): v for k, v in sorted(n.items())},
                 "first_family": fams[0], "last_family": fams[-1]}


def cost(train_fams: list[str], used: set[str]) -> tuple[list[dict], dict]:
    sweeps = defaultdict(list)
    for l in open(COST):
        v = json.loads(l)
        if v["split"] == "train" and v["family_id"] not in used:
            sweeps[(v["family_id"], v["variant"]["of"], v["variant"]["action"])].append(v)
    ok, dropped = {}, Counter()
    for key, vs in sweeps.items():
        rel = {v["variant"]["relation"] for v in vs}
        if rel != {"below", "equal", "above"}:
            dropped["sweep without all three sides (a cost below 1 would be needed)"] += 1
            continue
        d, good = key[2], True
        for v in vs:  # independent re-verification with the oracle
            st = instance_from_record(v).state
            new = minimal_plan.solve(st).to_json(st)
            plans = [set(p) for p in new["optimal_plans"]]
            has = [d in p for p in plans]
            want = {"below": all(has), "above": not any(has), "equal": any(has) and not all(has)}[v["variant"]["relation"]]
            good &= want and new["optimal_cost"] == v["oracle"]["optimal_cost"] \
                and new["optimal_plans"] == v["oracle"]["optimal_plans"]
        if not good:
            dropped["sweep that failed the oracle re-verification"] += 1
            continue
        ok[key] = vs
    fams = [f for f in train_fams if any(k[0] == f for k in ok)][:COST_FAMILIES]
    out = []
    for key in sorted(ok):
        if key[0] in fams:
            for v in sorted(ok[key], key=lambda v: v["variant"]["cost"]):
                out.append({**v, "followup": {"study": "cost", "sweep": "|".join(key)}})
    return out, {"families": len(fams), "sweeps": len({r["followup"]["sweep"] for r in out}), "items": len(out),
                 "items_by_relation": dict(Counter(r["variant"]["relation"] for r in out)),
                 "sweeps_dropped_before_family_choice": dict(dropped),
                 "first_family": fams[0], "last_family": fams[-1]}


def main() -> int:
    train = [r for r in map(json.loads, open(POOL)) if r["split"] == "train"]
    t1 = [r for r in map(json.loads, open(T1)) if r["split"] == "train"]
    fams = sorted({r["family_id"] for r in train})
    cl, cl_info = clarity(train, t1)
    co, co_info = cost(fams, set(fams[:CLARITY_FAMILIES]))
    assert not {r["family_id"] for r in cl} & {r["family_id"] for r in co}
    OUT.mkdir(parents=True, exist_ok=True)
    sha = {}
    for name, rows in (("clarity.jsonl", cl), ("cost.jsonl", co)):
        (OUT / name).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        sha[name] = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
    man = {"generator": "followup-v1", "split": "train", "clarity": cl_info, "cost": co_info, "sha256": sha,
           "wording": {"header_W0": HEADER_W0, "header_W1": HEADER_W1, "known_W0": KNOWN_W0, "known_W1": KNOWN_W1}}
    (ROOT / "data/followup_v1_manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    print(json.dumps(man, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
