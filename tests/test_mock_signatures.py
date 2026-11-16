"""Every metric moves the way it should for a known (SYNTHETIC) behaviour.

If a metric definition changes and a signature breaks, this fails.
"""

import hashlib

import pytest

from msep.agents.mock import AGENTS
from msep.benchmark import variants
from msep.eval import experiments as ex
from msep.eval import pilot
from msep.eval.summary import analyze_model
from msep.models.runner import run_jobs

from test_pilot_pipeline import make_records


@pytest.fixture(scope="module")
def summaries(tmp_path_factory):
    raw = tmp_path_factory.mktemp("raw")
    recs = make_records(3)
    var = {"cost": [v for r in recs for v in variants.cost_sweep(r)],
           "shift": [v for r in recs for f in (variants.shift_width, variants.shift_depth) for v in [f(r)] if v]}
    all_recs = recs + var["cost"] + var["shift"]
    by_id = {r["instance_id"]: r for r in all_recs}
    jobs = (pilot.build_jobs(recs) + ex.build_variant_jobs(var["cost"], "cost") + ex.build_variant_jobs(var["shift"], "shift")
            + ex.build_capability_jobs(recs))
    lookup = {hashlib.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in jobs}
    out = {}
    for agent in AGENTS:
        cfg = {"provider": "mock", "model_id": agent, "settings": {"agent": agent, "lookup": lookup, "max_tokens": 1000}}
        run_jobs(jobs, agent, cfg, raw, max_calls=len(jobs), concurrency=1, log=lambda *_: None)
        out[agent] = analyze_model(raw, agent, by_id)
    return out


def m(ci):
    return ci["mean"] if isinstance(ci, dict) else ci


def test_oracle_perfect_is_perfect_everywhere(summaries):
    s = summaries["oracle_perfect"]
    assert m(s["E1"]["a_base_decision_accuracy"]) == 1
    assert m(s["E2"]["detection_accuracy"]) == 1 and m(s["E2"]["over_answering"]) == 0
    for mode in ("detection_controlled", "end_to_end"):
        assert m(s["E3"][mode]["accuracy"]) == 1 and m(s["E3"][mode]["h2_plan_sufficient"]) == 1
    assert m(s["E4"]["diagnosis_controlled"]["exact_match"]) == 1
    assert m(s["E5"]["a_judgment"]["pair_both_correct"]) == 1
    assert m(s["E6"]["detection_controlled"]["optimal_given_sufficient"]) == 1
    assert m(s["E8"]["detection_controlled"]["correct_defer"]) == 1
    assert m(s["E9"]["detection_controlled"]["premature_stop"]) == 0
    assert m(s["E10"]["detection_controlled"]["optimal_rate"]) == 1
    rel = s["E10"]["detection_controlled"]["chose_swept_action_by_cost_relation"]
    assert rel["below"] == 1 and rel["above"] == 0
    for axis in ("width", "depth"):
        assert m(s["E12"]["detection_controlled"][axis]["paired_drop_plan_sufficient"]) == 0
    assert all(v == 1.0 for v in s["confirmatory"]["raw_p"].values())


def test_always_answer_fails_detection_and_answers_everything(summaries):
    s = summaries["always_answer"]
    assert m(s["E2"]["insufficiency_detected (sensitivity)"]) == 0
    assert m(s["E2"]["over_answering"]) == 1
    assert m(s["E8"]["detection_controlled"]["premature_answer"]) == 1
    assert m(s["E9"]["detection_controlled"]["premature_stop"]) == 1


def test_always_abstain_is_abstention_not_premature_stop(summaries):
    s = summaries["always_abstain"]
    assert m(s["E8"]["detection_controlled"]["correct_defer"]) == 1
    assert m(s["E9"]["detection_controlled"]["premature_stop"]) == 0
    assert m(s["E9"]["detection_controlled"]["abstained"]) == 1


