"""Analyses for E2, E4, E6, E8, E9, E10, E11, E12, the surface-probe baseline, and the
confirmatory test family. Inputs are scored plan rows (pilot.score_plan_results).

Every result names the mode it was measured in. End-to-End results test the full
chain (detection + diagnosis + planning) and are never read as planning failures.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from msep.benchmark.audit import FEATURE_SETS, lookup_probe, probe_rows
from msep.benchmark.schemas import instance_from_record
from msep.models.prompts import Mode, build_prompt, eligible
from msep.models.runner import Job
from msep.oracle.sufficiency import expost_sufficient

from .bootstrap import cluster_mean_ci, holm, mcnemar_exact, paired_diff_ci

RESOLVABLE = ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH")


def _rate(rows, key, cond=lambda r: True):
    return cluster_mean_ci((r["family_id"], bool(r.get(key))) for r in rows if cond(r))


def _mean(rows, key, cond=lambda r: True):
    vals = [(r["family_id"], float(r[key])) for r in rows if cond(r) and r.get(key) is not None]
    return cluster_mean_ci(vals)


def by_mode(rows, mode):
    return [r for r in rows if r["mode"] == mode]


# -- job builders for variant sets ------------------------------------------------------

VARIANT_MODES = {
    "cost": (Mode.DETECTION_CONTROLLED, Mode.DIAGNOSIS_CONTROLLED),
    "risk": (Mode.END_TO_END, Mode.DETECTION_CONTROLLED),
    "shift": (Mode.DETECTION_CONTROLLED, Mode.END_TO_END),
    "t1": (Mode.END_TO_END,),  # T1 flips change what is known, incl. into ALREADY_SUFFICIENT: E2E only
}


def build_variant_jobs(records: list[dict], kind: str) -> list[Job]:
    jobs = []
    for rec in records:
        rc = rec["oracle"]["resource_class"]
        for mode in VARIANT_MODES[kind]:
            if eligible(mode, rc):
                jobs.append(Job(f"plan_{kind}", rec["instance_id"], rec["family_id"], mode.value,
                                build_prompt(rec["prompt_text"], mode, rc), meta={"variant": rec.get("variant")}))
    return jobs


# -- E2: End-to-End detection -----------------------------------------------------------

def analyze_e2(rows: list[dict]) -> dict:
    e2e = by_mode(rows, "end_to_end")
    suff = [r for r in e2e if r["gold_class"] == "ALREADY_SUFFICIENT"]
    insuff = [r for r in e2e if r["gold_class"] != "ALREADY_SUFFICIENT"]
    sens = _rate(insuff, "detection_correct")
    spec = _rate(suff, "detection_correct")
    bal = None if sens["mean"] is None or spec["mean"] is None else (sens["mean"] + spec["mean"]) / 2
    return {
        "mode": "end_to_end",
        "detection_accuracy": _rate(e2e, "detection_correct"),
        "insufficiency_detected (sensitivity)": sens,
        "sufficiency_recognised (specificity)": spec,
        "balanced_detection_accuracy": bal,
        "over_answering": cluster_mean_ci((r["family_id"], r.get("decision") in ("true", "false")) for r in insuff),
        "unnecessary_intervention": cluster_mean_ci((r["family_id"], bool(r.get("plan_formal"))) for r in suff),
        "by_sibling": {t: _rate(e2e, "detection_correct", lambda r, t=t: r["sibling_type"] == t)["mean"]
                       for t in sorted({r["sibling_type"] for r in e2e})},
    }


# -- E4: exact targeting ----------------------------------------------------------------------

def action_overlap(pred: set[str], optimal_plans: list) -> tuple[float, float]:
    """Precision and recall of the predicted actions against the CLOSEST optimal plan (best F1).

    Several plans can be equally optimal; comparing against their union would penalise an
    agent that chose any one of them (fixed in the readiness review, 2026-11-04)."""
    best = (0.0, 0.0, -1.0)
    for plan in optimal_plans or [[]]:
        gold = set(plan)
        p = len(pred & gold) / len(pred) if pred else (1.0 if not gold else 0.0)
        r = len(pred & gold) / len(gold) if gold else 1.0
        f = 0.0 if p + r == 0 else 2 * p * r / (p + r)
        if f > best[2]:
            best = (p, r, f)
    return best[0], best[1]


def analyze_e4(rows: list[dict], records: dict) -> dict:
    out = {}
    for mode in ("diagnosis_controlled", "detection_controlled"):
        rr = [r for r in by_mode(rows, mode) if r["gold_class"] in RESOLVABLE and r["valid"]]
        prec, rec_ = [], []
        for r in rr:
            pp, rc = action_overlap(set(r.get("plan_formal") or []), records[r["instance_id"]]["oracle"]["optimal_plans"])
            prec.append((r["family_id"], pp))
            rec_.append((r["family_id"], rc))
        res = {"n": len(rr), "exact_match": _rate(rr, "plan_exact_match"),
               "action_precision": cluster_mean_ci(prec), "action_recall": cluster_mean_ci(rec_)}
        if mode == "detection_controlled":
            res["class_correct_but_plan_insufficient"] = cluster_mean_ci(
                (r["family_id"], r["class_correct"] and not r["plan_sufficient"]) for r in rr)
        out[mode] = res
    return out


# -- E6: minimality ------------------------------------------------------------------------------

def analyze_e6(rows: list[dict]) -> dict:
    out = {}
    for mode in ("detection_controlled", "diagnosis_controlled"):
        rr = [r for r in by_mode(rows, mode) if r["gold_class"] in RESOLVABLE and r["valid"]]
        suff = [r for r in rr if r["plan_sufficient"]]
        out[mode] = {
            "n": len(rr), "plan_sufficient": _rate(rr, "plan_sufficient"),
            "optimal_given_sufficient": _rate(suff, "plan_optimal"),
            "inclusion_minimal_given_sufficient": _rate(suff, "plan_minimal"),
            "excess_cost_given_sufficient": _mean(suff, "excess_cost"),
            "regret": _mean(rr, "regret"),
            "by_sibling_optimal_given_sufficient": {
                t: _rate(suff, "plan_optimal", lambda r, t=t: r["sibling_type"] == t)["mean"]
                for t in ("SUFFICIENT_NON_MINIMAL", "MULTIPLE_PLANS_DIFFERENT_COSTS", "BOTH", "INFORMATION_ONLY")},
        }
    return out


# -- E8: NEITHER ---------------------------------------------------------------------------------

def analyze_e8(rows: list[dict]) -> dict:
    out = {}
    for mode in ("end_to_end", "detection_controlled"):
        rr = [r for r in by_mode(rows, mode) if r["gold_class"] == "NEITHER"]
        out[mode] = {
            "n": len(rr),
            "correct_defer": cluster_mean_ci((r["family_id"], r["valid"] and not r.get("plan_formal") and
                                              r.get("decision") == "defer" and r.get("pred_class") == "NEITHER") for r in rr),
            "inappropriate_persistence": cluster_mean_ci((r["family_id"], bool(r.get("plan_formal"))) for r in rr),
            "hallucinated_actions": cluster_mean_ci((r["family_id"], bool(r.get("unknown_actions"))) for r in rr),
            "premature_answer": cluster_mean_ci((r["family_id"], r.get("decision") in ("true", "false")) for r in rr),
            "classified_neither": _rate(rr, "class_correct"),
        }
    return out


# -- E9: stopping (execution in the actual world) ---------------------------------------------------

def stopping_measures(row: dict, rec: dict) -> dict | None:
    if not row["valid"] or row.get("unknown_actions"):
        return None
    inst = instance_from_record(rec)
    plan = list(row.get("plan_formal") or [])
    first = None
    for k in range(len(plan) + 1):
        if expost_sufficient(inst, plan[:k]):
            first = k
            break
    reached = first is not None
    # Abstaining (no plan, NEITHER) is a choice to defer, not a premature stop.
    abstained = not plan and row.get("pred_class") == "NEITHER" and row.get("decision") == "defer"
    return {"abstained": abstained,
            "premature_stop": bool(row.get("stop_after_plan")) and not reached and not abstained,
            # A static plan is chosen before outcomes are seen; in the actual world an earlier prefix
            # may already settle q. That is a saving only an adaptive agent can take, not an error:
            # compare with the oracle's own value.
            "static_actions_after_expost_sufficiency": (len(plan) - first) if reached else 0,
            "continued_after_expost_sufficiency": reached and len(plan) > first}


def analyze_e9(rows: list[dict], records: dict) -> dict:
    out = {}
    for mode in ("detection_controlled", "end_to_end"):
        items = []
        for r in by_mode(rows, mode):
            if r["gold_class"] == "NEITHER":
                continue
            m = stopping_measures(r, records[r["instance_id"]])
            if m is not None:
                items.append({**m, "family_id": r["family_id"], "sibling_type": r["sibling_type"]})
        res = {"n": len(items),
               "premature_stop": cluster_mean_ci((i["family_id"], i["premature_stop"]) for i in items),
               "abstained": cluster_mean_ci((i["family_id"], i["abstained"]) for i in items),
               "continued_after_expost_sufficiency": cluster_mean_ci(
                   (i["family_id"], i["continued_after_expost_sufficiency"]) for i in items),
               "static_actions_after_expost_sufficiency_mean": cluster_mean_ci(
                   (i["family_id"], i["static_actions_after_expost_sufficiency"]) for i in items),
               "note": "continued_after_expost_sufficiency is not an error for a static plan; read it against the "
                       "oracle agent's value (the adaptive saving available)."}
        for t in ("PREMATURE_STOP", "UNNECESSARY_EXTRA_ACTION", "ALREADY_SUFFICIENT"):
            sel = [i for i in items if i["sibling_type"] == t]
            res[t] = {"premature_stop": cluster_mean_ci((i["family_id"], i["premature_stop"]) for i in sel)["mean"],
                      "continued_after_expost_sufficiency": cluster_mean_ci(
                          (i["family_id"], i["continued_after_expost_sufficiency"]) for i in sel)["mean"]}
        out[mode] = res
    return out


# -- E10: cost sensitivity -----------------------------------------------------------------------

def analyze_e10(rows: list[dict], records: dict) -> dict:
    out = {}
    for mode in ("detection_controlled", "diagnosis_controlled"):
        rr = [r for r in by_mode(rows, mode) if records[r["instance_id"]].get("variant", {}).get("kind") == "cost_sweep"]
        by_rel = defaultdict(list)
        sweeps = defaultdict(list)
        for r in rr:
            v = records[r["instance_id"]]["variant"]
            chose_swept = v["action"] in (r.get("plan_formal") or [])
            by_rel[v["relation"]].append((r["family_id"], chose_swept))
            sweeps[v["of"]].append(r["plan_optimal"] if r["valid"] else False)
        rel_of = lambda r: records[r["instance_id"]]["variant"]["relation"]  # noqa: E731
        out[mode] = {
            "n": len(rr),
            "optimal_rate": _rate(rr, "plan_optimal"),
            # 'below' items are the only ones where the base item's cheapest plan stops being cheapest;
            # a cost-blind policy that keeps the base plan scores 1 on 'above'/'equal' and 0 on 'below'
            "optimal_rate_by_relation": {rel: {**_rate([r for r in rr if rel_of(r) == rel], "plan_optimal"),
                                               "unparsed": sum(not r["valid"] for r in rr if rel_of(r) == rel)}
                                         for rel in ("below", "equal", "above")},
            "chose_swept_action_by_cost_relation": {k: cluster_mean_ci(v)["mean"] for k, v in sorted(by_rel.items())},
            "oracle_expectation": "swept action chosen when its cost is below the rival's, not when above; both are optimal when equal",
            "sweeps_optimal_at_every_cost": sum(all(v) for v in sweeps.values()) / max(1, len(sweeps)),
            "sweeps": len(sweeps),
        }
    return out


# -- E11: risk sensitivity -----------------------------------------------------------------------

def analyze_e11(rows: list[dict], records: dict) -> dict:
    out = {}
    for mode in ("end_to_end", "detection_controlled"):
        rr = [r for r in by_mode(rows, mode) if records[r["instance_id"]].get("variant", {}).get("kind") == "risk"]
        by_tau = defaultdict(list)
        for r in rr:
            by_tau[records[r["instance_id"]]["variant"]["tau"]].append(r)
        res = {}
        for tau, g in sorted(by_tau.items()):
            res[tau] = {
                "n": len(g),
                "oracle_answer_justified_rate": sum(r["gold_class"] == "ALREADY_SUFFICIENT" for r in g) / len(g),
                "model_answers_rate": sum(r.get("decision") in ("true", "false") for r in g) / len(g),
                "detection_correct": _rate(g, "detection_correct")["mean"],
                "plan_optimal": _rate(g, "plan_optimal")["mean"],
            }
        out[mode] = res
    return out


# -- E12: structural shift --------------------------------------------------------------------

def analyze_e12(shift_rows: list[dict], base_rows: list[dict], records: dict) -> dict:
    base = {(r["instance_id"], r["mode"]): r for r in base_rows}
    out = {}
    for mode in ("detection_controlled", "end_to_end"):
        res = {}
        for axis in ("width", "depth", "skin"):
            pairs = []
            for r in by_mode(shift_rows, mode):
                v = records[r["instance_id"]].get("variant", {})
                if v.get("axis") != axis or r["gold_class"] not in RESOLVABLE:
                    continue
                b = base.get((v["of"], mode))
                if b is not None:
                    pairs.append((r["family_id"], b, r))
            res[axis] = {
                "pairs": len(pairs),
                "in_distribution_plan_sufficient": cluster_mean_ci((f, b["plan_sufficient"]) for f, b, _ in pairs)["mean"],
                "shifted_plan_sufficient": cluster_mean_ci((f, s["plan_sufficient"]) for f, _, s in pairs)["mean"],
                "paired_drop_plan_sufficient": paired_diff_ci((f, float(b["plan_sufficient"]), float(s["plan_sufficient"]))
                                                              for f, b, s in pairs),
                "in_distribution_class_correct": cluster_mean_ci((f, b["class_correct"]) for f, b, _ in pairs)["mean"],
                "shifted_class_correct": cluster_mean_ci((f, s["class_correct"]) for f, _, s in pairs)["mean"],
                "mcnemar_plan_sufficient": mcnemar_exact((b["plan_sufficient"], s["plan_sufficient"]) for _, b, s in pairs),
            }
        out[mode] = res
    return out


# -- surface baseline, taxonomy, confirmatory family -----------------------------------------------

def surface_baseline(train_records: list[dict], eval_records: list[dict]) -> dict:
    """The audit's lookup probe, trained on train, scored on the evaluated instances."""
    tr = [r for r in probe_rows(train_records) if r["resource_class"] != "ALREADY_SUFFICIENT"]
    ev = [r for r in probe_rows(eval_records) if r["resource_class"] != "ALREADY_SUFFICIENT"]
    return {name: lookup_probe(tr, ev, feats) for name, feats in FEATURE_SETS.items()}


