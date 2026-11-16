from msep.benchmark.families import generate_family
from msep.benchmark.schemas import instance_record
from msep.eval.error_taxonomy import classify
from msep.eval.plan_metrics import score
from msep.models.prompts import Mode, build_prompt, eligible
from msep.models.schemas import ModelResponse, parse_response

FAM = generate_family(7)
RECS = {s.sibling_type: instance_record(family_id=FAM.family_id, instance_id=s.sibling_type,
                                        sibling_type=s.sibling_type, split="test", instance=s.instance,
                                        oracle=s.oracle, transformation=s.transformation, notes=s.notes)
        for s in FAM.siblings}


def oracle_response(rec, plan=None, decision=None):
    o = rec["oracle"]
    plan = list(o["optimal_plans"][0]) if plan is None and o["optimal_plans"] else (plan or [])
    if decision is None:
        decision = ("true" if rec["true_target_value"] else "false") if o["current_sufficient"] else "defer"
    return ModelResponse(o["current_sufficient"], o["resource_class"], plan, [], True, decision, 0.9, "")


def test_oracle_answer_scores_perfectly():
    for t, rec in RECS.items():
        r = oracle_response(rec)
        s = score(rec, r)
        assert s["regret"] == 0, t
        assert classify(rec, r, s) == "correct", t
        if rec["oracle"]["resource_class"] not in ("NEITHER",):
            assert s["plan_sufficient"] and s["plan_optimal"]


def test_decoy_plan_is_a_sufficiency_failure():
    rec = RECS["RELEVANT_INSUFFICIENT_INFORMATION"]
    r = oracle_response(rec, plan=[rec["notes"]["decoy"]])
    s = score(rec, r)
    assert not s["plan_sufficient"] and s["regret"] > 0
    assert classify(rec, r, s) == "sufficiency"


def test_bulk_plan_is_a_minimality_failure():
    rec = RECS["SUFFICIENT_NON_MINIMAL"]
    comp = [a["name"] for a in rec["oracle"]["actions"] if a["resource"] == "computation" and a["category"] == "optimal"]
    r = oracle_response(rec, plan=["ASK_REPORT", *comp])
    s = score(rec, r)
    assert s["plan_sufficient"] and not s["plan_optimal"] and s["excess_cost"] > 0
    assert classify(rec, r, s) == "minimality"


def test_answering_neither_is_penalised():
    rec = RECS["NEITHER"]
    s = score(rec, oracle_response(rec, plan=[], decision="true"))
    assert s["answered_prematurely"] and s["regret"] > 0


def test_prompt_modes_and_parser():
    assert not eligible(Mode.DETECTION_CONTROLLED, "ALREADY_SUFFICIENT")
    assert not eligible(Mode.DIAGNOSIS_CONTROLLED, "NEITHER")
    p = build_prompt("STATE", Mode.DIAGNOSIS_CONTROLLED, "BOTH")
    assert "not yet sufficient" in p and "both additional information and additional computation" in p
    assert "not yet sufficient" not in build_prompt("STATE", Mode.END_TO_END, "BOTH")
    r = parse_response('ok {"state_sufficient": false, "resource_class": "BOTH", "plan": '
                       '[{"type": "ASK", "action": "ASK_F1"}], "stop_after_plan": true, "decision": "defer", '
                       '"confidence": 0.5, "short_justification": "x"}')
    assert r.plan == ["ASK_F1"] and r.resource_class == "BOTH"
