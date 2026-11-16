"""Diagnostic re-analysis of the 10-family dev calibration from saved raw responses (no API calls).

Separates sufficiency from optimality, reports every rate on two stated bases (all attempted
answers, where an unparsed or truncated answer counts as a failure, and parsed answers only),
with n, unparsed counts and family counts, and 95% family-clustered bootstrap intervals.

Conditions are never mixed silently. Original conditions are the calibration runs as made.
Corrected conditions are separate and labelled:
- a model key run under changed settings on every job (e.g. forced schema), and
- a "recovered" condition: the original records with only the originally truncated jobs replaced
  by re-runs under a higher output cap (mixed settings, stated as such).

Calibration is diagnostic, not confirmatory: no p-values are reported here.

    python experiments/analyze_calibration.py --data data/generated/pool_v3/instances.jsonl \
        --out results/aggregate/diagnostics_2026-11-13
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from msep.eval import pilot
from msep.eval.bootstrap import cluster_mean_ci, paired_diff_ci
from msep.eval.experiments import RESOLVABLE
from msep.models.runner import load_results

ROOT = Path(__file__).resolve().parents[1]
MODES = ("end_to_end", "detection_controlled", "diagnosis_controlled")
MODE_SHORT = {"end_to_end": "E2E", "detection_controlled": "DC", "diagnosis_controlled": "DxC"}
CLASSES = ("ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER")
CEILING = 0.95  # same threshold as the report's ceiling flags

# (label, kind, how to build)
CONDITIONS = [
    ("qwen3.5-397b", "original", {"key": "adaption-qwen3.5-397b"}),
    ("qwen3.8-27b", "original", {"key": "adaption-qwen3.8-27b"}),
    ("deepseek-v4-flash", "original", {"key": "adaption-deepseek-v4-flash"}),
    ("gemma-4-26b", "original", {"key": "adaption-gemma-4-26b-a4b-it"}),
    ("gemma-4-26b +schema", "corrected: forced JSON-schema function tool, all jobs",
     {"key": "adaption-gemma-4-26b-a4b-it-schema", "expected_like": "adaption-gemma-4-26b-a4b-it"}),
    ("glm-5.3-flash", "original", {"key": "adaption-glm-53-flash"}),
    ("glm-5.3-flash recovered", "corrected (mixed caps): 16k answers + 32k re-runs of the 16k truncations",
     {"key": "adaption-glm-53-flash", "replace_truncated_with": "adaption-glm-53-flash-32k"}),
]
BASELINE = ("h1++ (heuristic-h1pp)", "heuristics", "heuristic-h1pp")


def _job_key(r: dict) -> tuple:
    return (r["pool"], r["instance_id"], r["mode"], tuple(r.get("candidate") or ()))


def load_condition(raw: Path, spec: dict, by_id: dict) -> tuple[list[dict], dict]:
    """All pools' records for a condition, restricted to the calibration instances, plus provenance notes."""
    pools = ("plan", "judgment", "decision")
    recs = [r for p in pools for r in load_results(raw, p, spec["key"]) if r["instance_id"] in by_id]
    notes: dict = {"source_key": spec["key"], "records": len(recs)}
    if "expected_like" in spec:  # missingness relative to the original job set
        expected = {_job_key(r) for p in pools for r in load_results(raw, p, spec["expected_like"])
                    if r["instance_id"] in by_id}
        have = {_job_key(r) for r in recs}
        notes["expected_jobs"] = len(expected)
        notes["missing_jobs"] = len(expected - have)
    if "replace_truncated_with" in spec:
        reruns = {_job_key(r): r for p in pools
                  for r in load_results(raw, p, spec["replace_truncated_with"]) if r["instance_id"] in by_id}
        out, replaced, not_rerun = [], 0, 0
        for r in recs:
            if r["status"] == "truncated":
                x = reruns.get(_job_key(r))
                if x is not None:
                    out.append(x)
                    replaced += 1
                    continue
                not_rerun += 1
            out.append(r)
        notes.update({"rerun_key": spec["replace_truncated_with"], "replaced": replaced,
                      "truncated_without_rerun": not_rerun,
                      "rerun_status": dict(Counter(x["status"] for x in reruns.values())),
                      "rerun_parse_errors": sum(bool(x["parse_error"]) for x in reruns.values())})
        recs = out
    return recs, notes