def taxonomy(rows: list[dict]) -> dict:
    return {mode: dict(Counter(r["stage"] for r in by_mode(rows, mode)))
            for mode in ("end_to_end", "detection_controlled", "diagnosis_controlled")}


CONFIRMATORY = {
    # name -> (where to find the McNemar result in the summary), mirrors PROTOCOL.md section 4
    "H2_diagnosis_vs_plan_sufficiency_DC": ("E3", "detection_controlled", "h2_mcnemar"),
    "H3_relevance_vs_sufficiency_judgment": ("E5", "a_judgment", "mcnemar"),
    "H4_INFO_vs_BOTH_DC": ("E7", "detection_controlled", "mcnemar_INFORMATION_ONLY_vs_BOTH"),
    "H4_COMP_vs_BOTH_DC": ("E7", "detection_controlled", "mcnemar_COMPUTATION_ONLY_vs_BOTH"),
}


def confirmatory(summary_for_model: dict) -> dict:
    ps = {}
    for name, path in CONFIRMATORY.items():
        node = summary_for_model
        try:
            for k in path:
                node = node[k]
            ps[name] = float(node["p_value"])
        except (KeyError, TypeError):
            continue
    return {"raw_p": ps, "holm_adjusted_p": holm(ps) if ps else {}}


# -- mode validation ----------------------------------------------------------------------------

