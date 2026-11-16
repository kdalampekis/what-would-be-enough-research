"""One entry point that computes every analysis from saved raw results.

Used by both the real pilot (run_pilot.py) and the synthetic offline run
(run_offline.py), so the mocks exercise exactly the code that will analyse
real models.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from msep.models.runner import load_results

from . import experiments as ex
from . import pilot

_STRATA: dict[str, str] = {}


def _stratum(rec: dict) -> str:
    """heuristic_easy / heuristic_hard for the h1pp shallow baseline (cached; text-only)."""
    from msep.benchmark.audit import heuristic_stratum
    if rec["instance_id"] not in _STRATA:
        _STRATA[rec["instance_id"]] = heuristic_stratum(rec)
    return _STRATA[rec["instance_id"]]


ALL_EXPERIMENTS = ("e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "e10", "e11", "e12")


def analyze_model(raw: Path, model_key: str, records: dict, experiments=ALL_EXPERIMENTS,
                  train_records: list[dict] | None = None) -> dict:
    plan_res = [r for r in load_results(raw, "plan", model_key) if r["instance_id"] in records]
    rows = pilot.score_plan_results(records, plan_res)
    all_res = [r for pool in ("plan", "judgment", "decision", "plan_cost", "plan_risk", "plan_shift", "capability")
               for r in load_results(raw, pool, model_key) if r["instance_id"] in records]
    s: dict = {"response_status": dict(Counter(r["status"] for r in plan_res)), "usage": pilot.usage_summary(all_res),
               "synthetic": any((r.get("raw_response") or {}).get("synthetic") for r in all_res)}
    exps = set(experiments)
    if "e1" in exps:
        s["E1"] = pilot.analyze_e1(records, rows, [r for r in load_results(raw, "decision", model_key)
                                                   if r["instance_id"] in records])
    if "e2" in exps:
        s["E2"] = ex.analyze_e2(rows)
    if "e3" in exps:
        s["E3"] = pilot.analyze_e3(rows)
        if train_records:
            evald = [records[i] for i in {r["instance_id"] for r in rows}]
            s["E3"]["surface_feature_baseline"] = ex.surface_baseline(train_records, evald)
    if "e4" in exps:
        s["E4"] = ex.analyze_e4(rows, records)
    if "e5" in exps:
        s["E5"] = pilot.analyze_e5(records, [r for r in load_results(raw, "judgment", model_key)
                                             if r["instance_id"] in records], rows)
    if "e6" in exps:
        s["E6"] = ex.analyze_e6(rows)
    if "e7" in exps:
        s["E7"] = pilot.analyze_e7(rows)
    if "e8" in exps:
        s["E8"] = ex.analyze_e8(rows)
    if "e9" in exps:
        s["E9"] = ex.analyze_e9(rows, records)
    for e, pool, fn in (("e10", "plan_cost", ex.analyze_e10), ("e11", "plan_risk", ex.analyze_e11)):
        if e in exps:
            res = [r for r in load_results(raw, pool, model_key) if r["instance_id"] in records]
            if res:
                s[e.upper()] = fn(pilot.score_plan_results(records, res), records)
    if "e12" in exps:
        res = [r for r in load_results(raw, "plan_shift", model_key) if r["instance_id"] in records]
        if res:
            s["E12"] = ex.analyze_e12(pilot.score_plan_results(records, res), rows, records)
    cap = [r for r in load_results(raw, "capability", model_key) if r["instance_id"] in records]
    if cap:
        s["E14"] = ex.analyze_e14(records, cap, rows)
    # mode validation and remaining metrics
    s["plan_sufficiency_by_mode"] = ex.plan_sufficiency_by_mode(rows)
    s["mode_decomposition"] = ex.mode_decomposition(rows)
    s["instruction_compliance"] = ex.instruction_compliance(rows)
    s["hierarchical"] = ex.hierarchical(rows, (s.get("E5") or {}).get("a_judgment"))
    conf = {(r["instance_id"], r["mode"]): (r["parsed"] or {}).get("confidence") for r in plan_res}
    s["calibration"] = ex.calibration_by_mode(rows, conf)
    s["regret_dc_vs_dxc"] = ex.mode_regret_test(rows)
    ids = {r["instance_id"] for r in rows}
    strata = {i: _stratum(records[i]) for i in ids}
    s["by_heuristic_stratum"] = ex.stratified(rows, strata)
    s["breakdown"] = ex.breakdown(rows, strata)
    s["by_template"] = ex.stratified(rows, {i: (records[i].get("notes") or {}).get("template", "v2") for i in ids})
    s["error_taxonomy"] = ex.taxonomy(rows)
    s["confirmatory"] = ex.confirmatory(s)
    s["ceiling_floor"] = pilot.ceiling_floor(s)
    return s
