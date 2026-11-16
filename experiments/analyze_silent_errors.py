"""Silent semantic errors in Study 3 (EXPLORATORY, POST HOC; no model calls).

Designed 2026-11-15, after the Study 3 results had been seen; not registered. Reads the stored Study 3 records
through the functions of `run_repair.py` and changes nothing there.

For every extraction that the reader ACCEPTED but whose state differs from the true state (accepted but wrong), the
exact planner (run_eop.planned_results) plans on the extracted state, and its plan is scored on the TRUE item
(run_eop.score, oracle labels in the item record). Each such plan is put in one class:

  still_optimal           the plan is optimal on the true state (or a correct stop/defer): the wrong state did no harm
  sufficient_but_costlier resolvable state; the plan settles the question but costs more than the optimum
  insufficient            resolvable state; the plan does not settle the question
  unnecessary_intervention  the true state is already sufficient; the plan proposes actions
  wrong_stop_or_defer     wrong decision with no action on an already-sufficient state, an answer on a NEITHER state
                          (should defer), or no action on a resolvable state (stops or defers too early)
  planner_error           the planner could not plan on the extracted state (detected downstream, not silent)

A silent consequential error is an accepted extraction with a wrong state whose plan is not still_optimal and that
the planner did not reject. Rates per item use all items of the arm as the denominator.

    .venv/bin/python experiments/analyze_silent_errors.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_repair as rr  # noqa: E402
from msep.benchmark.parsing import parse_state  # noqa: E402
from msep.controllers.llm_extractor import state_from_extraction  # noqa: E402
from msep.eval.bootstrap import cluster_mean_ci, paired_diff_ci  # noqa: E402
from msep.eval.extraction_match import _sig, compare  # noqa: E402
from msep.models.runner import latest_record  # noqa: E402
from run_eop import planned_results, score  # noqa: E402

RAW = rr.ROOT / "results" / "raw" / "pilot"
OUT = rr.ROOT / "results" / "aggregate" / "repair"
MODELS = ("adaption-gemma-4-26b-a4b-it-schema", "adaption-deepseek-v4-flash")
CLASSES = ("still_optimal", "sufficient_but_costlier", "insufficient", "unnecessary_intervention",
           "wrong_stop_or_defer", "planner_error")
HARMLESS = {"still_optimal", "planner_error"}


def exact(d, ref) -> bool:
    try:
        return compare(state_from_extraction(d), ref)["exact"]
    except Exception:
        return False


def extractions(its: list[dict], arm: str, key: str) -> tuple[dict, dict]:
    first, final = {}, {}
    for r in its:
        d1, _ = rr.read(latest_record(RAW, rr.job1(arm, key, r), key))
        d2 = d1
        if d1 is None and (j := rr.job2(arm, key, r, RAW)) is not None:
            d2, _ = rr.read(latest_record(RAW, j, key))
        first[r["instance_id"]], final[r["instance_id"]] = d1, d2
    return first, final


def classify(rec: dict, row: dict, status: str) -> str:
    if status != "ok" or not row.get("valid"):
        return "planner_error"
    rc = rec["oracle"]["resource_class"]
    plan = row.get("plan_formal") or []
    if rc == "ALREADY_SUFFICIENT":
        if plan:
            return "unnecessary_intervention"
        return "still_optimal" if row.get("stop_ok") else "wrong_stop_or_defer"
    if rc == "NEITHER":
        return "still_optimal" if row.get("stop_ok") else "wrong_stop_or_defer"
    if not plan:
        return "wrong_stop_or_defer"
    if row.get("plan_optimal"):
        return "still_optimal"
    return "sufficient_but_costlier" if row.get("plan_sufficient") else "insufficient"


def stage(its: list[dict], ex: dict, ref: dict) -> dict:
    by = {r["instance_id"]: r for r in its}
    wrong = [i for i, d in ex.items() if d is not None and not exact(d, ref[i])]
    res, stats = planned_results([by[i] for i in wrong], {i: {"parsed": ex[i], "status": "ok"} for i in wrong})
    rows = score(by, res, wrong)
    status = {r["instance_id"]: r["status"] for r in res}
    cls = {i: classify(by[i], rows[i], status[i]) for i in wrong}
    detail = {i: {"family_id": by[i]["family_id"], "wording": by[i]["robust"]["kind"],
                  "true_class": by[i]["oracle"]["resource_class"], "true_answer": by[i]["true_target_value"], "class": cls[i],
                  "plan_on_extracted_state": rows[i].get("plan_formal"), "decision": rows[i].get("decision"),
                  "true_optimal_plans": by[i]["oracle"]["optimal_plans"], "true_optimal_cost": by[i]["oracle"]["optimal_cost"],
                  "plan_cost": rows[i].get("plan_cost"), "diff": _diff(ex[i], ref[i])} for i in wrong}
    silent = {i for i in wrong if cls[i] not in HARMLESS}
    n = Counter(cls.values())
    fam = lambda i: by[i]["family_id"]  # noqa: E731
    return {
        "items": len(its), "accepted": sum(d is not None for d in ex.values()),
        "accepted_exact": sum(d is not None and exact(d, ref[i]) for i, d in ex.items()),
        "accepted_but_wrong": len(wrong),
        "classes": {c: n.get(c, 0) for c in CLASSES},
        "class_share_of_accepted_but_wrong": {c: (round(n.get(c, 0) / len(wrong), 3) if wrong else None) for c in CLASSES},
        "silent_consequential": len(silent),
        "silent_consequential_share_of_accepted_but_wrong": cluster_mean_ci((fam(i), float(i in silent)) for i in wrong),
        "silent_consequential_per_item": cluster_mean_ci((fam(i), float(i in silent)) for i in by),
        "harmful_per_item (insufficient or wrong stop/defer)": cluster_mean_ci(
            (fam(i), float(cls.get(i) in ("insufficient", "wrong_stop_or_defer"))) for i in by),
        "accepted_but_wrong_per_item": cluster_mean_ci((fam(i), float(i in cls)) for i in by),
        "fields_differing_counts": dict(Counter("+".join(detail[i]["diff"].get("fields_differing", ["conversion_error"]))
                                                for i in wrong)),
        "planner_pipeline": stats, "_silent_ids": sorted(silent), "_detail": detail}


def _diff(d, ref) -> dict:
    """Which parts of the extracted state differ from the true state, named concretely."""
    try:
        st = state_from_extraction(d)
    except Exception as e:
        return {"conversion_error": f"{type(e).__name__}: {str(e)[:120]}"}
    c = compare(st, ref)
    a, b = _sig(st), _sig(ref)
    out = {"fields_differing": [k for k in ("variables", "known", "actions", "rules") if c.get(k) is False]}
    if c["variables"] is False:
        out["variables_extra"] = sorted(set(a["variables"]) - set(b["variables"]))
        out["variables_missing"] = sorted(set(b["variables"]) - set(a["variables"]))
    if c["known"] is False:
        out["known_extracted_vs_true"] = {v: [a["known"].get(v), b["known"].get(v)]
                                          for v in sorted(set(a["known"]) | set(b["known"])) if a["known"].get(v) != b["known"].get(v)}
    if c["actions"] is False:
        out["actions_differing"] = {n: [a["actions"].get(n), b["actions"].get(n)]
                                    for n in sorted(set(a["actions"]) | set(b["actions"])) if a["actions"].get(n) != b["actions"].get(n)}
    return out


def main() -> int:
    its = rr.items()
    ref = {r["instance_id"]: parse_state(r["canonical_text"], opaque_tasks=True) for r in its}
    fam = {r["instance_id"]: r["family_id"] for r in its}
    out = {"status": "EXPLORATORY, POST HOC: designed 2026-11-15 after the Study 3 results were seen; not registered; "
                     "no model calls (stored Study 3 records only)",
           "data": "data/generated/repair_v1/items.jsonl (174 reworded items, 12 train families); records in results/raw/pilot",
           "classes": CLASSES, "models": {}}
    for key in MODELS:
        for arm in rr.ARMS:
            first, final = extractions(its, arm, key)
            a, b = stage(its, first, ref), stage(its, final, ref)
            sa, sb = set(a["_silent_ids"]), set(b["_silent_ids"])
            out["models"][f"{key.replace('adaption-', '')} | {arm}"] = {
                "first_answer": a, "with_repair": b,
                "change_in_silent_consequential_per_item": paired_diff_ci(
                    (fam[i], float(i in sb), float(i in sa)) for i in fam),
                "silent_with_repair_from_repair_call": sorted(sb - sa)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "silent_errors.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    (OUT / "silent_errors.md").write_text(render(out))
    print(render(out))
    return 0


def fmt(d) -> str:
    if not isinstance(d, dict) or d.get("mean") is None:
        return "n/a"
    if d.get("lo") is None:
        return f"{d['mean']:.2f}"
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


def render(s: dict) -> str:
    L = ["# Silent semantic errors in Study 3 (exploratory, post hoc)", "",
         "**Status.** Exploratory and post hoc: designed 2026-11-15, after the Study 3 results had been seen; not registered. "
         "No model calls: the stored Study 3 records are re-read through the functions of `experiments/run_repair.py`. "
         "Generated by `experiments/analyze_silent_errors.py`.", "",
         "**Method.** For each extraction the reader accepted but whose state differs from the true state (accepted but wrong), "
         "the exact planner plans on the extracted state and the plan is scored on the true item (oracle labels). "
         "Classes: still optimal; sufficient but costlier; insufficient; unnecessary intervention (true state already "
         "sufficient, plan acts); wrong stop or defer; planner error (the planner rejected the state, so the error is not silent). "
         "A *silent consequential error* is accepted, has a wrong state, is not rejected by the planner, and its plan is not optimal "
         "on the true state. Per-item rates use all 174 items of an arm; intervals are 95% family-clustered bootstrap (12 families).", "",
         "Distinguish: exact-state accuracy (state equals the true state), parser acceptance (the reader accepts the answer), "
         "plan optimality and sufficiency (scored on the true state), and undetected semantic errors (accepted, wrong state).", "",
         "| Model and prompt | Stage | Accepted | Accepted and exact | Accepted but wrong | Still optimal | Costlier | Insufficient | "
         "Unnecessary | Wrong stop/defer | Planner error | Silent consequential | per item [95% CI] |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, m in s["models"].items():
        for st, lab in (("first_answer", "first answer"), ("with_repair", "with repair")):
            x = m[st]
            c = x["classes"]
            L.append(f"| {name} | {lab} | {x['accepted']}/{x['items']} | {x['accepted_exact']} | {x['accepted_but_wrong']} | "
                     + " | ".join(str(c[k]) for k in CLASSES)
                     + f" | {x['silent_consequential']} | {fmt(x['silent_consequential_per_item'])} |")
    L += ["", "Silent consequential errors that end in a committed wrong answer (decision true/false opposite to the true answer):", ""]
    for name, m in s["models"].items():
        for st in ("first_answer", "with_repair"):
            ids = m[st]["_silent_ids"]
            if ids:
                det = m[st]["_detail"]
                k = sum(det[i]["decision"] in ("true", "false") and (det[i]["decision"] == "true") != det[i]["true_answer"] for i in ids)
                L.append(f"- {name}, {st.replace('_', ' ')}: {k} of {len(ids)}")
    L += ["", "Which parts of the state were wrong in accepted-but-wrong extractions (counts):", ""]
    for name, m in s["models"].items():
        for st in ("first_answer", "with_repair"):
            if m[st]["accepted_but_wrong"]:
                L.append(f"- {name}, {st.replace('_', ' ')}: {m[st]['fields_differing_counts']}")
    L += ["", "Change in the silent-consequential rate per item with repair (paired, family-clustered):", ""]
    for name, m in s["models"].items():
        L.append(f"- {name}: {fmt(m['change_in_silent_consequential_per_item'])}; silent errors with repair that came from a "
                 f"repair call: {len(m['silent_with_repair_from_repair_call'])}.")
    L += ["", "Share of accepted-but-wrong extractions that are silent and consequential (family-clustered):", ""]
    for name, m in s["models"].items():
        L.append(f"- {name}: first {fmt(m['first_answer']['silent_consequential_share_of_accepted_but_wrong'])}, "
                 f"with repair {fmt(m['with_repair']['silent_consequential_share_of_accepted_but_wrong'])}.")
    none = [n for n, m in s["models"].items() if m["with_repair"]["accepted_but_wrong"] == 0 and m["first_answer"]["accepted_but_wrong"] == 0]
    if none:
        L += ["", f"No accepted-but-wrong extraction in: {', '.join(none)}. Nothing to classify there; the analysis cannot say "
                  "how such errors would act for these arms."]
    L += ["", "## Examples (with repair)", ""]
    seen = set()
    for name, m in s["models"].items():
        for i in m["with_repair"]["_silent_ids"]:
            if len(seen) >= 3 or i in seen:
                continue
            seen.add(i)
            d = m["with_repair"]["_detail"][i]
            L.append(f"- `{i}` ({name}, {d['wording']}): true class {d['true_class']}, true answer {d['true_answer']}, optimal plan(s) "
                     f"{d['true_optimal_plans']} (cost {d['true_optimal_cost']}); planned on the extracted state: "
                     f"{d['plan_on_extracted_state']} (decision {d['decision']}, cost {d['plan_cost']}) -> **{d['class']}**. "
                     f"State difference: {json.dumps(d['diff'], default=str)[:400]}")
    L += ["", "**Limits.** 12 families, one sample per item, one benchmark generator; small counts per class, so class "
          "shares are descriptive. The classification is ours and was fixed after seeing the Study 3 results.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    raise SystemExit(main())