def mode_decomposition(rows: list[dict]) -> dict:
    """Attribute failures to a stage by comparing the SAME instance across modes.

    On insufficient, resolvable instances ("success" = class correct and plan sufficient):
      E2E vs DC:  E2E fails but DC succeeds -> the End-to-End failure is attributable to
                  detection/framing, not to planning ability.
      DC vs DxC:  DC fails but DxC plan succeeds -> attributable to diagnosis.
      fails in all modes -> a planning failure that survives both controls.
    """
    idx = {(r["instance_id"], r["mode"]): r for r in rows}
    inst = {r["instance_id"]: r for r in rows if r["gold_class"] in RESOLVABLE}
    cats = defaultdict(list)
    excluded = 0
    for iid, r in inst.items():
        e = idx.get((iid, "end_to_end"))
        d = idx.get((iid, "detection_controlled"))
        x = idx.get((iid, "diagnosis_controlled"))
        if not (e and d and x):
            continue
        # An unparsed or truncated answer in any mode says nothing about the stage that failed:
        # attributing it would turn a format failure into a "diagnosis" or "detection" failure.
        if not (e.get("valid", True) and d.get("valid", True) and x.get("valid", True)):
            excluded += 1
            continue
        ok_e = bool(e.get("detection_correct") and e.get("class_correct") and e.get("plan_sufficient"))
        ok_d = bool(d.get("class_correct") and d.get("plan_sufficient"))
        ok_x = bool(x.get("plan_sufficient"))
        f = r["family_id"]
        cats["e2e_success"].append((f, ok_e))
        cats["e2e_fail_detection_wrong"].append((f, not ok_e and not e.get("detection_correct")))
        cats["e2e_fail_but_dc_success"].append((f, not ok_e and ok_d))
        cats["dc_fail_but_dxc_success (diagnosis-attributable)"].append((f, not ok_d and ok_x))
        cats["fail_in_all_modes (planning)"].append((f, not ok_e and not ok_d and not ok_x))
    out = {k: cluster_mean_ci(v) for k, v in cats.items()}
    out["excluded_unparsed_in_some_mode"] = excluded
    return out


