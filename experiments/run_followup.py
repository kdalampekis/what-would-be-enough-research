"""The two follow-up studies of PREREG_FOLLOWUP.md: model calls and analysis.

clarity  the same states in the benchmark's wording (W0) and a clarified wording (W1); End-to-End, native answer.
cost     E10: cost sweeps across the price at which the cheapest sufficient plan changes; Detection-Controlled.

Calls go through the same runner as every other run (cache by job id, at most 3 attempts per job, spend ledger).

    python experiments/run_followup.py --study clarity --models KEY --concurrency 5 --max-calls 900 --budget CAP
    python experiments/run_followup.py --study cost    --models KEY --concurrency 5 --max-calls 800 --budget CAP
    python experiments/run_followup.py --analyze-only --models KEY1,KEY2,KEY3
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from msep.benchmark.schemas import instance_from_record  # noqa: E402
from msep.envfile import load_env  # noqa: E402
from msep.eval import pilot  # noqa: E402
from msep.eval.bootstrap import cluster_mean_ci, holm, paired_diff_ci  # noqa: E402
from msep.models.config_check import check_all, currency  # noqa: E402
from msep.models.prompts import Mode, build_prompt, eligible  # noqa: E402
from msep.models.runner import Job, load_models, load_results, run_jobs  # noqa: E402
from msep.models.spend import Ledger  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated" / "followup_v1"
STUDIES = {"clarity": ("clarity.jsonl", "plan_clar", Mode.END_TO_END),
           "cost": ("cost.jsonl", "plan_cost", Mode.DETECTION_CONTROLLED)}


def load(study: str) -> list[dict]:
    return [json.loads(l) for l in open(DATA / STUDIES[study][0])]


def jobs_for(study: str) -> list[Job]:
    _, pool, mode = STUDIES[study]
    recs = load(study)
    assert all(eligible(mode, r["oracle"]["resource_class"]) for r in recs)
    return [Job(pool, r["instance_id"], r["family_id"], mode.value,
                build_prompt(r["prompt_text"], mode, r["oracle"]["resource_class"]), meta={"followup": r["followup"]})
            for r in recs]


# -- analysis ---------------------------------------------------------------------------------------

def scored(study: str, key: str, raw: Path) -> tuple[dict, dict]:
    recs = {r["instance_id"]: r for r in load(study)}
    rows = {r["instance_id"]: r for r in pilot.score_plan_results(recs, load_results(raw, STUDIES[study][1], key))}
    return recs, rows


def one_sided_p(pairs, reps: int = 10_000, seed: int = 0) -> float | None:
    """Family-cluster bootstrap p for 'mean of (a - b) is below zero': share of resamples with mean >= 0."""
    by = defaultdict(list)
    for f, a, b in pairs:
        by[f].append(a - b)
    fams = sorted(by)
    if len(fams) < 2:
        return None
    rng, ge = random.Random(seed), 0
    for _ in range(reps):
        s = [x for f in (rng.choice(fams) for _ in fams) for x in by[f]]
        ge += (sum(s) / len(s)) >= 0
    return ge / reps


def _recert(rec: dict, row: dict | None) -> bool:
    """The plan includes a computation whose results are all listed as known already."""
    if row is None or not row["valid"]:
        return False
    st = instance_from_record(rec).state
    known = set(st.known)
    acts = [st.action_index[a] for a in row["plan_formal"] if a in st.action_index]
    return any(a.resource.value == "computation" and set(a.reveals) <= known for a in acts)


def clarity_outcomes(rec: dict, row: dict | None, parsed_only: bool) -> dict | None:
    """Outcomes of one answer. All attempted: a missing or unreadable answer is the bad outcome of each measure."""
    ok = row is not None and row["valid"]
    if not ok and parsed_only:
        return None
    rc = rec["oracle"]["resource_class"]
    plan = row["plan_formal"] if ok else None
    o = {"acts": (not ok) or bool(plan), "recertifies": _recert(rec, row)}
    if rc == "ALREADY_SUFFICIENT":
        o["correct_stop"] = ok and not plan and row.get("decision_correct") is True
    elif rc == "NEITHER":
        o["correct_stop"] = ok and not plan and row.get("decision") == "defer" and row.get("pred_class") == "NEITHER"
    else:
        o["premature_stop"] = (not ok) or not plan or row.get("state_sufficient_said") is True
        o["plan_optimal"] = ok and bool(row.get("plan_optimal"))
    o["class_correct"] = ok and bool(row.get("class_correct"))
    return o


CLARITY_GROUPS = {
    "AS all": lambda r: r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT",
    "AS exposed": lambda r: r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT" and r["followup"]["exposed"],
    "AS not exposed": lambda r: r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT" and not r["followup"]["exposed"],
    "AS from the start": lambda r: r["oracle"]["resource_class"] == "ALREADY_SUFFICIENT" and r["followup"]["group"] == "sibling",
    "AS after one edit": lambda r: r["followup"]["group"] == "edited_into_sufficient",
    "COMPUTATION_ONLY": lambda r: r["oracle"]["resource_class"] == "COMPUTATION_ONLY",
    "BOTH": lambda r: r["oracle"]["resource_class"] == "BOTH",
    "NEITHER": lambda r: r["oracle"]["resource_class"] == "NEITHER",
}


def analyze_clarity(key: str, raw: Path) -> dict:
    recs, rows = scored("clarity", key, raw)
    states = defaultdict(dict)
    for i, r in recs.items():
        states[r["followup"]["of"]][r["followup"]["wording"]] = i
    out = {"answers": {w: sum(1 for i, r in recs.items() if r["followup"]["wording"] == w and i in rows) for w in ("W0", "W1")},
           "unparsed": {w: sum(1 for i, r in recs.items() if r["followup"]["wording"] == w and i in rows and not rows[i]["valid"])
                        for w in ("W0", "W1")}, "groups": {}}
    for basis in ("all_attempted", "parsed_only"):
        for g, pred in CLARITY_GROUPS.items():
            per = defaultdict(list)  # measure -> (family, W0 value, W1 value)
            for s, w in states.items():
                r0 = recs[w["W0"]]
                if not pred(r0):
                    continue
                a = clarity_outcomes(r0, rows.get(w["W0"]), basis == "parsed_only")
                b = clarity_outcomes(recs[w["W1"]], rows.get(w["W1"]), basis == "parsed_only")
                if a is None or b is None:
                    continue
                for m in a:
                    per[m].append((r0["family_id"], float(a[m]), float(b[m])))
            res = {"n_states": len(next(iter(per.values()), []))}
            for m, tr in per.items():
                res[m] = {"W0": cluster_mean_ci((f, a) for f, a, _ in tr), "W1": cluster_mean_ci((f, b) for f, _, b in tr),
                          "W1_minus_W0": paired_diff_ci((f, b, a) for f, a, b in tr),
                          "p_one_sided_reduction": one_sided_p([(f, b, a) for f, a, b in tr]),
                          "changed_W0_only": sum(a > b for _, a, b in tr), "changed_W1_only": sum(b > a for _, a, b in tr)}
            out["groups"].setdefault(basis, {})[g] = res
    return out


def analyze_cost(key: str, raw: Path) -> dict:
    recs, rows = scored("cost", key, raw)
    sweeps = defaultdict(list)
    for i, r in recs.items():
        sweeps[r["followup"]["sweep"]].append(r)
    out = {"answers": sum(i in rows for i in recs), "unparsed": sum(1 for i in recs if i in rows and not rows[i]["valid"]),
           "sweeps": len(sweeps)}
    opt = lambda r: (i := r["instance_id"]) in rows and rows[i]["valid"] and bool(rows[i].get("plan_optimal"))  # noqa: E731
    suff = lambda r: (i := r["instance_id"]) in rows and rows[i]["valid"] and bool(rows[i].get("plan_sufficient"))  # noqa: E731
    by_rel = defaultdict(list)
    for r in recs.values():
        by_rel[r["variant"]["relation"]].append(r)
    out["by_relation"] = {rel: {"n": len(rr), "optimal": cluster_mean_ci((r["family_id"], opt(r)) for r in rr),
                                "sufficient": cluster_mean_ci((r["family_id"], suff(r)) for r in rr),
                                "optimal_parsed_only": cluster_mean_ci((r["family_id"], opt(r)) for r in rr
                                                                       if r["instance_id"] in rows and rows[r["instance_id"]]["valid"]),
                                "chose_swept_action": cluster_mean_ci(
                                    (r["family_id"], r["variant"]["action"] in (rows[r["instance_id"]].get("plan_formal") or []))
                                    for r in rr if r["instance_id"] in rows and rows[r["instance_id"]]["valid"])}
                         for rel, rr in sorted(by_rel.items())}
    flip, control, kinds, excess = [], [], Counter(), []
    for s, rr in sweeps.items():
        b = rr[0]["variant"]["boundary_cost"]
        at = {r["variant"]["cost"]: r for r in rr}
        lo, hi = at[b - 1], at[b + 1]
        fam = lo["family_id"]
        flip.append((fam, float(opt(hi)), float(opt(lo))))
        others = [r for c, r in at.items() if c > b + 1]
        for r in others:  # the cost changes and the cheapest plan does not
            control.append((fam, float(opt(hi)), float(opt(r))))
        row = rows.get(lo["instance_id"])
        old = [sorted(p) for p in hi["oracle"]["optimal_plans"]]
        if row is None or not row["valid"]:
            k = "no usable answer"
        elif row.get("plan_optimal"):
            k = "optimal"
        elif sorted(row["plan_formal"]) in old:
            k = "kept the plan that was cheapest before the price change"
        elif row.get("plan_sufficient"):
            k = "another sufficient plan that is not the cheapest"
        else:
            k = "insufficient plan"
        kinds[k] += 1
        if row is not None and row["valid"] and row.get("excess_cost") is not None:
            excess.append((fam, float(row["excess_cost"])))
    out["flip_pairs"] = {
        "n": len(flip),
        "optimal_above": cluster_mean_ci((f, a) for f, a, _ in flip), "optimal_below": cluster_mean_ci((f, b) for f, _, b in flip),
        "both_optimal": cluster_mean_ci((f, a * b) for f, a, b in flip),
        "below_optimal_given_above_optimal": cluster_mean_ci((f, b) for f, a, b in flip if a),
        "above_minus_below": paired_diff_ci(flip),
        "p_one_sided_above_greater": one_sided_p([(f, b, a) for f, a, b in flip]),
        "below_item_outcomes": dict(kinds),
        "excess_cost_of_sufficient_plans_on_below_items": cluster_mean_ci(excess) if excess else None}
    out["control_pairs_price_changes_plan_does_not"] = {
        "n": len(control), "both_optimal": cluster_mean_ci((f, a * b) for f, a, b in control),
        "difference": paired_diff_ci(control)} if control else None
    out["baselines_by_construction"] = {
        "cost_blind_policy_keeps_the_plan_of_the_above_item": {"below": 0.0, "equal": 1.0, "above": 1.0},
        "exact_planner_on_the_true_state": {"below": 1.0, "equal": 1.0, "above": 1.0}}
    return out


def fmt(d) -> str:
    if not isinstance(d, dict) or d.get("mean") is None:
        return "n/a"
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


def render(summary: dict) -> str:
    L = ["# Follow-up studies: results", "", "Generated by `experiments/run_followup.py --analyze-only`. "
         "Protocol: `PREREG_FOLLOWUP.md`. These studies were proposed after the held-out results had been viewed.", ""]
    L += ["## Clarity: the same states in the original wording (W0) and the clarified wording (W1)", "",
          "End-to-End, native answer, all attempted. `acts`: proposes any action. `recertifies`: the plan includes a "
          "computation whose results are all listed as known.", ""]
    for k, m in summary["clarity"]["models"].items():
        L += [f"### {k.replace('adaption-', '')}", "", f"Answers: {m['answers']}; unparsed: {m['unparsed']}.", "",
              "| Group | States | Measure | W0 | W1 | W1 − W0 | One-sided p (reduction) | Holm p |", "|---|---|---|---|---|---|---|---|"]
        for g, res in m["groups"]["all_attempted"].items():
            for meas in ("acts", "recertifies", "correct_stop", "premature_stop", "plan_optimal", "class_correct"):
                if meas in res:
                    x = res[meas]
                    hp = summary["clarity"]["primary_holm_p"].get(k) if (g, meas) == ("AS all", "acts") else None
                    L.append(f"| {g} | {res['n_states']} | {meas} | {fmt(x['W0'])} | {fmt(x['W1'])} | {fmt(x['W1_minus_W0'])} | "
                             f"{x['p_one_sided_reduction']} | {'' if hp is None else hp} |")
        L.append("")
    L += ["## Cost (E10): the cheapest plan changes when one price crosses a boundary", "",
          "Detection-Controlled, native answer, all attempted. `below`: the swept action is one unit under the boundary and "
          "its plan is now the only cheapest one. `above`: one unit over, the original plan is cheapest.", ""]
    for k, m in summary["cost"]["models"].items():
        f = m["flip_pairs"]
        L += [f"### {k.replace('adaption-', '')}", "", f"Answers: {m['answers']}; unparsed: {m['unparsed']}; sweeps: {m['sweeps']}.", "",
              "| Side | Items | Optimal | Sufficient | Chose the swept action (parsed) |", "|---|---|---|---|---|"]
        for rel in ("above", "equal", "below"):
            x = m["by_relation"][rel]
            L.append(f"| {rel} | {x['n']} | {fmt(x['optimal'])} | {fmt(x['sufficient'])} | {fmt(x['chose_swept_action'])} |")
        L += ["", f"Flip pairs (n={f['n']}): optimal above {fmt(f['optimal_above'])}, below {fmt(f['optimal_below'])}, both "
              f"{fmt(f['both_optimal'])}; below optimal given above optimal {fmt(f['below_optimal_given_above_optimal'])}; "
              f"above − below {fmt(f['above_minus_below'])}, one-sided p {f['p_one_sided_above_greater']}, "
              f"Holm p {summary['cost']['primary_holm_p'].get(k)}.", "",
              f"Outcomes on the below items: {f['below_item_outcomes']}. Mean excess cost of sufficient plans there: "
              f"{fmt(f['excess_cost_of_sufficient_plans_on_below_items'])}.", ""]
        c = m["control_pairs_price_changes_plan_does_not"]
        if c:
            L += [f"Control pairs, price changes and the cheapest plan does not (n={c['n']}): both optimal {fmt(c['both_optimal'])}.", ""]
    L += ["Baselines by construction: a cost-blind policy that keeps the plan of the above item scores 0 on below items and 1 "
          "elsewhere; the exact planner on the true state scores 1 everywhere.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", choices=sorted(STUDIES))
    ap.add_argument("--models", required=True)
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "followup"))
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--budget", type=float, default=0.0, help="cap on the cumulative ledger total (credits)")
    ap.add_argument("--analyze-only", action="store_true")
    a = ap.parse_args(argv)
    keys = [k.strip() for k in a.models.split(",")]
    raw = Path(a.raw)
    if a.analyze_only:
        s = {"clarity": {"models": {k: analyze_clarity(k, raw) for k in keys}},
             "cost": {"models": {k: analyze_cost(k, raw) for k in keys}}}
        s["clarity"]["primary_holm_p"] = holm({k: p for k, m in s["clarity"]["models"].items()
                                               if (p := m["groups"]["all_attempted"]["AS all"]["acts"]["p_one_sided_reduction"]) is not None})
        s["cost"]["primary_holm_p"] = holm({k: p for k, m in s["cost"]["models"].items()
                                            if (p := m["flip_pairs"]["p_one_sided_above_greater"]) is not None})
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "followup_summary.json").write_text(json.dumps(s, indent=1, default=str))
        (out / "followup_report.md").write_text(render(s))
        print(f"wrote {out / 'followup_summary.json'} and followup_report.md")
        return 0
    if not a.study or a.budget <= 0 or a.max_calls <= 0:
        print("pass --study, --budget (cumulative ledger cap) and --max-calls; no calls made")
        return 2
    load_env(ROOT / ".env")
    models = load_models(Path(a.models_config))
    errs, warns = check_all(models, keys)
    for e in errs:
        print("ERROR", e)
    if errs:
        return 2
    jobs = jobs_for(a.study)
    cur = currency(models[keys[0]])
    ledger = Ledger(raw / ("spend_ledger.jsonl" if cur == "usd" else f"spend_ledger_{cur}.jsonl"), a.budget)
    print(f"{a.study}: {len(jobs)} jobs per model; budget {a.budget:.4f}; already spent {ledger.spent:.4f}")
    for k in keys:
        print(k, run_jobs(jobs, k, models[k], raw, max_calls=a.max_calls, concurrency=a.concurrency, ledger=ledger))
    print(f"cumulative spend {ledger.spent:.4f} of {a.budget:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
