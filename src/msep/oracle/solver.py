"""SAT/MaxSAT plan oracle for the logical decision rule.

Static MSEP is a 2-level problem: find the cheapest action set such that no
distinguishing pair survives it. We solve it exactly by counterexample-guided
refinement:

1. A weighted MaxSAT solver (RC2) proposes the cheapest action set that
   satisfies all blocking clauses found so far (a minimum-cost hitting set;
   soft clauses "not a" with weight cost(a)).
2. The pair solver looks for a q-true / q-false pair that the proposed set
   cannot tell apart.
3. If one exists, the actions revealing any variable on which the pair
   differs form a new blocking clause: every sufficient plan must contain one
   of them. Go to 1.
4. If none exists, the proposal is an optimal sufficient plan.

Why MaxSAT here: once sufficiency is reduced to "hit every distinguishing
pair", minimum-cost plan selection is exactly weighted hitting set, which is
what weighted MaxSAT encodes. MaxSAT alone could not express sufficiency
(a for-all over outcomes); the refinement loop supplies that part.

To enumerate all inclusion-minimal sufficient plans, each found plan's
supersets are blocked and the loop continues. With positive costs, every plan
found this way is inclusion-minimal, and plans arrive in nondecreasing cost.
"""

from __future__ import annotations

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

from msep.world.state import FormalState, LogicalEntailment

from .logic import PairSolver
from .sufficiency import Plan, PlanAnalysis, canonical

DEFAULT_CAP = 512


def _check_rule(state: FormalState) -> None:
    if not isinstance(state.decision_rule, LogicalEntailment):
        raise ValueError("solver.py handles the logical-entailment rule; use probability.py")


def counterexample(state: FormalState, plan: Plan, pairs: PairSolver | None = None):
    _check_rule(state)
    own = pairs is None
    pairs = pairs or PairSolver(state)
    try:
        return pairs.find_pair(state.plan_reveals(plan))
    finally:
        if own:
            pairs.close()


def plan_sufficient(state: FormalState, plan: Plan) -> bool:
    return counterexample(state, plan) is None


def _min_hitting_set(m: int, costs: list[int], hard: list[list[int]]) -> tuple[list[int], int] | None:
    if any(len(c) == 0 for c in hard):
        return None
    w = WCNF()
    for c in hard:
        w.append(c)
    for j in range(m):
        w.append([-(j + 1)], weight=costs[j])
    with RC2(w) as rc2:
        model = rc2.compute()
        if model is None:
            return None
        chosen = [j for j in range(m) if (j + 1) in set(model)]
        return chosen, sum(costs[j] for j in chosen)


def analyze(state: FormalState, cap: int = DEFAULT_CAP) -> PlanAnalysis:
    _check_rule(state)
    actions = list(state.actions)
    m = len(actions)
    costs = [a.cost for a in actions]
    pairs = PairSolver(state)
    hard: list[list[int]] = []
    found: list[tuple[Plan, int]] = []
    refinements = 0
    truncated = False
    try:
        while True:
            proposal = _min_hitting_set(m, costs, hard)
            if proposal is None:
                break
            chosen, cost = proposal
            plan = canonical(actions[j].name for j in chosen)
            pair = pairs.find_pair(state.plan_reveals(plan))
            if pair is not None:
                diff = PairSolver.difference(pair)
                clause = [j + 1 for j, a in enumerate(actions) if diff & set(a.reveals)]
                hard.append(clause)
                refinements += 1
                if not clause:  # no available action can separate this pair
                    break
                continue
            found.append((plan, cost))
            if not chosen:  # the empty plan is sufficient
                break
            if len(found) >= cap:
                truncated = True
                break
            hard.append([-(j + 1) for j in chosen])  # block this plan and its supersets
    finally:
        pairs.close()
    if not found:
        return PlanAnalysis(False, None, [], [], extras={"refinements": refinements})
    best = found[0][1]
    return PlanAnalysis(
        already_sufficient=(found[0][0] == ()),
        optimal_cost=best,
        optimal_plans=sorted(p for p, c in found if c == best),
        minimal_plans=sorted(p for p, _ in found),
        minimal_truncated=truncated,
        extras={"refinements": refinements,
                # if the cap was hit while still at the optimal cost, more optimal plans may exist
                "optimal_truncated": truncated and found[-1][1] == best},
    )