def plan_sufficiency_by_mode(rows: list[dict]) -> dict:
    """Plan sufficiency on resolvable states, per mode, on two stated bases:
    all answers (an unparsed or truncated answer counts as a failure) and parsed answers only."""
    out = {}
    for mode in ("end_to_end", "detection_controlled", "diagnosis_controlled"):
        rr = [r for r in by_mode(rows, mode) if r["gold_class"] in RESOLVABLE]
        val = [r for r in rr if r["valid"]]
        out[mode] = {"n": len(rr), "unparsed": len(rr) - len(val),
                     "all_answers": _rate(rr, "plan_sufficient"), "parsed_only": _rate(val, "plan_sufficient"),
                     "optimal_all_answers": _rate(rr, "plan_optimal"), "optimal_parsed_only": _rate(val, "plan_optimal")}
    return out


def instruction_compliance(rows: list[dict]) -> dict:
    """Controlled modes state facts; responses contradicting them are reported, not silently scored."""
    dc = [r for r in by_mode(rows, "detection_controlled") if r["valid"]]
    dx = [r for r in by_mode(rows, "diagnosis_controlled") if r["valid"]]
    return {
        "dc_claims_state_sufficient": cluster_mean_ci((r["family_id"], r.get("state_sufficient_said") is True) for r in dc),
        "dxc_claims_state_sufficient": cluster_mean_ci((r["family_id"], r.get("state_sufficient_said") is True) for r in dx),
        "dxc_class_differs_from_given": cluster_mean_ci((r["family_id"], r.get("pred_class") != r["gold_class"]) for r in dx),
    }


