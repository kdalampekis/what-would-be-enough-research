"""ORACLE obligation planner (A). Part of the oracle, NOT the mitigation.

It receives the exact formal state and the instance, so it cannot be evidence
that anything helps an agent. It serves as a third exact path in E0. The
candidate mitigation, which sees only agent-visible information, is
controllers/realistic_planner.py (B).

Formal core shared with (B):

Pipeline (PROBLEM_SPEC section 14):

    formal state -> unresolved obligations -> actions that discharge each
    -> minimum-cost set discharging all (weighted hitting set, RC2)
    -> execute one action -> re-evaluate -> stop when sufficient, or defer

In Phase 1 the formal state is given exactly. In Phase 2 an LLM or parser
builds it from text, and the planner is compared with native LLM planning,
confidence thresholds, ask-vs-think heuristics and learned routers.

Static planning (`plan`) is exact and must equal the oracle's optimal cost;
the validation suite checks this. `run` re-plans after every observation, so
it stops as soon as the actual outcomes make the decision justified.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

from msep.obligations.discharge import discharges
from msep.obligations.extraction import extract
from msep.oracle.sufficiency import canonical, is_sufficient
from msep.world.state import FormalState, Instance, LogicalEntailment


@dataclass
class PlannerOutput:
    sufficient_now: bool
    plan: tuple[str, ...] | None       # None: no available plan (defer)
    cost: int | None
    obligations: list[dict]
    unresolvable: list[str]


def plan(state: FormalState) -> PlannerOutput:
    if not isinstance(state.decision_rule, LogicalEntailment):
        raise ValueError("the obligation planner is defined for the logical-entailment rule")
    obligations, truncated = extract(state)
    if truncated:
        raise RuntimeError("too many obligations to plan exactly")
    obs_json = [o.to_json(state) for o in obligations]
    if not obligations:
        return PlannerOutput(True, (), 0, obs_json, [])
    actions = list(state.actions)
    hard = []
    unresolvable = []
    for o in obligations:
        clause = [j + 1 for j, a in enumerate(actions) if discharges(state, a, o)]
        if not clause:
            unresolvable.append(o.id)
        hard.append(clause)
    if unresolvable:
        return PlannerOutput(False, None, None, obs_json, unresolvable)
    w = WCNF()
    for c in hard:
        w.append(c)
    for j, a in enumerate(actions):
        w.append([-(j + 1)], weight=a.cost)
    with RC2(w) as rc2:
        model = rc2.compute()
    chosen = canonical(actions[j].name for j in range(len(actions)) if (j + 1) in set(model))
    return PlannerOutput(False, chosen, sum(state.action_index[a].cost for a in chosen), obs_json, [])


@dataclass
class RunTrace:
    steps: list[dict] = field(default_factory=list)
    outcome: str = ""          # "answered" | "deferred"
    decision: bool | None = None
    total_cost: int = 0


def run(instance: Instance, max_steps: int = 50) -> RunTrace:
    """Execute with re-planning after each observation. Uses only the formal state
    and the actions' real outcomes; the latent world is read only by information
    actions when they execute."""
    state = instance.state
    trace = RunTrace()
    for _ in range(max_steps):
        out = plan(state)
        if out.sufficient_now:
            from msep.oracle.logic import status
            from msep.oracle.sufficiency import Status
            trace.outcome = "answered"
            trace.decision = status(state) is Status.ENTAILED
            return trace
        if out.plan is None:
            trace.outcome = "deferred"
            return trace
        # next action: the one discharging the most obligations; ties by cost, then name
        obligations, _ = extract(state)

        def score(name: str):
            a = state.action_index[name]
            return (-sum(discharges(state, a, o) for o in obligations), a.cost, name)

        nxt = min(out.plan, key=score)
        learned = Instance(state, instance.world).execute(nxt)
        cost = state.action_index[nxt].cost
        trace.steps.append({"action": nxt, "cost": cost, "learned": {state.variables[i].name: v for i, v in learned.items()},
                            "planned": list(out.plan)})
        trace.total_cost += cost
        state = state.with_knowledge(learned)
    raise RuntimeError("planner did not terminate")


def check_static(state: FormalState) -> bool:
    """The planner's plan is sufficient (oracle check)."""
    out = plan(state)
    return out.plan is None or is_sufficient(state, out.plan)
