import json
import re
from pathlib import Path

from msep.benchmark import external, variants
from msep.benchmark.schemas import instance_from_record
from msep.oracle import minimal_plan
from msep.oracle.brute_force import BruteForce

from test_pilot_pipeline import make_records

RECS = make_records(4)


def by_type(t):
    return [r for r in RECS if r["sibling_type"] == t]


def test_cost_sweep_switches_at_the_boundary():
    for r in by_type("MULTIPLE_PLANS_DIFFERENT_COSTS"):
        for v in variants.cost_sweep(r):
            plans = v["oracle"]["optimal_plans"]
            rel = v["variant"]["relation"]
            if rel == "below":
                assert plans == [["ASK_wa"]]
            elif rel == "above":
                assert plans == [["ASK_w1"]]
            else:
                assert sorted(plans) == [["ASK_w1"], ["ASK_wa"]]
            assert v["oracle"]["resource_class"] == "INFORMATION_ONLY"
            assert v["family_id"] == r["family_id"] and v["split"] == r["split"]


def test_cost_sweep_bulk_becomes_optimal_when_cheap():
    for r in by_type("SUFFICIENT_NON_MINIMAL"):
        cheap = [v for v in variants.cost_sweep(r) if v["variant"]["relation"] == "below"]
        assert any("ASK_REPORT" in p for v in cheap for p in v["oracle"]["optimal_plans"])


def test_shift_preserves_class_and_grows_plans():
    for r in RECS:
        for fn in (variants.shift_width, variants.shift_depth):
            v = fn(r)
            if v is None:
                continue
            assert v["oracle"]["resource_class"] == r["oracle"]["resource_class"], (r["sibling_type"], fn.__name__)
            if r["oracle"]["optimal_cost"] and r["oracle"]["resource_class"] != "ALREADY_SUFFICIENT":
                assert v["oracle"]["optimal_cost"] >= r["oracle"]["optimal_cost"]
            st = instance_from_record(v).state
            assert BruteForce(st).analyze().key() == minimal_plan.solve(st).analysis.key()


def test_skin_shift_changes_only_wording():
    for r in RECS[:11]:
        v = variants.shift_skin(r)
        assert v["oracle"] == r["oracle"]
        assert v["rendering"]["skin"] == "harbour" and r["rendering"]["skin"] != "harbour"


def test_risk_variants_render_priors_and_tau1_matches_logic():
    for r in by_type("BOTH") + by_type("INFORMATION_ONLY"):
        vs = variants.risk_variants(r, seed=0)
        assert all("Prior probabilities" in v["prompt_text"] for v in vs)
        tau1 = next(v for v in vs if v["variant"]["tau"] == "1")
        assert tau1["oracle"]["resource_class"] == r["oracle"]["resource_class"]
        assert tau1["oracle"]["optimal_cost"] == r["oracle"]["optimal_cost"]


def test_external_converter():
    rows = external.load(Path(__file__).parent / "fixtures" / "external_sample.jsonl")
    ok = {p["id"]: (inst, err) for p, inst, err in rows}
    inst, _ = ok["ext-1"]
    res = minimal_plan.solve(inst.state)
    assert res.resource_class.value == "INFORMATION_ONLY" and res.analysis.optimal_plans == [("ASK_cones_out",)]
    inst2, _ = ok["ext-2"]
    assert minimal_plan.solve(inst2.state).resource_class.value == "NEITHER"  # d is unconstrained
    assert ok["ext-bad"][0] is None and "violates" in ok["ext-bad"][1]


def test_generic_cost_sweep_on_v3_switches_at_boundary():
    import random as _r
    from msep.benchmark.rendering import make_rendering, render_state
    from msep.benchmark.schemas import instance_record
    from msep.benchmark.template_v3 import generate_family_v3
    checked = 0
    for seed in range(12):
        f = generate_family_v3(seed)
        r = make_rendering(f.siblings[0].instance.state, _r.Random(seed), shuffle_rules=True)
        for k, s in enumerate(f.siblings):
            rec = instance_record(family_id=f.family_id, instance_id=f"{f.family_id}-{k}", sibling_type=s.sibling_type,
                                  split="dev", instance=s.instance, oracle=s.oracle, transformation="t",
                                  rendering={**r.to_json(), "action_alias": dict(r.action_alias)},
                                  prompt_text=render_state(s.instance.state, r), notes=s.notes)
            for v in variants.cost_sweep(rec):
                d = v["variant"]["action"]
                in_opt = any(d in p for p in v["oracle"]["optimal_plans"])
                rel = v["variant"]["relation"]
                assert in_opt == (rel in ("below", "equal")), (rel, v["oracle"]["optimal_plans"])
                checked += 1
    assert checked > 10