def hierarchical(rows: list[dict], judgment: dict | None) -> dict:
    """EXPERIMENT_PLAN §8: A_D, A_G, A_P, A_S, A_E2E, each from its own mode."""
    e2e = by_mode(rows, "end_to_end")
    dc = [r for r in by_mode(rows, "detection_controlled") if r["gold_class"] != "ALREADY_SUFFICIENT"]
    dx = by_mode(rows, "diagnosis_controlled")

    def e2e_optimal(r):
        if r["gold_class"] == "ALREADY_SUFFICIENT":
            return bool(r.get("detection_correct") and not r.get("plan_formal") and r.get("decision_correct"))
        if r["gold_class"] == "NEITHER":
            return bool(r.get("class_correct") and not r.get("plan_formal") and r.get("decision") == "defer")
        return bool(r.get("detection_correct") and r.get("class_correct") and r.get("plan_optimal"))
    return {
        "A_D detection (E2E)": _rate(e2e, "detection_correct"),
        "A_G diagnosis given insufficiency (DC)": _rate(dc, "class_correct"),
        "A_P plan optimal given correct diagnosis (DC)": _rate([r for r in dc if r["class_correct"]
                                                               and r["gold_class"] in RESOLVABLE], "plan_optimal"),
        "A_P' plan optimal given class (DxC)": _rate(dx, "plan_optimal"),
        "A_S sufficiency judgment (E5)": None if not judgment else judgment.get("pair_both_correct"),
        "A_E2E fully correct behaviour (E2E)": cluster_mean_ci((r["family_id"], e2e_optimal(r)) for r in e2e),
    }


