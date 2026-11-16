from msep.benchmark.families import generate_family
from msep.controllers import obligation_planner
from msep.oracle.sufficiency import ResourceClass


def test_planner_on_families():
    for seed in range(10):
        for s in generate_family(seed).siblings:
            res = s.oracle
            out = obligation_planner.plan(s.instance.state)
            trace = obligation_planner.run(s.instance)
            if res.resource_class is ResourceClass.NEITHER:
                assert out.plan is None and trace.outcome == "deferred"
                continue
            assert (out.cost or 0) == res.analysis.optimal_cost
            assert trace.outcome == "answered"
            assert trace.decision == s.instance.full_assignment()[s.instance.state.target]
            # re-planning after each observation never costs more than the static optimum
            assert trace.total_cost <= res.analysis.optimal_cost