def _ci(rows, key, cond=lambda r: True) -> dict:
    sel = [r for r in rows if cond(r)]
    return cluster_mean_ci((r["family_id"], bool(r.get(key))) for r in sel)


def _mean(rows, key) -> dict:
    sel = [r for r in rows if r.get(key) is not None]
    return cluster_mean_ci((r["family_id"], float(r[key])) for r in sel)


def format_summary(recs: list[dict]) -> dict:
    out = {}
    for pool in ("plan", "judgment", "decision"):
        rr = [r for r in recs if r["pool"] == pool]
        out[pool] = {"n": len(rr), "status": dict(Counter(r["status"] for r in rr)),
                     "parse_errors": sum(bool(r["parse_error"]) for r in rr),
                     "parse_error_kinds": dict(Counter(str(r["parse_error"])[:60] for r in rr
                                                       if r["parse_error"]).most_common(4))}
    allr = recs
    out["all"] = {"n": len(allr), "parse_error_rate": sum(bool(r["parse_error"]) for r in allr) / max(1, len(allr)),
                  "truncation_rate": sum(r["status"] == "truncated" for r in allr) / max(1, len(allr)),
                  "truncated_without_text": sum(r["status"] == "truncated" and not r.get("text") for r in allr),
                  "answered_but_unparsed": sum(bool(r["parse_error"]) and bool(r.get("text")) for r in allr)}
    return out


def mode_metrics(rows: list[dict]) -> dict:
    out = {}
    for mode in MODES:
        mr = [r for r in rows if r["mode"] == mode]
        res = [r for r in mr if r["gold_class"] in RESOLVABLE]
        par = [r for r in res if r["valid"]]
        suff = [r for r in par if r.get("plan_sufficient")]
        out[mode] = {
            "n_items": len(mr), "n_resolvable": len(res), "unparsed_resolvable": len(res) - len(par),
            "unparsed_items": sum(not r["valid"] for r in mr), "truncated_items": sum(r["status"] == "truncated" for r in mr),
            "families": len({r["family_id"] for r in mr}),
            "class_acc_all": _ci(mr, "class_correct"), "class_acc_parsed": _ci([r for r in mr if r["valid"]], "class_correct"),
            "suff_all": _ci(res, "plan_sufficient"), "suff_parsed": _ci(par, "plan_sufficient"),
            "opt_all": _ci(res, "plan_optimal"), "opt_parsed": _ci(par, "plan_optimal"),
            "opt_given_suff": _ci(suff, "plan_optimal"),
            "regret_parsed": _mean(par, "regret"),
            "excess_cost_given_suff": _mean(suff, "excess_cost"),
            # why a sufficient plan is not optimal: redundant actions (not minimal) vs a minimal plan that
            # is not the cheapest (a cost choice, what E10 probes)
            "suff_not_optimal": sum(not r.get("plan_optimal") for r in suff),
            "suff_not_optimal_nonminimal": sum(not r.get("plan_optimal") and not r.get("plan_minimal") for r in suff),
            "suff_not_optimal_minimal_dearer": sum(not r.get("plan_optimal") and bool(r.get("plan_minimal")) for r in suff),
            "insufficient_parsed": sum(not r.get("plan_sufficient") for r in par),
        }
    return out