def calibration_by_mode(rows: list[dict], results_by_key: dict) -> dict:
    """Stated confidence vs whether the plan was sufficient (plan responses)."""
    from .bootstrap import calibration
    out = {}
    for mode in ("end_to_end", "detection_controlled", "diagnosis_controlled"):
        items = []
        for r in by_mode(rows, mode):
            conf = results_by_key.get((r["instance_id"], mode))
            if r["valid"] and conf is not None:
                items.append((conf, r["plan_sufficient"] if r["gold_class"] != "ALREADY_SUFFICIENT" else r["detection_correct"]))
        out[mode] = calibration(items)
    return out


def mode_regret_test(rows: list[dict]) -> dict:
    """Paired permutation test of regret, Detection-Controlled vs Diagnosis-Controlled (same instances)."""
    from .bootstrap import paired_cluster_permutation
    idx = {(r["instance_id"], r["mode"]): r for r in rows}
    pairs = []
    for (iid, mode), r in idx.items():
        if mode != "detection_controlled" or r["gold_class"] not in RESOLVABLE:
            continue
        x = idx.get((iid, "diagnosis_controlled"))
        if x and r.get("regret") is not None and x.get("regret") is not None:
            pairs.append((r["family_id"], r["regret"], x["regret"]))
    return paired_cluster_permutation(pairs)


def stratified(rows: list[dict], strata: dict[str, str]) -> dict:
    """Key metrics per stratum (e.g. heuristic_easy / heuristic_hard, template v2 / v3)."""
    out = {}
    for s in sorted(set(strata.values())):
        rr = [r for r in rows if strata.get(r["instance_id"]) == s]
        dc = [r for r in by_mode(rr, "detection_controlled") if r["gold_class"] != "ALREADY_SUFFICIENT"]
        out[s] = {
            "n_instances": len({r["instance_id"] for r in rr}),
            "dc_class_correct": _rate(dc, "class_correct"),
            "dc_plan_sufficient": _rate([r for r in dc if r["gold_class"] in RESOLVABLE], "plan_sufficient"),
            "dc_plan_optimal": _rate([r for r in dc if r["gold_class"] in RESOLVABLE], "plan_optimal"),
            "e2e_detection": _rate(by_mode(rr, "end_to_end"), "detection_correct"),
        }
    return out


def breakdown(rows: list[dict], strata: dict[str, str]) -> dict:
    """Stratum (all / heuristic_hard / heuristic_easy) x mode x gold class:
    n, class correct, plan sufficient, plan optimal (family-clustered CIs)."""
    out = {}
    for st in ("all", "heuristic_hard", "heuristic_easy"):
        sel = rows if st == "all" else [r for r in rows if strata.get(r["instance_id"]) == st]
        out[st] = {}
        for mode in ("end_to_end", "detection_controlled", "diagnosis_controlled"):
            mm = by_mode(sel, mode)
            out[st][mode] = {}
            for cls in ("ALL", "ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER"):
                g = mm if cls == "ALL" else [r for r in mm if r["gold_class"] == cls]
                if not g:
                    continue
                res_g = [r for r in g if r["gold_class"] in RESOLVABLE]
                out[st][mode][cls] = {"n": len(g), "class_correct": _rate(g, "class_correct"),
                                      "plan_sufficient": _rate(res_g, "plan_sufficient") if res_g else None,
                                      "plan_optimal": _rate(res_g, "plan_optimal") if res_g else None}
    return out


# -- E14: computation-capability control ------------------------------------------------------

