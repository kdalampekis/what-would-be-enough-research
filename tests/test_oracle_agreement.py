"""Brute force vs SAT/MaxSAT vs WMC vs obligation planner on random instances.

The full 10,000-instance run is experiments/e0_oracle_validation.py; this is a
fast subset for the test suite.
"""

import random

import pytest

from msep.controllers import obligation_planner
from msep.obligations.extraction import extract
from msep.oracle import probability, solver
from msep.oracle.brute_force import BruteForce
from msep.oracle.sufficiency import canonical
from msep.world.generator import random_instance
from msep.world.state import LogicalEntailment

SEEDS = range(600)


@pytest.mark.parametrize("seed", SEEDS)
def test_agreement(seed):
    inst = random_instance(random.Random(seed))
    st = inst.state
    bf = BruteForce(st)
    b = bf.analyze()
    if isinstance(st.decision_rule, LogicalEntailment):
        s = solver.analyze(st)
        assert s.key() == b.key()
        obs, truncated = extract(st)
        assert not truncated
        assert sorted(sorted(o.variables) for o in obs) == sorted(sorted(x) for x in bf.obligation_sets())
        out = obligation_planner.plan(st)
        if b.optimal_cost is None:
            assert out.plan is None
        else:
            assert (out.cost if out.plan else 0) == b.optimal_cost
            assert canonical(out.plan) in b.optimal_plans
        rng = random.Random(seed)
        names = [a.name for a in st.actions]
        for _ in range(5):
            plan = canonical(n for n in names if rng.random() < 0.5)
            assert solver.plan_sufficient(st, plan) == bf.plan_sufficient(plan)
    else:
        p = probability.analyze(st)
        assert p.key() == b.key()
        assert probability.posteriors(st) == {
            tuple(sorted((i, bool((g >> i) & 1)) for i in st.computed_vars() if i not in st.known)): v
            for g, v in bf.posteriors().items()}
