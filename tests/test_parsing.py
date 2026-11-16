"""Rendering is faithful: the formal state can be recovered exactly from the prompt text."""

import itertools
import json
from pathlib import Path

import pytest

from msep.benchmark.parsing import parse_state
from msep.benchmark.schemas import instance_from_record
from msep.oracle import minimal_plan
from msep.world.constraints import evaluate, variables

from test_pilot_pipeline import make_records

POOL = Path(__file__).resolve().parents[1] / "data" / "generated" / "pool_v2" / "instances.jsonl"


def equivalent(state, parsed, alias):
    """Same variables, rules (by truth table), knowledge, actions, tasks, rule — up to renaming."""
    ren = {i: next(j for j, v in enumerate(parsed.variables) if v.name == alias[x.name])
           for i, x in enumerate(state.variables)}
    assert {v.kind for v in state.variables} == {v.kind for v in parsed.variables}
    assert {ren[i]: v for i, v in state.known.items()} == parsed.known
    assert sorted((a.cost, tuple(sorted(ren[v] for v in a.reveals)), a.resource) for a in state.actions) == \
        sorted((a.cost, tuple(sorted(a.reveals)), a.resource) for a in parsed.actions)
    assert {ren[i]: t for i, t in state.tasks.items()} == parsed.tasks
    assert state.decision_rule == parsed.decision_rule
    # rules: compare the conjunction of all rules over all assignments
    n = state.n
    for bits in itertools.product((False, True), repeat=n):
        a = dict(enumerate(bits))
        b = {ren[i]: bits[i] for i in range(n)}
        assert all(evaluate(r.formula, a) for r in state.rules) == all(evaluate(r.formula, b) for r in parsed.rules)


def test_roundtrip_small():
    for rec in make_records(2):
        st = instance_from_record(rec).state
        parsed = parse_state(rec["prompt_text"])
        equivalent(st, parsed, rec["rendering"]["var_alias"])
        a = minimal_plan.solve(st)
        b = minimal_plan.solve(parsed)
        assert a.resource_class == b.resource_class and a.analysis.optimal_cost == b.analysis.optimal_cost
        alias = rec["rendering"]["action_alias"]
        assert sorted(tuple(sorted(alias[x] for x in p)) for p in a.analysis.optimal_plans) == \
            sorted(b.analysis.optimal_plans)


@pytest.mark.skipif(not POOL.exists(), reason="pool_v2 not generated")
def test_roundtrip_pool_sample():
    recs = [json.loads(l) for l in open(POOL)]
    for rec in recs[::37]:  # deterministic sample across families and sibling types
        st = instance_from_record(rec).state
        parsed = parse_state(rec["prompt_text"])
        b = minimal_plan.solve(parsed)
        assert b.resource_class.value == rec["oracle"]["resource_class"]
        assert b.analysis.optimal_cost == rec["oracle"]["optimal_cost"]