def build_capability_jobs(records: list[dict]) -> list[Job]:
    """One job per certified task per family (tasks are shared by all siblings of a family)."""
    from msep.models.prompts import build_capability_prompt
    from msep.world.compute_tasks import task_from_json
    jobs, seen = [], set()
    for rec in records:
        for name, t in rec["state"]["compute_tasks"].items():
            key = (rec["family_id"], name)
            if key in seen:
                continue
            seen.add(key)
            task = task_from_json(t)
            jobs.append(Job("capability", rec["instance_id"], rec["family_id"], "capability",
                            build_capability_prompt(task.describe()), meta={"var": name, "kind": task.kind}))
    return jobs


def analyze_e14(records: dict, cap_results: list[dict], rows: list[dict]) -> dict:
    """Separate 'cannot plan certified computation' from 'computed it internally and skipped COMPUTE'.

    capability[family, var] = the model settled the task correctly with no tools. For instances that
    need computation (COMPUTATION_ONLY, BOTH), compare how often the model's plan skips the needed
    computation when it is internally capable vs not. A higher skip rate when capable suggests a
    tool-policy choice (substituting its own computation), not a failure to see that computation is needed.
    """
    cap, kind_items = {}, defaultdict(list)
    for r in cap_results:
        rec = records.get(r["instance_id"])
        if rec is None:
            continue
        var = r["meta"]["var"]
        truth = rec["true_computed_values"][var]
        ok = r["parsed"] is not None and (r["parsed"]["value"] == "true") == truth
        cap[(r["family_id"], var)] = ok
        kind_items[r["meta"]["kind"]].append((r["family_id"], ok))
    out = {"capability_by_kind": {k: cluster_mean_ci(v) for k, v in sorted(kind_items.items())},
           "capability_overall": cluster_mean_ci([x for v in kind_items.values() for x in v])}
    for mode in ("end_to_end", "detection_controlled"):
        capable, incapable = [], []
        for r in by_mode(rows, mode):
            if r["gold_class"] not in ("COMPUTATION_ONLY", "BOTH") or not r["valid"]:
                continue
            rec = records[r["instance_id"]]
            comp_names = {a["name"]: a["reveals"] for a in rec["state"]["comp_actions"]}
            needed = {v for a in rec["oracle"]["optimal_plans"][0] if a in comp_names for v in comp_names[a]}
            if not needed or any((r["family_id"], v) not in cap for v in needed):
                continue
            chosen_comp = [a for a in (r.get("plan_formal") or []) if a in comp_names]
            skipped = (not chosen_comp) or (mode == "end_to_end" and r.get("state_sufficient_said") is True)
            (capable if all(cap[(r["family_id"], v)] for v in needed) else incapable).append((r["family_id"], skipped))
        out[mode] = {"skip_rate_when_capable": cluster_mean_ci(capable),
                     "skip_rate_when_not_capable": cluster_mean_ci(incapable),
                     "note": "skip = no computation action for the needed fact (E2E: or claims sufficiency)"}
    return out


def versus_baseline(model_rows: list[dict], base_rows: list[dict]) -> dict:
    """Same instances, same mode: model vs a shallow heuristic on plan optimality (resolvable states)
    and class correctness. Paired McNemar and paired difference with family-clustered CI."""
    base = {(r["instance_id"], r["mode"]): r for r in base_rows}
    out = {}
    for mode in ("detection_controlled", "diagnosis_controlled", "end_to_end"):
        pairs_opt, pairs_cls = [], []
        for r in by_mode(model_rows, mode):
            b = base.get((r["instance_id"], mode))
            if b is None:
                continue
            pairs_cls.append((r["family_id"], bool(r.get("class_correct")), bool(b.get("class_correct"))))
            if r["gold_class"] in RESOLVABLE:
                pairs_opt.append((r["family_id"], bool(r.get("plan_optimal")), bool(b.get("plan_optimal"))))
        out[mode] = {
            "plan_optimal_model_minus_baseline": paired_diff_ci((f, float(a), float(b)) for f, a, b in pairs_opt),
            "plan_optimal_mcnemar": mcnemar_exact((a, b) for _, a, b in pairs_opt),
            "class_correct_model_minus_baseline": paired_diff_ci((f, float(a), float(b)) for f, a, b in pairs_cls),
        }
    return out
