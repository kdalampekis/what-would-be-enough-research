"""Every equally optimal plan is accepted by every metric (not only a canonical one)."""

import random

from msep.benchmark.rendering import make_rendering, render_state
from msep.benchmark.schemas import instance_from_record, instance_record
from msep.benchmark.template_v3 import generate_family_v3
from msep.eval.error_taxonomy import classify
from msep.eval.experiments import action_overlap
from msep.eval.plan_metrics import score
from msep.models.schemas import ModelResponse
from msep.oracle.sufficiency import is_sufficient


def tie_records(limit=6):
    out = []
    for seed in range(200):
        f = generate_family_v3(seed)
        r = make_rendering(f.siblings[0].instance.state, random.Random(seed), shuffle_rules=True)
        for k, s in enumerate(f.siblings):
            if len(s.oracle.analysis.optimal_plans) > 1:
                text = render_state(s.instance.state, r)  # sets the action aliases for this sibling
                out.append(instance_record(family_id=f.family_id, instance_id=f"{f.family_id}-{k}",
                                           sibling_type=s.sibling_type, split="dev", instance=s.instance,
                                           oracle=s.oracle, transformation="t",
                                           rendering={**r.to_json(), "action_alias": dict(r.action_alias)},
                                           prompt_text=text, notes=s.notes))
        if len(out) >= limit:
            return out
    return out


TIES = tie_records()


def test_ties_exist_in_v3():
    assert len(TIES) >= 3


def test_every_optimal_plan_scores_as_optimal_everywhere():
    for rec in TIES:
        alias = rec["rendering"]["action_alias"]
        st = instance_from_record(rec).state
        for plan in rec["oracle"]["optimal_plans"]:
            resp = ModelResponse(False, rec["oracle"]["resource_class"], [alias[a] for a in plan], [], True, "defer", 0.5, "")
            s = score(rec, resp)
            assert s["plan_sufficient"] and s["plan_optimal"] and s["plan_exact_match"] and s["plan_minimal"]
            assert s["regret"] == 0 and s["excess_cost"] == 0
            assert classify(rec, resp, s) == "correct"
            assert action_overlap(set(plan), rec["oracle"]["optimal_plans"]) == (1.0, 1.0)
            assert is_sufficient(st, tuple(plan))  # E5 judgment labels are recomputed exactly