def class_metrics(rows: list[dict]) -> dict:
    out = {}
    for mode in MODES:
        for c in CLASSES:
            cr = [r for r in rows if r["mode"] == mode and r["gold_class"] == c]
            if not cr:
                continue
            par = [r for r in cr if r["valid"]]
            d = {"n": len(cr), "unparsed": len(cr) - len(par), "families": len({r["family_id"] for r in cr}),
                 "class_acc_all": _ci(cr, "class_correct")}
            if c in RESOLVABLE:
                d.update({"suff_all": _ci(cr, "plan_sufficient"), "suff_parsed": _ci(par, "plan_sufficient"),
                          "opt_all": _ci(cr, "plan_optimal"), "opt_parsed": _ci(par, "plan_optimal"),
                          "regret_parsed": _mean(par, "regret")})
            elif c == "NEITHER":
                d["defer_parsed"] = cluster_mean_ci((r["family_id"], r.get("decision") == "defer") for r in par)
            else:  # ALREADY_SUFFICIENT: the empty plan is optimal; an answer (not defer) is expected
                d["empty_plan_parsed"] = cluster_mean_ci((r["family_id"], not r.get("plan_formal")) for r in par)
            out[f"{mode}|{c}"] = d
    return out


def versus(rows: list[dict], base_rows: list[dict]) -> dict:
    """Same (instance, mode) pairs, resolvable states only, against the h1++ baseline."""
    base = {(r["instance_id"], r["mode"]): r for r in base_rows}
    out = {}
    for mode in MODES:
        pairs = [(r, base[(r["instance_id"], mode)]) for r in rows
                 if r["mode"] == mode and r["gold_class"] in RESOLVABLE and (r["instance_id"], mode) in base]
        par = [(r, b) for r, b in pairs if r["valid"]]
        out[mode] = {
            "pairs_all": len(pairs), "pairs_parsed": len(par), "families": len({r["family_id"] for r, _ in pairs}),
            "opt_diff_all": paired_diff_ci((r["family_id"], float(bool(r.get("plan_optimal"))),
                                            float(bool(b.get("plan_optimal")))) for r, b in pairs),
            "opt_diff_parsed": paired_diff_ci((r["family_id"], float(bool(r.get("plan_optimal"))),
                                               float(bool(b.get("plan_optimal")))) for r, b in par),
            "suff_diff_all": paired_diff_ci((r["family_id"], float(bool(r.get("plan_sufficient"))),
                                             float(bool(b.get("plan_sufficient")))) for r, b in pairs),
            "class_diff_all": paired_diff_ci((r["family_id"], float(bool(r.get("class_correct"))),
                                              float(bool(b.get("class_correct")))) for r, b in pairs),
        }
    return out


def ceilings(mm: dict) -> dict:
    out = {}
    for mode, m in mm.items():
        s, o = m["suff_all"]["mean"], m["opt_all"]["mean"]
        out[mode] = {"sufficiency_ceiling": s is not None and s >= CEILING,
                     "optimality_ceiling": o is not None and o >= CEILING,
                     "sufficiency_minus_optimality": None if s is None or o is None else s - o}
    return out


# -- rendering -------------------------------------------------------------------------

def f(ci: dict | None, digits: int = 2) -> str:
    if not ci or ci.get("mean") is None:
        return "–"
    if ci.get("lo") is None:
        return f"{ci['mean']:.{digits}f}"
    return f"{ci['mean']:.{digits}f} [{ci['lo']:.{digits}f}, {ci['hi']:.{digits}f}]"


