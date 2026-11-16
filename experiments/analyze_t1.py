"""T1 analysis (pre-registered in PREREG_T1.md): item, pair and transition metrics from saved raw responses.

No API calls. Heuristic baselines (h1, h1p, h1++) are run here deterministically on the same T1 items.

    python experiments/analyze_t1.py --data data/generated/pool_v3/instances.jsonl \
        --t1 data/generated/t1_v1/pairs.jsonl --splits dev --skip-families 10 --max-families 20 \
        --models adaption-qwen3.5-397b,adaption-qwen3.8-27b,adaption-gemma-4-26b-a4b-it-schema \
        --out results/aggregate/t1_pilot_dev

Definitions (all on the *all-attempted* basis unless stated; an unparsed answer is incorrect):
- item correct: NEITHER -> decision "defer"; otherwise the plan is optimal (sufficient at minimum cost;
  on ALREADY_SUFFICIENT the empty plan).
- joint: both members of a pair correct.
- transition correct (pairs without a NEITHER member, both answers parsed; else incorrect): the model's
  change (A plan minus B plan, B plan minus A plan) equals the change between some optimal A plan and
  some optimal B plan.
- excess inconsistency (primary): joint − joint under a family-matched permutation that re-pairs each A
  with the B members of other pairs from the same family and the same transition stratum (keeps each
  member's accuracy, difficulty stratum and family-level dependence; breaks the specific edit link).
  Secondary: joint − Σ p(A stratum)·p(B stratum) (stratified independence).
- 95% intervals: family-clustered bootstrap (2,000 resamples, seed 0).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from msep.eval import pilot
from msep.eval.experiments import build_variant_jobs
from msep.models.runner import load_results, run_jobs

ROOT = Path(__file__).resolve().parents[1]
REPS, SEED = 2000, 0


def select_t1(data: Path, t1: Path, splits, skip: int, max_families: int | None) -> list[dict]:
    if "test" in splits:
        raise SystemExit("refusing the test split")
    base = pilot.load_records(data, splits, None)
    fams = sorted({r["family_id"] for r in base})[skip:]
    keep = set(fams[:max_families] if max_families is not None else fams)
    return [v for v in (json.loads(l) for l in open(t1)) if v["family_id"] in keep and v["split"] in splits]


def run_heuristics(t1: list[dict], raw: Path) -> list[str]:
    from msep.agents.heuristics import HEURISTICS
    by_id = {r["instance_id"]: r for r in t1}
    jobs = build_variant_jobs(t1, "t1")
    lookup = {hashlib.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in jobs}
    keys = []
    for h in HEURISTICS:
        k = f"heuristic-{h}"
        run_jobs(jobs, k, {"provider": "mock", "model_id": k, "settings": {"agent": h, "lookup": lookup, "max_tokens": 1},
                           "prices": {"input_per_mtok": 0.0, "output_per_mtok": 0.0}},
                 raw, max_calls=len(jobs), concurrency=1, log=lambda *_: None)
        keys.append(k)
    return keys


def _ok(row: dict, rec: dict) -> bool:
    if not row["valid"]:
        return False
    if rec["oracle"]["resource_class"] == "NEITHER":
        return row.get("decision") == "defer"
    return bool(row.get("plan_optimal"))


def _transition_ok(ra: dict, rb: dict, A: dict, B: dict) -> bool:
    if not (ra["valid"] and rb["valid"]):
        return False
    pa, pb = frozenset(ra.get("plan_formal") or []), frozenset(rb.get("plan_formal") or [])
    oa = [frozenset(p) for p in A["oracle"]["optimal_plans"]]
    ob = [frozenset(p) for p in B["oracle"]["optimal_plans"]]
    return any((pa - pb, pb - pa) == (x - y, y - x) for x in oa for y in ob)


def pair_rows(t1: list[dict], results: list[dict]) -> list[dict]:
    by_id = {r["instance_id"]: r for r in t1}
    rows = {r["instance_id"]: r for r in pilot.score_plan_results(by_id, results)}
    status = {r["instance_id"]: r["status"] for r in results}
    pairs = defaultdict(dict)
    for r in t1:
        pairs[r["t1"]["pair_id"]][r["t1"]["role"]] = r
    out = []
    for pid, m in sorted(pairs.items()):
        A, B = m["A"], m["B"]
        ra, rb = rows.get(A["instance_id"]), rows.get(B["instance_id"])
        missing = ra is None or rb is None
        ra = ra or {"valid": False}
        rb = rb or {"valid": False}
        t = B["t1"]
        neither = "NEITHER" in (t["class_a"], t["class_b"])
        out.append({
            "pair_id": pid, "family_id": A["family_id"], "missing": missing,
            "transition": t["transition"], "edit": t["edit"], "class_a": t["class_a"], "class_b": t["class_b"],
            "into_AS": t["class_b"] == "ALREADY_SUFFICIENT", "class_change": t["class_change"],
            "drop_rule_ok": t["drop_rule_ok"],
            "a_ok": _ok(ra, A), "b_ok": _ok(rb, B),
            "a_parsed": ra["valid"], "b_parsed": rb["valid"],
            "a_trunc": status.get(A["instance_id"]) == "truncated", "b_trunc": status.get(B["instance_id"]) == "truncated",
            "transition_eligible": not neither,
            "transition_ok": (not neither) and _transition_ok(ra, rb, A, B),
        })
    return out


# -- statistics ------------------------------------------------------------------------

def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def _stats(prs: list[dict], rng: random.Random | None = None) -> dict:
    a = _mean(p["a_ok"] for p in prs)
    b = _mean(p["b_ok"] for p in prs)
    joint = _mean(p["a_ok"] and p["b_ok"] for p in prs)
    te = [p for p in prs if p["transition_eligible"]]
    trans = _mean(p["transition_ok"] for p in te)
    # stratified independence
    sa, sb = defaultdict(list), defaultdict(list)
    for p in prs:
        sa[(p["class_a"], p["transition"], p["edit"])].append(p["a_ok"])
        sb[(p["class_b"], p["transition"], p["edit"])].append(p["b_ok"])
    pa = {k: _mean(v) for k, v in sa.items()}
    pb = {k: _mean(v) for k, v in sb.items()}
    indep = _mean(pa[(p["class_a"], p["transition"], p["edit"])] * pb[(p["class_b"], p["transition"], p["edit"])]
                  for p in prs)
    # family-matched permutation: all re-pairings of A with B's of other pairs in the same family+transition
    groups = defaultdict(list)
    for p in prs:
        groups[(p["family_id"], p["transition"])].append(p)
    perm_vals, n_with_partner = [], 0
    for g in groups.values():
        if len(g) < 2:
            continue
        n_with_partner += len(g)
        for x in g:
            perm_vals.extend(x["a_ok"] and y["b_ok"] for y in g if y is not x)
    within = [p for g in groups.values() if len(g) >= 2 for p in g]
    joint_within = _mean(p["a_ok"] and p["b_ok"] for p in within)
    perm = _mean(perm_vals)
    b_given_a = _mean(p["b_ok"] for p in prs if p["a_ok"])
    b_given_not_a = _mean(p["b_ok"] for p in prs if not p["a_ok"])
    return {"a": a, "b": b, "joint": joint, "transition": trans, "indep_expected": indep,
            "excess_vs_independence": None if joint is None or indep is None else joint - indep,
            "joint_within_permutable": joint_within, "perm_expected": perm,
            "excess_vs_family_perm": None if joint_within is None or perm is None else joint_within - perm,
            "b_given_a_ok": b_given_a, "b_given_a_wrong": b_given_not_a}


def bootstrap(prs: list[dict]) -> dict:
    point = _stats(prs)
    fams = sorted({p["family_id"] for p in prs})
    by_f = defaultdict(list)
    for p in prs:
        by_f[p["family_id"]].append(p)
    rng = random.Random(SEED)
    draws = defaultdict(list)
    for _ in range(REPS):
        sample = []
        for i, f in enumerate(rng.choice(fams) for _ in fams):
            # relabel resampled families so duplicates stay separate clusters for the permutation baseline
            sample.extend({**p, "family_id": f"{f}#{i}"} for p in by_f[f])
        for k, v in _stats(sample).items():
            if v is not None:
                draws[k].append(v)
    out = {"n_pairs": len(prs), "families": len(fams),
           "pairs_transition_eligible": sum(p["transition_eligible"] for p in prs),
           "pairs_with_perm_partner": sum(1 for p in prs if sum(q["family_id"] == p["family_id"] and
                                                                q["transition"] == p["transition"] for q in prs) > 1)}
    for k, v in point.items():
        d = sorted(draws[k])
        lo = d[int(0.025 * (len(d) - 1))] if d else None
        hi = d[int(0.975 * (len(d) - 1))] if d else None
        out[k] = {"mean": v, "lo": lo, "hi": hi}
    return out


def analyze(prs: list[dict]) -> dict:
    strata = {"all": prs,
              "direct": [p for p in prs if p["transition"] == "direct"],
              "indirect": [p for p in prs if p["transition"] == "indirect"],
              "E_OBS": [p for p in prs if p["edit"] == "E_OBS"], "E_CERT": [p for p in prs if p["edit"] == "E_CERT"],
              "into_ALREADY_SUFFICIENT": [p for p in prs if p["into_AS"]],
              "not_into_ALREADY_SUFFICIENT": [p for p in prs if not p["into_AS"]],
              "from_NEITHER": [p for p in prs if p["class_a"] == "NEITHER"],
              "drop_rule_ok": [p for p in prs if p["drop_rule_ok"]],
              "drop_rule_fails": [p for p in prs if not p["drop_rule_ok"]]}
    out = {k: bootstrap(v) for k, v in strata.items() if v}
    both_parsed = [p for p in prs if p["a_parsed"] and p["b_parsed"]]
    out["all_parsed_only"] = bootstrap(both_parsed) if both_parsed else None
    out["format"] = {"items": 2 * len(prs), "unparsed": sum((not p["a_parsed"]) + (not p["b_parsed"]) for p in prs),
                     "truncated": sum(p["a_trunc"] + p["b_trunc"] for p in prs),
                     "missing_pairs": sum(p["missing"] for p in prs)}
    return out


def controls(t1: list[dict]) -> dict:
    pairs = defaultdict(dict)
    for r in t1:
        pairs[r["t1"]["pair_id"]][r["t1"]["role"]] = r
    out = defaultdict(lambda: defaultdict(list))
    for m in pairs.values():
        A, B = m["A"], m["B"]
        for s in ("all", B["t1"]["transition"]):
            o = out[s]
            o["len_a"].append(len(A["prompt_text"]))
            o["len_delta"].append(len(B["prompt_text"]) - len(A["prompt_text"]))
            o["actions"].append(len(A["state"]["info_actions"]) + len(A["state"]["comp_actions"]))
            o["n_minimal_a"].append(len(A["oracle"]["minimal_sufficient_plans"]))
            o["n_minimal_b"].append(len(B["oracle"]["minimal_sufficient_plans"]))
            o["opt_cost_a"].append(A["oracle"]["optimal_cost"] if A["oracle"]["optimal_cost"] is not None else -1)
            o["opt_cost_b"].append(B["oracle"]["optimal_cost"] if B["oracle"]["optimal_cost"] is not None else -1)
    res = {s: {k: round(_mean(v), 2) for k, v in d.items()} for s, d in out.items()}
    res["class_transitions"] = dict(Counter(f"{m['B']['t1']['class_a']}->{m['B']['t1']['class_b']}" for m in pairs.values()))
    res["strata_counts"] = dict(Counter(f"{m['B']['t1']['edit']}|{m['B']['t1']['transition']}" for m in pairs.values()))
    return res


def fmt(ci) -> str:
    if not ci or ci.get("mean") is None:
        return "–"
    if ci.get("lo") is None:
        return f"{ci['mean']:.3f}"
    return f"{ci['mean']:.3f} [{ci['lo']:.3f}, {ci['hi']:.3f}]"


def render(summary: dict) -> str:
    L = ["# T1 counterfactual flips — dev pilot", "",
         f"Pre-registered in PREREG_T1.md. Families: {summary['families']} (dev, sorted ids {summary['skip'] + 1}–"
         f"{summary['skip'] + summary['families']}); pairs: {summary['pairs']}. End-to-End only. "
         "All-attempted basis (unparsed = incorrect) unless stated. 95% family-clustered bootstrap intervals.", "",
         "## Controls (data only)", "", "```", json.dumps(summary["controls"], indent=1), "```", ""]
    keys = [("a", "Item A"), ("b", "Item B"), ("joint", "Joint"), ("transition", "Transition"),
            ("excess_vs_family_perm", "Excess vs family perm. (primary)"),
            ("excess_vs_independence", "Excess vs indep."), ("b_given_a_ok", "P(B|A ok)"), ("b_given_a_wrong", "P(B|A wrong)")]
    for stratum in ("all", "direct", "indirect", "E_OBS", "E_CERT", "into_ALREADY_SUFFICIENT",
                    "not_into_ALREADY_SUFFICIENT", "from_NEITHER", "drop_rule_ok", "drop_rule_fails", "all_parsed_only"):
        L += [f"## Stratum: {stratum}", "", "| Model | pairs (fam) | " + " | ".join(k[1] for k in keys) + " |",
              "|---|---|" + "---|" * len(keys)]
        for m, s in summary["models"].items():
            r = s.get(stratum)
            if not r:
                continue
            L.append(f"| {m} | {r['n_pairs']} ({r['families']}) | " + " | ".join(fmt(r.get(k)) for k, _ in keys) + " |")
        L.append("")
    L += ["## Format", ""] + [f"- {m}: {json.dumps(s['format'])}" for m, s in summary["models"].items()]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--t1", default=str(ROOT / "data" / "generated" / "t1_v1" / "pairs.jsonl"))
    ap.add_argument("--splits", default="dev")
    ap.add_argument("--skip-families", type=int, default=10)
    ap.add_argument("--max-families", type=int, default=20)
    ap.add_argument("--models", default="")
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "t1_pilot_dev"))
    a = ap.parse_args(argv)
    splits = tuple(s.strip() for s in a.splits.split(","))
    t1 = select_t1(Path(a.data), Path(a.t1), splits, a.skip_families, a.max_families)
    raw = Path(a.raw)
    keys = [k for k in a.models.split(",") if k]
    hkeys = run_heuristics(t1, raw / "heuristics")
    summary = {"splits": list(splits), "skip": a.skip_families, "families": len({r["family_id"] for r in t1}),
               "pairs": len(t1) // 2, "controls": controls(t1), "models": {}}
    for k, root in [(k, raw) for k in keys] + [(h, raw / "heuristics") for h in hkeys]:
        ids = {r["instance_id"] for r in t1}
        res = [r for r in load_results(root, "plan_t1", k) if r["instance_id"] in ids]
        summary["models"][k] = analyze(pair_rows(t1, res))
        summary["models"][k]["format"]["responses"] = len(res)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "t1_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    (out / "t1_report.md").write_text(render(summary))
    print(f"wrote {out / 't1_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
