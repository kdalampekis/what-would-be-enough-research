"""Mitigation driver (experiments/run_eop.py): no oracle leakage, failure accounting, S1 prompt. No network."""

import json
import sys
from pathlib import Path

from msep.benchmark import t1_flips
from msep.models.prompts import Mode, build_prompt
from msep.models.prompts_s1 import s1_prompt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import run_eop  # noqa: E402
from test_pilot_pipeline import make_records  # noqa: E402
from test_realistic_planner import _extraction_json  # noqa: E402


def _t1():
    return [m for r in make_records(4) for m in t1_flips.make_pair(r)]


def _visible_only(r):
    """Everything hidden removed: oracle labels, latent world, true values, state, t1 labels."""
    return {"instance_id": r["instance_id"], "family_id": r["family_id"], "prompt_text": r["prompt_text"]}


def test_planning_uses_only_the_prompt_text():
    t1 = _t1()
    ex = {r["instance_id"]: {"parsed": _extraction_json(r["prompt_text"]), "status": "ok"} for r in t1}
    full, _ = run_eop.planned_results(t1, ex)
    stripped, _ = run_eop.planned_results([_visible_only(r) for r in t1], ex)
    assert [x["parsed"] for x in full] == [x["parsed"] for x in stripped]


def test_perfect_extraction_plans_optimally():
    t1 = _t1()
    ex = {r["instance_id"]: {"parsed": _extraction_json(r["prompt_text"]), "status": "ok"} for r in t1}
    res, stats = run_eop.planned_results(t1, ex)
    by_id = {r["instance_id"]: r for r in t1}
    m = run_eop.summarize(run_eop.score(by_id, res, list(by_id)))
    assert m["optimal_all"]["mean"] == 1 and m["unparsed_resolvable"] == 0 and not any(k.startswith("planner_error") for k in stats)
    assert m["stop_ok_AS_NEITHER"]["mean"] in (1, None)


def test_failed_or_missing_extractions_are_failures_not_skipped():
    t1 = _t1()
    ex = {t1[0]["instance_id"]: {"parsed": None, "status": "truncated"}}
    res, stats = run_eop.planned_results(t1, ex)
    assert stats["extraction_failed"] == 1 and stats["extraction_missing"] == len(t1) - 1
    assert all(x["parsed"] is None for x in res)
    by_id = {r["instance_id"]: r for r in t1}
    assert run_eop.summarize(run_eop.score(by_id, res, list(by_id)))["optimal_all"]["mean"] == 0


def test_inconsistent_extraction_is_a_pipeline_failure():
    t1 = _t1()[:2]
    bad = _extraction_json(t1[0]["prompt_text"])
    bad["known"] = [{"handle": bad["variables"][0]["handle"], "value": True},
                    {"handle": bad["variables"][0]["handle"], "value": False}]
    res, stats = run_eop.planned_results(t1[:1], {t1[0]["instance_id"]: {"parsed": bad, "status": "ok"}})
    assert res[0]["parsed"] is None and any(k.startswith("planner_error") for k in stats)


def test_s1_prompt_extends_the_native_prompt_and_keeps_the_output_format():
    r = _t1()[0]
    base = build_prompt(r["prompt_text"], Mode.END_TO_END, r["oracle"]["resource_class"])
    p = s1_prompt(base)
    assert p.startswith(base) and "obligation" in p and "JSON object must come last" in p
    jobs = run_eop.jobs_for([r], "t1pilot", "s1") + run_eop.jobs_for([r], "t1pilot", "s3")
    assert [j.pool for j in jobs] == ["plan_t1s1", "extract_t1"]
    v3 = run_eop.jobs_for([r], "v3dev", "s1")
    assert {j.pool for j in v3} == {"plan_s1"} and {j.mode for j in v3} <= {"end_to_end", "detection_controlled"}
    assert "Do not solve it" in jobs[1].prompt and json.dumps(r["oracle"]) not in jobs[1].prompt