def render(summary: dict) -> str:
    L = ["# Calibration diagnostics (dev, 10 families)", "",
         "Diagnostic re-analysis from saved raw responses; no API calls. **Not confirmatory**: 10 families, "
         "so intervals are wide and no significance tests are reported. Intervals are 95% family-clustered "
         "bootstrap (ratio of sums). *all* = every attempted answer, an unparsed or truncated answer counts as a "
         "failure; *parsed* = parsed answers only. Optimality = sufficient and minimum cost. "
         f"Ceiling = point estimate ≥ {CEILING} on the *all* basis.", "",
         "Corrected conditions are separate rows, never merged into the originals. "
         "`glm-5.3-flash recovered` mixes two output caps (16k for originally answered jobs, 32k for the "
         "re-run of the originally truncated ones) and is a sensitivity analysis, not a clean condition.", ""]
    L += ["## Conditions and format reliability (all pools: plan, judgment, decision)", "",
          "| Condition | Kind | Requests | Parse-error rate | Truncation rate | Truncated, no text | Answered but unparsed | Notes |",
          "|---|---|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        a = c["format"]["all"]
        notes = {k: v for k, v in c["notes"].items() if k not in ("records",)}
        L.append(f"| {lab} | {c['kind']} | {a['n']} | {a['parse_error_rate']:.3f} | {a['truncation_rate']:.3f} | "
                 f"{a['truncated_without_text']} | {a['answered_but_unparsed']} | {json.dumps(notes)} |")
    L += ["", "Parse-error kinds by pool:", ""]
    for lab, c in summary["conditions"].items():
        kinds = {p: c["format"][p]["parse_error_kinds"] for p in ("plan", "judgment", "decision")
                 if c["format"][p]["parse_error_kinds"]}
        if kinds:
            L.append(f"- {lab}: {json.dumps(kinds)}")
    L += ["", "## Sufficiency vs optimality by mode (resolvable states)", "",
          "| Condition | Mode | n (fam) | unparsed | Sufficient, all | Sufficient, parsed | Optimal, all | "
          "Optimal, parsed | Optimal given sufficient | Excess cost given sufficient | Regret, parsed | Ceiling: suff / opt |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        for mode in MODES:
            m, ce = c["modes"][mode], c["ceilings"][mode]
            L.append(f"| {lab} | {MODE_SHORT[mode]} | {m['n_resolvable']} ({m['families']}) | {m['unparsed_resolvable']} | "
                     f"{f(m['suff_all'])} | {f(m['suff_parsed'])} | {f(m['opt_all'])} | {f(m['opt_parsed'])} | "
                     f"{f(m['opt_given_suff'])} (n={m['opt_given_suff']['n']}) | {f(m['excess_cost_given_suff'])} | "
                     f"{f(m['regret_parsed'])} | {'Y' if ce['sufficiency_ceiling'] else 'n'} / "
                     f"{'Y' if ce['optimality_ceiling'] else 'n'} |")
    L += ["", "## Where optimality is lost (resolvable states, counts)", "",
          "A sufficient plan that is not optimal either contains redundant actions (not minimal) or is minimal "
          "but not the cheapest minimal plan (a cost choice).", "",
          "| Condition | Mode | Parsed | Insufficient | Sufficient | Sufficient, not optimal | of which redundant (not minimal) | "
          "of which minimal but dearer |", "|---|---|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        for mode in MODES:
            m = c["modes"][mode]
            parsed = m["n_resolvable"] - m["unparsed_resolvable"]
            L.append(f"| {lab} | {MODE_SHORT[mode]} | {parsed} | {m['insufficient_parsed']} | "
                     f"{m['opt_given_suff']['n']} | {m['suff_not_optimal']} | {m['suff_not_optimal_nonminimal']} | "
                     f"{m['suff_not_optimal_minimal_dearer']} |")
    L += ["", "## Resource-class diagnosis by mode (all items)", "",
          "In Diagnosis-Controlled the class is given, so accuracy there measures instruction compliance.", "",
          "| Condition | Mode | n | unparsed | Class acc., all | Class acc., parsed |", "|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        for mode in MODES:
            m = c["modes"][mode]
            L.append(f"| {lab} | {MODE_SHORT[mode]} | {m['n_items']} | {m['unparsed_items']} | "
                     f"{f(m['class_acc_all'])} | {f(m['class_acc_parsed'])} |")
    L += ["", "## By gold resource class", "",
          "| Condition | Mode | Class | n (fam) | unparsed | Class acc., all | Sufficient, all | Optimal, all | "
          "Optimal, parsed | Regret, parsed | NEITHER: defer (parsed) | ALREADY_SUFFICIENT: empty plan (parsed) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        for k, d in c["classes"].items():
            mode, cls = k.split("|")
            L.append(f"| {lab} | {MODE_SHORT[mode]} | {cls} | {d['n']} ({d['families']}) | {d['unparsed']} | "
                     f"{f(d['class_acc_all'])} | {f(d.get('suff_all'))} | {f(d.get('opt_all'))} | "
                     f"{f(d.get('opt_parsed'))} | {f(d.get('regret_parsed'))} | {f(d.get('defer_parsed'))} | "
                     f"{f(d.get('empty_plan_parsed'))} |")
    L += ["", f"## Versus {BASELINE[0]} on exactly the same (instance, mode) pairs (resolvable states)", "",
          "Model minus baseline; positive favours the model. *all* keeps the model's unparsed answers as failures; "
          "*parsed* drops pairs where the model's answer did not parse (the baseline always parses).", "",
          "| Condition | Mode | pairs all / parsed (fam) | Optimal diff, all | Optimal diff, parsed | "
          "Sufficient diff, all | Class diff, all |", "|---|---|---|---|---|---|---|"]
    for lab, c in summary["conditions"].items():
        for mode in MODES:
            v = c["versus_h1pp"][mode]
            L.append(f"| {lab} | {MODE_SHORT[mode]} | {v['pairs_all']} / {v['pairs_parsed']} ({v['families']}) | "
                     f"{f(v['opt_diff_all'])} | {f(v['opt_diff_parsed'])} | {f(v['suff_diff_all'])} | "
                     f"{f(v['class_diff_all'])} |")
    b = summary["baseline"]
    L += ["", f"Baseline {BASELINE[0]} itself:", ""]
    for mode in MODES:
        m = b[mode]
        L.append(f"- {MODE_SHORT[mode]}: n={m['n_resolvable']}, sufficient {f(m['suff_all'])}, optimal {f(m['opt_all'])}, "
                 f"optimal given sufficient {f(m['opt_given_suff'])}, class acc. {f(m['class_acc_all'])}")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--splits", default="dev")
    ap.add_argument("--max-families", type=int, default=10)
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "diagnostics"))
    a = ap.parse_args(argv)
    splits = tuple(s.strip() for s in a.splits.split(","))
    if "test" in splits:
        print("refusing the test split")
        return 2
    by_id = {r["instance_id"]: r for r in pilot.load_records(Path(a.data), splits, a.max_families)}
    raw = Path(a.raw)
    base_rows = pilot.score_plan_results(by_id, [r for r in load_results(raw / BASELINE[1], "plan", BASELINE[2])
                                                 if r["instance_id"] in by_id])
    summary = {"splits": list(splits), "families": len({r["family_id"] for r in by_id.values()}),
               "instances": len(by_id), "baseline": mode_metrics(base_rows), "conditions": {}}
    for lab, kind, spec in CONDITIONS:
        recs, notes = load_condition(raw, spec, by_id)
        if not recs:
            print(f"skip {lab}: no records under {spec['key']}")
            continue
        rows = pilot.score_plan_results(by_id, [r for r in recs if r["pool"] == "plan"])
        mm = mode_metrics(rows)
        summary["conditions"][lab] = {"kind": kind, "notes": notes, "format": format_summary(recs), "modes": mm,
                                      "ceilings": ceilings(mm), "classes": class_metrics(rows),
                                      "versus_h1pp": versus(rows, base_rows)}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagnostics.json").write_text(json.dumps(summary, indent=1, default=str))
    (out / "diagnostics.md").write_text(render(summary))
    print(f"wrote {out / 'diagnostics.md'} and diagnostics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
