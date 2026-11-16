"""Runner + analysis pipeline with an oracle-backed test double (no API calls, no results/ writes)."""

import hashlib
import json
import random

from msep.benchmark.families import generate_family
from msep.benchmark.rendering import make_rendering, render_state
from msep.benchmark.schemas import instance_from_record, instance_record
from msep.eval import pilot
from msep.models.runner import load_results, run_jobs
from msep.oracle.sufficiency import is_sufficient


def make_records(n=4):
    recs = []
    for seed in range(n):
        fam = generate_family(seed)
        r = make_rendering(fam.siblings[0].instance.state, random.Random(seed))
        for j, s in enumerate(fam.siblings):
            text = render_state(s.instance.state, r)
            recs.append(instance_record(family_id=fam.family_id, instance_id=f"{fam.family_id}-{j}",
                                        sibling_type=s.sibling_type, split="dev", instance=s.instance,
                                        oracle=s.oracle, transformation=s.transformation,
                                        rendering={**r.to_json(), "action_alias": dict(r.action_alias)},
                                        prompt_text=text, notes=s.notes))
    return recs


def oracle_answer(rec, job):
    o = rec["oracle"]
    alias = rec["rendering"]["action_alias"]
    if job.pool == "decision":
        return {"decision": "true" if rec["true_target_value"] else "false", "confidence": 1, "short_justification": ""}
    if job.pool == "judgment":
        ok = is_sufficient(instance_from_record(rec).state, job.candidate)
        return {"plan_sufficient": ok, "confidence": 1, "short_justification": ""}
    plan = [] if o["resource_class"] == "NEITHER" or not o["optimal_plans"] else o["optimal_plans"][0]
    return {"state_sufficient": o["current_sufficient"], "resource_class": o["resource_class"],
            "plan": [{"type": "ASK" if a.startswith("ASK") else "COMPUTE", "action": alias[a]} for a in plan],
            "stop_after_plan": True,
            "decision": ("true" if rec["true_target_value"] else "false") if o["current_sufficient"] else "defer",
            "confidence": 1, "short_justification": ""}


def test_perfect_responder_scores_perfectly(tmp_path):
    recs = make_records()
    by_id = {r["instance_id"]: r for r in recs}
    jobs = pilot.build_jobs(recs)
    answers = {hashlib.sha256(j.prompt.encode()).hexdigest(): oracle_answer(by_id[j.instance_id], j) for j in jobs}
    cfg = {"provider": "fake", "model_id": "oracle-double", "settings": {"answers": answers}}
    counts = run_jobs(jobs, "oracle-double", cfg, tmp_path, max_calls=len(jobs), concurrency=2)
    assert counts["ok"] == len(jobs) and counts["parse_error"] == 0
    # resumable: a second run makes no calls
    assert run_jobs(jobs, "oracle-double", cfg, tmp_path, max_calls=0)["skipped_done"] == len(jobs)
    plan = load_results(tmp_path, "plan", "oracle-double")
    rows = pilot.score_plan_results(by_id, plan)
    e3 = pilot.analyze_e3(rows)
    assert e3["detection_controlled"]["accuracy"]["mean"] == 1.0
    assert e3["detection_controlled"]["macro_f1"]["value"] == 1.0
    e5 = pilot.analyze_e5(by_id, load_results(tmp_path, "judgment", "oracle-double"), rows)
    assert e5["a_judgment"]["all_insufficient_candidates_relevant"]
    assert e5["a_judgment"]["accuracy_relevant_insufficient_candidates"]["mean"] == 1.0
    e7 = pilot.analyze_e7(rows)
    for mode in ("detection_controlled", "diagnosis_controlled", "end_to_end"):
        for c in e7[mode]["per_class"].values():
            assert c["plan_sufficient"]["mean"] == 1.0
    e1 = pilot.analyze_e1(by_id, rows, load_results(tmp_path, "decision", "oracle-double"))
    assert e1["a_base_decision_accuracy"]["mean"] == 1.0
    md = pilot.markdown_report({"splits": ["dev"], "families": 4, "prompt_version": "t", "models": ["oracle-double"],
                                "by_model": {"oracle-double": {"response_status": {}, "E1": e1, "E3": e3, "E5": e5, "E7": e7}}})
    assert "E7 BOTH" in md
    rec = json.loads(next((tmp_path / "plan" / "oracle-double").glob("*.json")).read_text())
    assert rec["raw_response"] and rec["request"] and rec["prompt_sha256"]


def test_noisy_responder_is_penalised(tmp_path):
    recs = make_records(3)
    by_id = {r["instance_id"]: r for r in recs}
    jobs = [j for j in pilot.build_jobs(recs) if j.pool == "plan"]
    answers = {hashlib.sha256(j.prompt.encode()).hexdigest(): oracle_answer(by_id[j.instance_id], j) for j in jobs}
    cfg = {"provider": "fake", "model_id": "noisy", "settings": {"answers": answers, "error_rate": 1.0}}
    run_jobs(jobs, "noisy", cfg, tmp_path, max_calls=len(jobs))
    rows = pilot.score_plan_results(by_id, load_results(tmp_path, "plan", "noisy"))
    e7 = pilot.analyze_e7(rows)
    assert e7["detection_controlled"]["per_class"]["BOTH"]["plan_sufficient"]["mean"] == 0.0
    assert pilot.analyze_e3(rows)["detection_controlled"]["accuracy"]["mean"] == 1.0  # class untouched by the flip


def test_max_calls_is_enforced(tmp_path):
    import pytest
    recs = make_records(1)
    jobs = pilot.build_jobs(recs)
    with pytest.raises(RuntimeError, match="max-calls"):
        run_jobs(jobs, "x", {"provider": "fake", "model_id": "x", "settings": {"answers": {}}}, tmp_path, max_calls=1)
