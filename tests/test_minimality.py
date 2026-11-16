import random

from msep.oracle.brute_force import BruteForce
from msep.oracle.sufficiency import plan_cost
from msep.world.generator import random_instance


def test_optimal_plans_are_sufficient_minimal_and_cheapest():
    for seed in range(300):
        st = random_instance(random.Random(10_000 + seed)).state
        bf = BruteForce(st)
        a = bf.analyze()
        sufficient = a.extras["sufficient_plans"]
        for p in a.optimal_plans:
            assert bf.plan_sufficient(p)
            for x in p:
                assert not bf.plan_sufficient(tuple(y for y in p if y != x))
            assert all(plan_cost(st, q) >= plan_cost(st, p) for q in sufficient)
        for p in a.minimal_plans:
            assert p in sufficient
            assert not any(set(q) < set(p) for q in sufficient)