def _b_answer(r, plan_names):
    from msep.models.runner import _parse
    resp = {"state_sufficient": False, "resource_class": "BOTH", "decision": "defer", "stop_after_plan": True,
            "confidence": 0.5, "short_justification": "x",
            "plan": [{"type": "ASK" if n.startswith("ASK") else "COMPUTE", "action": n} for n in plan_names]}
    parsed, err = _parse("plan", json.dumps(resp))
    assert err is None
    return {"instance_id": r["instance_id"], "family_id": r["family_id"], "mode": "end_to_end", "parsed": parsed}


def test_d_prunes_unneeded_actions_never_adds_and_stops_when_decided():
    t1 = _t1()
    ex = {r["instance_id"]: {"parsed": _extraction_json(r["prompt_text"]), "status": "ok"} for r in t1}
    by_id = {r["instance_id"]: r for r in t1}
    checked = 0
    for r in t1:
        names = sorted(a["name"] for a in r["state"]["info_actions"] + r["state"]["comp_actions"])
        alias = (r.get("rendering") or {}).get("action_alias") or {}
        shown = [alias.get(n, n) for n in names]
        out, _ = run_eop.verified_results([_b_answer(r, shown)], ex)  # B proposes every action
        d = out[0]["parsed"]
        assert d is not None and set(d["plan"]) <= set(shown)  # nothing added
        rc = r["oracle"]["resource_class"]
        if rc == "ALREADY_SUFFICIENT":
            assert d["plan"] == [] and d["state_sufficient"] is True
        if rc in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH") and len(d["plan"]) < len(shown):
            checked += 1
        row = run_eop.score(by_id, out, [r["instance_id"]])[r["instance_id"]]
        if rc in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH"):
            assert row["plan_sufficient"]  # pruning keeps every action that discharges an obligation
    assert checked > 0  # some unneeded actions were actually removed


def test_amendment1_extraction_v2_shows_the_layout_and_keeps_v1_unchanged():
    from msep.controllers.llm_extractor import INSTRUCTIONS, extraction_prompt, extraction_prompt_v2
    r = _t1()[0]
    v1, v2 = extraction_prompt(r["prompt_text"]), extraction_prompt_v2(r["prompt_text"])
    assert v1 == r["prompt_text"] + "\n\n" + INSTRUCTIONS  # registered condition C unchanged
    assert v2.startswith(v1) and '"handle": "F1"' in v2 and '"reveals": ["F1"]' in v2
    jobs = run_eop.jobs_for([r], "t1pilot", "s3v2") + run_eop.jobs_for([r], "v3dev", "s3v2")
    assert [j.pool for j in jobs] == ["extract_t1v2", "extract_v2"]
    # a perfect extraction in the v2 layout still plans optimally
    ex = {x["instance_id"]: {"parsed": _extraction_json(x["prompt_text"]), "status": "ok"} for x in _t1()}
    res, _ = run_eop.planned_results(_t1(), ex)
    assert all(x["parsed"] is not None for x in res)


def test_amendment2_message_text_parse_only_fills_missing_function_calls():
    msg = ('Reasoning first. {"state_sufficient": false, "resource_class": "INFORMATION_ONLY", "plan": '
           '[{"type": "ASK", "action": "ASK_F1"}], "stop_after_plan": true, "decision": "defer", "confidence": 0.5, '
           '"short_justification": "x"}')
    rec = {"instance_id": "i", "family_id": "f", "mode": "end_to_end", "status": "ok", "parsed": None,
           "parse_error": "no text", "raw_response": {"output": [{"type": "message", "content": [{"type": "output_text", "text": msg}]}]}}
    ok = {**rec, "parsed": {"plan": ["ASK_F2"]}, "parse_error": None}
    out = run_eop.message_text_results([rec, ok])
    assert out[0]["parsed"]["plan"] == ["ASK_F1"] and out[1] is ok
