"""Phase 2 pilot: job construction and the E1, E3, E5, E7 analyses.

Three job pools share calls across experiments:
- plan      every instance x every eligible mode (E3, E5b, E7, and E1b on ALREADY_SUFFICIENT)
- judgment  "is this specific plan sufficient?" for matched candidate plans (E5a)
- decision  "Q true or false?" on already-sufficient states (E1a)

Guardrails (ASSUMPTIONS.md A1, A20):
- results are reported separately per mode;
- End-to-End errors are never interpreted as planning failures;
- unparseable or failed responses count as incorrect and are reported separately.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from msep.benchmark.schemas import instance_from_record
from msep.eval.bootstrap import (balanced_accuracy, cluster_mean_ci, cluster_stat_ci, confusion, macro_f1,
                                 mcnemar_exact, paired_diff_ci)
from msep.eval.error_taxonomy import classify
from msep.eval.plan_metrics import score
from msep.models.prompts import Mode, build_decision_prompt, build_judgment_prompt, build_prompt, eligible
from msep.models.runner import Job
from msep.models.schemas import ModelResponse
from msep.oracle.sufficiency import canonical, composition, is_sufficient

DIAG_LABELS = ["INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER"]
JUDGMENT_SIBLINGS = ("RELEVANT_INSUFFICIENT_INFORMATION", "RELEVANT_INSUFFICIENT_COMPUTATION", "BOTH", "PREMATURE_STOP")
MODES = [m.value for m in Mode]


def load_records(path: Path, splits: tuple[str, ...], max_families: int | None = None) -> list[dict]:
    recs = [json.loads(l) for l in open(path)]
    recs = [r for r in recs if r["split"] in splits]
    if max_families is not None:
        keep = sorted({r["family_id"] for r in recs})[:max_families]
        recs = [r for r in recs if r["family_id"] in set(keep)]
    return recs


def _alias(rec: dict) -> dict:
    return rec["rendering"]["action_alias"]


def judgment_candidates(rec: dict) -> list[tuple[str, tuple[str, ...]]]:
    """(kind, formal plan) candidates for E5a. Labels are recomputed exactly at analysis time."""
    o = rec["oracle"]
    best = tuple(o["optimal_plans"][0])
    out = [("optimal", best)]
    if rec["sibling_type"].startswith("RELEVANT_INSUFFICIENT"):
        out.append(("decoy_only", (rec["notes"]["decoy"],)))
    else:
        for a in best:
            out.append((f"without_{a}", tuple(x for x in best if x != a)))
    return out


def build_jobs(records: list[dict]) -> list[Job]:
    jobs: list[Job] = []
    for rec in records:
        rc = rec["oracle"]["resource_class"]
        text = rec["prompt_text"]
        for mode in Mode:
            if eligible(mode, rc):
                jobs.append(Job("plan", rec["instance_id"], rec["family_id"], mode.value, build_prompt(text, mode, rc)))
        if rec["sibling_type"] in JUDGMENT_SIBLINGS:
            for kind, plan in judgment_candidates(rec):
                shown = sorted(_alias(rec)[a] for a in plan)
                jobs.append(Job("judgment", rec["instance_id"], rec["family_id"], "judgment",
                                build_judgment_prompt(text, shown), candidate=canonical(plan), meta={"kind": kind}))
        if rec["sibling_type"] == "ALREADY_SUFFICIENT":
            jobs.append(Job("decision", rec["instance_id"], rec["family_id"], "base_decision",
                            build_decision_prompt(text)))
    return jobs


# -- per-response scoring --------------------------------------------------------

def _response(parsed: dict) -> ModelResponse:
    return ModelResponse(**parsed)


def score_plan_results(records: dict[str, dict], results: list[dict]) -> list[dict]:
    rows = []
    for r in results:
        rec = records.get(r["instance_id"])
        if rec is None:
            continue
        row = {"instance_id": r["instance_id"], "family_id": r["family_id"], "mode": r["mode"],
               "sibling_type": rec["sibling_type"], "gold_class": rec["oracle"]["resource_class"],
               "valid": r["parsed"] is not None, "status": r["status"]}
        if r["parsed"] is not None:
            resp = _response(r["parsed"])
            s = score(rec, resp)
            inv = {v: k for k, v in _alias(rec).items()}
            plan = [inv.get(p, p) for p in resp.plan]
            row.update(s)
            row.update({"pred_class": resp.resource_class, "stage": classify(rec, resp, s),
                        "plan_formal": plan, "decision": resp.decision, "stop_after_plan": resp.stop_after_plan,
                        "state_sufficient_said": resp.state_sufficient,
                        "plan_composition": composition(instance_from_record(rec).state,
                                                        [p for p in plan if p in inv.values()]).value
                        if not s["unknown_actions"] else "invalid"})
        else:
            row.update({"pred_class": "INVALID", "stage": "invalid", "detection_correct": False,
                        "class_correct": False, "plan_sufficient": False, "plan_optimal": False,
                        "plan_exact_match": False})
        rows.append(row)
    return rows


# -- analyses ------------------------------------------------------------------------

def _rate(rows, key, cond=lambda r: True):
    sel = [r for r in rows if cond(r)]
    return cluster_mean_ci((r["family_id"], bool(r.get(key))) for r in sel)


def analyze_e1(records: dict, plan_rows: list[dict], decision_results: list[dict]) -> dict:
    items = []
    invalid = 0
    for r in decision_results:
        rec = records.get(r["instance_id"])
        if rec is None:
            continue
        truth = "true" if rec["true_target_value"] else "false"
        ok = r["parsed"] is not None and r["parsed"]["decision"] == truth
        invalid += r["parsed"] is None
        items.append((r["family_id"], ok))
    e2e = [x for x in plan_rows if x["mode"] == "end_to_end" and x["gold_class"] == "ALREADY_SUFFICIENT"]
    return {
        "a_base_decision_accuracy": cluster_mean_ci(items), "a_invalid": invalid,
        "b_end_to_end_on_sufficient_states": {
            "says_sufficient": _rate(e2e, "detection_correct"),
            "proposes_any_action": cluster_mean_ci((x["family_id"], x.get("plan_cost", 1) > 0 if x["valid"] else True)
                                                  for x in e2e),
            "decision_correct": cluster_mean_ci((x["family_id"], x.get("decision_correct") is True) for x in e2e),
        },
    }


def analyze_e3(plan_rows: list[dict]) -> dict:
    out = {}
    for mode in ("detection_controlled", "end_to_end"):
        rows = [r for r in plan_rows if r["mode"] == mode and r["gold_class"] in DIAG_LABELS]
        tri = [(r["family_id"], r["gold_class"], r["pred_class"]) for r in rows]
        gold = [g for _, g, _ in tri]
        pred = [p for _, _, p in tri]
        res = {
            "n": len(rows), "invalid": sum(not r["valid"] for r in rows),
            "accuracy": _rate(rows, "class_correct"),
            "macro_f1": cluster_stat_ci(tri, macro_f1, DIAG_LABELS),
            "balanced_accuracy": cluster_stat_ci(tri, balanced_accuracy, DIAG_LABELS),
            "confusion": confusion(gold, pred, DIAG_LABELS + ["ALREADY_SUFFICIENT"]) if rows else {},
            "accuracy_by_sibling": {t: _rate(rows, "class_correct", lambda r, t=t: r["sibling_type"] == t)["mean"]
                                    for t in sorted({r["sibling_type"] for r in rows})},
        }
        if mode == "end_to_end":
            res["detection_accuracy"] = _rate(rows, "detection_correct")
            res["diagnosis_given_detected"] = _rate(rows, "class_correct", lambda r: r.get("detection_correct"))
        # H2: diagnosis vs plan sufficiency on resolvable instances
        resolv = [r for r in rows if r["gold_class"] != "NEITHER"]
        res["h2_class_correct"] = _rate(resolv, "class_correct")
        res["h2_plan_sufficient"] = _rate(resolv, "plan_sufficient")
        res["h2_plan_sufficient_given_class_correct"] = _rate(resolv, "plan_sufficient", lambda r: r["class_correct"])
        res["h2_paired_class_minus_sufficient"] = paired_diff_ci(
            (r["family_id"], float(r["class_correct"]), float(r["plan_sufficient"])) for r in resolv)
        res["h2_mcnemar"] = mcnemar_exact((r["class_correct"], r["plan_sufficient"]) for r in resolv)
        out[mode] = res
    return out


def analyze_e5(records: dict, judgment_results: list[dict], plan_rows: list[dict]) -> dict:
    # (a) judgments, with labels recomputed exactly
    by_inst: dict = defaultdict(dict)
    items = []
    for r in judgment_results:
        rec = records.get(r["instance_id"])
        if rec is None:
            continue
        st = instance_from_record(rec).state
        label = is_sufficient(st, tuple(r["candidate"]))
        relevant = all(a["relevant"] for a in rec["oracle"]["actions"] if a["name"] in r["candidate"])
        said = None if r["parsed"] is None else r["parsed"]["plan_sufficient"]
        ok = said is not None and said == label
        item = {"family_id": r["family_id"], "instance_id": r["instance_id"], "sibling": rec["sibling_type"],
                "kind": r["meta"]["kind"], "label_sufficient": label, "relevant": relevant, "correct": ok,
                "said_sufficient": said}
        items.append(item)
        by_inst[r["instance_id"]][r["meta"]["kind"]] = item
    suff = [i for i in items if i["label_sufficient"]]
    insuff = [i for i in items if not i["label_sufficient"]]
    pairs = []
    for inst, d in by_inst.items():
        if "optimal" not in d:
            continue
        for k, it in d.items():
            if k != "optimal":
                pairs.append((it["family_id"], d["optimal"]["correct"], it["correct"]))
    judg = {
        "n_items": len(items), "invalid": sum(i["said_sufficient"] is None for i in items),
        "all_insufficient_candidates_relevant": all(i["relevant"] for i in insuff),
        "accuracy_sufficient_candidates": cluster_mean_ci((i["family_id"], i["correct"]) for i in suff),
        "accuracy_relevant_insufficient_candidates": cluster_mean_ci((i["family_id"], i["correct"]) for i in insuff),
        "relevant_insufficient_judged_sufficient": cluster_mean_ci(
            (i["family_id"], i["said_sufficient"] is True) for i in insuff),
        "pair_both_correct": cluster_mean_ci((f, a and b) for f, a, b in pairs),
        "paired_diff_sufficient_minus_insufficient": paired_diff_ci((f, float(a), float(b)) for f, a, b in pairs),
        "mcnemar": mcnemar_exact((a, b) for _, a, b in pairs),
        "by_sibling_and_kind": {
            f"{s}/{k}": cluster_mean_ci((i["family_id"], i["correct"]) for i in items if i["sibling"] == s and
                                        (i["kind"] == k))["mean"]
            for s, k in sorted({(i["sibling"], "optimal" if i["kind"] == "optimal" else i["kind"]) for i in items})},
    }
    # (b) construction in decoy siblings vs matched clean siblings
    constr = {}
    match = {"RELEVANT_INSUFFICIENT_INFORMATION": "INFORMATION_ONLY",
             "RELEVANT_INSUFFICIENT_COMPUTATION": "COMPUTATION_ONLY"}
    for mode in ("detection_controlled", "diagnosis_controlled", "end_to_end"):
        res = {}
        for decoy_t, clean_t in match.items():
            dec = {r["family_id"]: r for r in plan_rows if r["mode"] == mode and r["sibling_type"] == decoy_t}
            cln = {r["family_id"]: r for r in plan_rows if r["mode"] == mode and r["sibling_type"] == clean_t}
            fams = sorted(set(dec) & set(cln))
            decoy_name = {"RELEVANT_INSUFFICIENT_INFORMATION": "ASK_dw", "RELEVANT_INSUFFICIENT_COMPUTATION": "COMPUTE_dc"}[decoy_t]
            res[decoy_t] = {
                "families": len(fams),
                "plan_sufficient_with_decoy": cluster_mean_ci((f, dec[f]["plan_sufficient"]) for f in fams),
                "plan_sufficient_clean_sibling": cluster_mean_ci((f, cln[f]["plan_sufficient"]) for f in fams),
                "decoy_selected": cluster_mean_ci((f, decoy_name in (dec[f].get("plan_formal") or [])) for f in fams),
                "decoy_only_plan": cluster_mean_ci((f, (dec[f].get("plan_formal") or []) == [decoy_name]) for f in fams),
                "mcnemar_clean_vs_decoy": mcnemar_exact((cln[f]["plan_sufficient"], dec[f]["plan_sufficient"]) for f in fams),
            }
        constr[mode] = res
    return {"a_judgment": judg, "b_construction": constr}


def analyze_e7(plan_rows: list[dict]) -> dict:
    out = {}
    core = ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH")
    for mode in ("detection_controlled", "diagnosis_controlled", "end_to_end"):
        rows = [r for r in plan_rows if r["mode"] == mode and r["sibling_type"] in core]
        by_t = {t: {r["family_id"]: r for r in rows if r["sibling_type"] == t} for t in core}
        res = {"per_class": {}}
        for t in core:
            rr = list(by_t[t].values())
            res["per_class"][t] = {
                "n": len(rr), "invalid": sum(not r["valid"] for r in rr),
                "class_correct": None if mode == "diagnosis_controlled" else _rate(rr, "class_correct")["mean"],
                "plan_sufficient": _rate(rr, "plan_sufficient"),
                "plan_optimal": _rate(rr, "plan_optimal")["mean"],
                "exact_match": _rate(rr, "plan_exact_match")["mean"],
                "stages": dict(Counter(r["stage"] for r in rr)),
            }
        both = by_t["BOTH"]
        res["both_single_resource_plans"] = cluster_mean_ci(
            (f, r.get("plan_composition") in ("information", "computation")) for f, r in both.items())
        for single in ("INFORMATION_ONLY", "COMPUTATION_ONLY"):
            fams = sorted(set(both) & set(by_t[single]))
            res[f"paired_{single}_minus_BOTH_plan_sufficient"] = paired_diff_ci(
                (f, float(by_t[single][f]["plan_sufficient"]), float(both[f]["plan_sufficient"])) for f in fams)
            res[f"mcnemar_{single}_vs_BOTH"] = mcnemar_exact(
                (by_t[single][f]["plan_sufficient"], both[f]["plan_sufficient"]) for f in fams)
        out[mode] = res
    return out


# -- usage, cost, ceiling/floor ----------------------------------------------------------

def _pct(xs: list[float]) -> dict | None:
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    q = lambda p: xs[min(len(xs) - 1, int(p * (len(xs) - 1) + 0.5))]  # noqa: E731
    return {"n": len(xs), "min": xs[0], "p10": q(0.1), "p50": q(0.5), "p90": q(0.9), "max": xs[-1],
            "mean": sum(xs) / len(xs)}


def usage_summary(results: list[dict]) -> dict:
    """Status rates, exact token distributions and recorded cost, per pool and overall."""
    def block(rs):
        n = len(rs)
        st = Counter(r["status"] for r in rs)
        toks = [r.get("tokens") or {} for r in rs]
        costs = [r.get("cost_usd") for r in rs if r.get("cost_usd") is not None]
        return {
            "requests": n, "status": dict(st),
            "parse_error_rate": (sum(1 for r in rs if r.get("parse_error")) / n) if n else None,
            "refusal_rate": st.get("refusal", 0) / n if n else None,
            "truncation_rate": st.get("truncated", 0) / n if n else None,
            "input_tokens": _pct([t.get("input_tokens") for t in toks]),
            "output_tokens": _pct([t.get("output_tokens") for t in toks]),
            "reasoning_tokens": _pct([t.get("reasoning_tokens") for t in toks]),
            "cost_usd_total": round(sum(costs), 6), "cost_usd_per_request": _pct(costs),
            # key names kept for compatibility; the unit is the model's price currency
            "currency": next(((r.get("prices") or {}).get("currency", "usd") for r in rs if r.get("prices")), "usd"),
            "served_models": dict(Counter(r.get("served_model") for r in rs if r.get("served_model"))),
        }
    out = {"all": block(results)}
    for pool in ("plan", "judgment", "decision"):
        out[pool] = block([r for r in results if r["pool"] == pool])
    return out


def ceiling_floor(model_summary: dict, hi: float = 0.95, lo: float = 0.05) -> list[dict]:
    """Headline rates at or beyond the ceiling/floor thresholds. Small-n caveat applies."""
    cands = []
    e1 = model_summary.get("E1")
    if e1:
        cands.append(("E1 base decision accuracy", e1["a_base_decision_accuracy"]))
    for mode, r in (model_summary.get("E3") or {}).items():
        if mode not in MODES:
            continue
        cands.append((f"E3 {mode} class accuracy", r["accuracy"]))
        cands.append((f"E3 {mode} plan sufficient (resolvable)", r["h2_plan_sufficient"]))
    j = (model_summary.get("E5") or {}).get("a_judgment")
    if j:
        cands.append(("E5 judgment accuracy, sufficient plans", j["accuracy_sufficient_candidates"]))
        cands.append(("E5 judgment accuracy, relevant-insufficient plans", j["accuracy_relevant_insufficient_candidates"]))
    for mode, r in (model_summary.get("E7") or {}).items():
        for t, c in r["per_class"].items():
            cands.append((f"E7 {mode} {t} plan sufficient", c["plan_sufficient"]))
    flags = []
    for name, ci in cands:
        m = ci.get("mean") if isinstance(ci, dict) else None
        if m is None:
            continue
        if m >= hi or m <= lo:
            flags.append({"metric": name, "mean": m, "n": ci.get("n"), "kind": "ceiling" if m >= hi else "floor"})
    return flags


# -- report ------------------------------------------------------------------------------

def _fmt(ci) -> str:
    if not isinstance(ci, dict) or ci.get("mean", ci.get("value")) is None:
        return "–"
    v = ci.get("mean", ci.get("value"))
    if ci.get("lo") is None:
        return f"{v:.2f}"
    return f"{v:.2f} [{ci['lo']:.2f}, {ci['hi']:.2f}]"


def markdown_report(summary: dict) -> str:
    L = [f"# Phase 2 pilot: E1, E3, E5, E7", "",
         f"Split(s): {', '.join(summary['splits'])} · families: {summary['families']} · prompt version "
         f"`{summary['prompt_version']}` · models: {', '.join(summary['models'])}", "",
         "Exploratory pilot. 95% intervals are family-clustered bootstrap. Each mode is reported on its own. "
         "End-to-End errors mix detection with planning and are not evidence of a planning failure. Unparseable "
         "or failed responses count as incorrect.", ""]
    for mk, s in summary["by_model"].items():
        L += [f"## {mk}", "", f"Responses (plan pool): {s['response_status']}", ""]
        u = s.get("usage")
        if u:
            L += ["### Usage and cost (exact provider-reported tokens)", "",
                  "| Pool | Requests | Parse err. | Refusal | Truncated | Output tokens p50 / p90 / max | Reasoning p50 | Input p50 | Cost total | Cost / request p50 |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for pool, b in u.items():
                if not b["requests"]:
                    continue
                o, rz, i, c = b["output_tokens"], b["reasoning_tokens"], b["input_tokens"], b["cost_usd_per_request"]
                out_s = "{} / {} / {}".format(o["p50"], o["p90"], o["max"]) if o else "–"
                rz_s = str(rz["p50"]) if rz else "–"
                in_s = str(i["p50"]) if i else "–"
                c_s = "${:.5f}".format(c["p50"]) if c else "–"
                L.append(f"| {pool} | {b['requests']} | {b['parse_error_rate']:.1%} | {b['refusal_rate']:.1%} | "
                         f"{b['truncation_rate']:.1%} | {out_s} | {rz_s} | {in_s} | ${b['cost_usd_total']:.4f} | {c_s} |")
            L.append("")
        cf = s.get("ceiling_floor")
        if cf is not None:
            L += ["### Ceiling / floor flags (mean ≥ 0.95 or ≤ 0.05)", ""]
            L += [f"- {f['kind']}: {f['metric']} = {f['mean']:.2f} (n = {f['n']})" for f in cf] or ["- none"]
            L.append("")
        e1 = s["E1"]
        L += ["### E1 base competence (already-sufficient states)", "",
              f"- Base decision accuracy: {_fmt(e1['a_base_decision_accuracy'])}",
              f"- End-to-End on the same states: says sufficient {_fmt(e1['b_end_to_end_on_sufficient_states']['says_sufficient'])}, "
              f"proposes an action {_fmt(e1['b_end_to_end_on_sufficient_states']['proposes_any_action'])}", ""]
        L += ["### E3 resource diagnosis", "", "| Mode | n | Accuracy | Macro-F1 | Balanced acc. | Class correct (resolvable) | Plan sufficient (resolvable) | Plan sufficient given class correct |",
              "|---|---|---|---|---|---|---|---|"]
        for mode, r in s["E3"].items():
            L.append(f"| {mode} | {r['n']} | {_fmt(r['accuracy'])} | {_fmt(r['macro_f1'])} | {_fmt(r['balanced_accuracy'])} | "
                     f"{_fmt(r['h2_class_correct'])} | {_fmt(r['h2_plan_sufficient'])} | {_fmt(r['h2_plan_sufficient_given_class_correct'])} |")
        L.append("")
        j = s["E5"]["a_judgment"]
        L += ["### E5 relevance vs sufficiency", "",
              f"- Judgment accuracy, sufficient plans: {_fmt(j['accuracy_sufficient_candidates'])}",
              f"- Judgment accuracy, relevant-but-insufficient plans: {_fmt(j['accuracy_relevant_insufficient_candidates'])}",
              f"- Relevant-but-insufficient plans judged sufficient: {_fmt(j['relevant_insufficient_judged_sufficient'])}",
              f"- Matched pairs both correct: {_fmt(j['pair_both_correct'])}; McNemar p = {j['mcnemar']['p_value']:.3g}", "",
              "| Mode | Decoy sibling | Plan sufficient (with decoy) | Plan sufficient (clean sibling) | Decoy chosen | Decoy-only plan |",
              "|---|---|---|---|---|---|"]
        for mode, rr in s["E5"]["b_construction"].items():
            for t, r in rr.items():
                L.append(f"| {mode} | {t} | {_fmt(r['plan_sufficient_with_decoy'])} | {_fmt(r['plan_sufficient_clean_sibling'])} | "
                         f"{_fmt(r['decoy_selected'])} | {_fmt(r['decoy_only_plan'])} |")
        L += ["", "### E7 BOTH vs single-resource", "",
              "| Mode | Class | n | Class correct | Plan sufficient | Plan optimal |", "|---|---|---|---|---|---|"]
        for mode, r in s["E7"].items():
            for t, c in r["per_class"].items():
                cc = "–" if c["class_correct"] is None else f"{c['class_correct']:.2f}"
                L.append(f"| {mode} | {t} | {c['n']} | {cc} | {_fmt(c['plan_sufficient'])} | "
                         f"{'–' if c['plan_optimal'] is None else format(c['plan_optimal'], '.2f')} |")
        L.append("")
        for mode, r in s["E7"].items():
            L.append(f"- {mode}: BOTH plans that use only one resource type {_fmt(r['both_single_resource_plans'])}; "
                     f"INFORMATION_ONLY − BOTH {_fmt(r['paired_INFORMATION_ONLY_minus_BOTH_plan_sufficient'])} "
                     f"(McNemar p = {r['mcnemar_INFORMATION_ONLY_vs_BOTH']['p_value']:.3g}); "
                     f"COMPUTATION_ONLY − BOTH {_fmt(r['paired_COMPUTATION_ONLY_minus_BOTH_plan_sufficient'])} "
                     f"(McNemar p = {r['mcnemar_COMPUTATION_ONLY_vs_BOTH']['p_value']:.3g})")
        L.append("")
    return "\n".join(L) + "\n"