def test_relevant_insufficient_shows_relevance_not_sufficiency(summaries):
    s = summaries["relevant_insufficient"]
    dc = s["E3"]["detection_controlled"]
    assert m(dc["h2_class_correct"]) > m(dc["h2_plan_sufficient"]) + 0.3
    assert m(s["E5"]["a_judgment"]["relevant_insufficient_judged_sufficient"]) == 1
    assert m(s["E5"]["b_construction"]["detection_controlled"]["RELEVANT_INSUFFICIENT_INFORMATION"]["decoy_only_plan"]) == 1
    assert m(s["E7"]["detection_controlled"]["per_class"]["BOTH"]["plan_sufficient"]) == 0


def test_expensive_sufficient_is_sufficient_but_not_minimal(summaries):
    s = summaries["expensive_sufficient"]
    dc = s["E6"]["detection_controlled"]
    assert m(dc["plan_sufficient"]) == 1
    assert m(dc["optimal_given_sufficient"]) < 0.5 and m(dc["excess_cost_given_sufficient"]) > 0
    assert m(s["E8"]["detection_controlled"]["inappropriate_persistence"]) == 1


def test_premature_stop_stops_early(summaries):
    s = summaries["premature_stop"]
    assert m(s["E9"]["detection_controlled"]["premature_stop"]) > 0
    assert m(s["E9"]["detection_controlled"]["PREMATURE_STOP"]["premature_stop"]) == 1
    assert m(s["E7"]["detection_controlled"]["per_class"]["BOTH"]["plan_sufficient"]) == 0


def test_always_ask_and_compute_cover_only_their_resource(summaries):
    ask = summaries["always_ask"]["E7"]["detection_controlled"]["per_class"]
    comp = summaries["always_compute"]["E7"]["detection_controlled"]["per_class"]
    assert m(ask["INFORMATION_ONLY"]["plan_sufficient"]) == 1 and m(ask["COMPUTATION_ONLY"]["plan_sufficient"]) == 0
    assert m(comp["COMPUTATION_ONLY"]["plan_sufficient"]) == 1 and m(comp["INFORMATION_ONLY"]["plan_sufficient"]) == 0
    assert m(ask["BOTH"]["plan_sufficient"]) == 0 and m(comp["BOTH"]["plan_sufficient"]) == 0


def test_mock_results_are_marked_synthetic(summaries):
    assert all(s["synthetic"] for s in summaries.values())


def test_mode_decomposition_attributes_failures(summaries):
    db = summaries["detection_blind"]["mode_decomposition"]
    assert m(db["e2e_fail_detection_wrong"]) == 1 and m(db["e2e_fail_but_dc_success"]) == 1
    assert m(db["fail_in_all_modes (planning)"]) == 0
    nd = summaries["needs_diagnosis"]["mode_decomposition"]
    assert m(nd["dc_fail_but_dxc_success (diagnosis-attributable)"]) > 0.3
    assert m(nd["fail_in_all_modes (planning)"]) == 0
    ri = summaries["relevant_insufficient"]["mode_decomposition"]
    assert m(ri["fail_in_all_modes (planning)"]) > 0.3


def test_instruction_compliance_and_hierarchy(summaries):
    nc = summaries["noncompliant"]["instruction_compliance"]
    assert m(nc["dc_claims_state_sufficient"]) == 1
    ok = summaries["oracle_perfect"]
    assert m(ok["instruction_compliance"]["dc_claims_state_sufficient"]) == 0
    assert all(m(v) == 1 for k, v in ok["hierarchical"].items() if v is not None)


def test_strata_and_calibration_present(summaries):
    s = summaries["oracle_perfect"]
    assert set(s["by_heuristic_stratum"]) <= {"heuristic_easy", "heuristic_hard"}
    assert s["calibration"]["detection_controlled"]["n"] > 0


def test_e14_capability_control(summaries):
    o = summaries["oracle_perfect"]["E14"]
    assert m(o["capability_overall"]) == 1
    assert m(o["detection_controlled"]["skip_rate_when_capable"]) == 0
    a = summaries["always_answer"]["E14"]
    assert m(a["end_to_end"]["skip_rate_when_capable"]) in (1, None) or m(a["end_to_end"]["skip_rate_when_not_capable"]) == 1
