"""Several optimal plans: any of them, and any sufficient plan at optimal cost, scores as optimal."""

from msep.actions.information import InformationAction
from msep.benchmark.schemas import instance_record
from msep.eval.plan_metrics import score
from msep.models.schemas import ModelResponse
from msep.oracle import minimal_plan
from msep.world.constraints import Iff, lit
from msep.world.state import FormalState, Instance, LatentWorld, Rule, Variable, VarKind


def tie_record():
    v = (Variable("q", VarKind.WORLD), Variable("A", VarKind.WORLD), Variable("B", VarKind.WORLD))
    st = FormalState(variables=v, rules=(Rule("R1", Iff(lit(0), lit(1))), Rule("R2", Iff(lit(2), lit(1)))), target=0,
                     info_actions=(InformationAction("ASK_A", (1,), 2), InformationAction("ASK_B", (2,), 2),
                                   InformationAction("ASK_AB", (1, 2), 5)))
    inst = Instance(st, LatentWorld(((0, True), (1, True), (2, True))))
    res = minimal_plan.solve(st)
    return instance_record(family_id="T", instance_id="T1", sibling_type="TIE", split="dev", instance=inst,
                           oracle=res, transformation="tie")


def resp(plan):
    return ModelResponse(False, "INFORMATION_ONLY", plan, [], True, "defer", 0.5, "")


def test_both_optimal_plans_score_as_optimal():
    rec = tie_record()
    assert sorted(rec["oracle"]["optimal_plans"]) == [["ASK_A"], ["ASK_B"]]
    for p in (["ASK_A"], ["ASK_B"]):
        s = score(rec, resp(p))
        assert s["plan_sufficient"] and s["plan_optimal"] and s["plan_exact_match"] and s["regret"] == 0


def test_sufficient_nonminimal_plan_is_not_optimal():
    rec = tie_record()
    s = score(rec, resp(["ASK_AB"]))
    assert s["plan_sufficient"] and not s["plan_optimal"] and s["excess_cost"] == 3
    s = score(rec, resp(["ASK_A", "ASK_B"]))
    assert s["plan_sufficient"] and not s["plan_minimal"] and s["excess_cost"] == 2


def test_optimal_by_cost_even_if_not_listed():
    rec = tie_record()
    rec["oracle"]["optimal_plans"] = [["ASK_A"]]  # simulate a truncated list
    s = score(rec, resp(["ASK_B"]))
    assert s["plan_optimal"] and not s["plan_exact_match"]
