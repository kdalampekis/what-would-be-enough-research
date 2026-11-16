"""Oracle front end: everything the benchmark records about one formal state.

Uses the SAT/MaxSAT path for the logical rule and the WMC path for the
posterior rule. The brute-force oracle is used only for validation.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

from msep.obligations.discharge import action_discharges, discharge_map, discharges, unresolvable
from msep.obligations.extraction import extract
from msep.obligations.model import Obligation
from msep.world.state import FormalState, LogicalEntailment

from . import logic, probability, solver
from .sufficiency import PlanAnalysis, ResourceClass, Status, composition, plan_cost


@dataclass
class ActionRole:
    name: str
    resource: str
    cost: int
    reveals: list[str]
    already_known: bool
    alone_sufficient: bool
    relevant: bool
    in_optimal_plan: bool
    in_minimal_plan: bool | None
    necessary: bool | None
    category: str  # optimal | dominated | relevant_insufficient | irrelevant

    def to_json(self) -> dict:
        return dict(self.__dict__)


@dataclass
class OracleResult:
    decision_rule: dict
    status: Status
    posteriors: list | None
    analysis: PlanAnalysis
    resource_class: ResourceClass
    necessity: dict
    actions: list[ActionRole]
    obligations: list[Obligation] | None
    obligations_truncated: bool
    discharge: dict | None
    unresolvable_obligations: list[str] | None
    why_necessary: dict | None

    def to_json(self, state: FormalState) -> dict:
        a = self.analysis
        return {
            "decision_rule": self.decision_rule,
            "current_status": self.status.value,
            "posteriors": self.posteriors,
            "current_sufficient": a.already_sufficient,
            "resource_class": self.resource_class.value,
            "optimal_cost": a.optimal_cost,
            "optimal_plans": [list(p) for p in a.optimal_plans],
            "optimal_plan_compositions": [composition(state, p).value for p in a.optimal_plans],
            "minimal_sufficient_plans": [
                {"plan": list(p), "cost": plan_cost(state, p), "composition": composition(state, p).value}
                for p in a.minimal_plans],
            "minimal_plans_truncated": a.minimal_truncated,
            "necessity": self.necessity,
            "actions": [r.to_json() for r in self.actions],
            "obligations": None if self.obligations is None else [o.to_json(state) for o in self.obligations],
            "obligations_truncated": self.obligations_truncated,
            "obligation_discharge": self.discharge,
            "unresolvable_obligations": self.unresolvable_obligations,
            "why_necessary": self.why_necessary,
        }


def _relevance_sat(state: FormalState, obligation_vars: set[int]) -> dict[str, bool]:
    single = logic.SingleSolver(state)
    try:
        targets = [v for v in (*sorted(obligation_vars), state.target) if not single.determined(v, {})]
        out = {}
        for a in state.actions:
            if not targets:
                out[a.name] = False
                continue
            rel = False
            unknown = [v for v in a.reveals if v not in state.known]
            for values in itertools.product((False, True), repeat=len(unknown)):
                o = dict(zip(unknown, values))
                if not single.consistent(o):
                    continue
                if any(single.determined(v, o) for v in targets):
                    rel = True
                    break
            out[a.name] = rel
        return out
    finally:
        single.close()


def solve(state: FormalState) -> OracleResult:
    logical = isinstance(state.decision_rule, LogicalEntailment)
    status = logic.status(state)
    posts = None
    if logical:
        analysis = solver.analyze(state)
    else:
        analysis = probability.analyze(state)
        posts = [{"computed": {state.variables[i].name: v for i, v in g}, "p_target": str(p)}
                 for g, p in sorted(probability.posteriors(state).items())]
    rclass = analysis.resource_class(state)

    obligations, ob_trunc = extract(state) if logical else (None, False)
    # Relevance is a logical notion: "some outcome pins down a variable that matters".
    # Under the posterior rule it uses the obligations of the same state under the logical rule.
    rel_obs = obligations if logical else extract(_as_logical(state))[0]
    ob_vars = set().union(*[o.variables for o in rel_obs]) if rel_obs else set()
    relevance = _relevance_sat(state, ob_vars)

    optimal_names = {a for p in analysis.optimal_plans for a in p}
    minimal_names = None if analysis.minimal_truncated else {a for p in analysis.minimal_plans for a in p}
    roles = []
    for a in state.actions:
        in_min = None if minimal_names is None else a.name in minimal_names
        necessary = None
        if minimal_names is not None and analysis.minimal_plans:
            necessary = all(a.name in p for p in analysis.minimal_plans)
        alone = _alone(state, a.name, logical)
        if a.name in optimal_names:
            cat = "optimal"
        elif in_min:
            cat = "dominated"
        elif relevance[a.name]:
            cat = "relevant_insufficient"
        else:
            cat = "irrelevant"
        roles.append(ActionRole(
            name=a.name, resource=a.resource.value, cost=a.cost,
            reveals=[state.variables[v].name for v in a.reveals],
            already_known=all(v in state.known for v in a.reveals),
            alone_sufficient=alone, relevant=relevance[a.name],
            in_optimal_plan=a.name in optimal_names, in_minimal_plan=in_min,
            necessary=necessary, category=cat))

    disc = unres = why = None
    if obligations is not None:
        disc = discharge_map(state, obligations)
        unres = [o.id for o in unresolvable(state, obligations)]
        if not ob_trunc:
            why = {}
            for p in analysis.optimal_plans:
                entry = {}
                for name in p:
                    others = [state.action_index[b] for b in p if b != name]
                    only = [o.id for o in obligations
                            if discharges(state, state.action_index[name], o)
                            and not any(discharges(state, b, o) for b in others)]
                    entry[name] = only
                why["+".join(p)] = entry
    return OracleResult(
        decision_rule=state.decision_rule.to_json(), status=status, posteriors=posts,
        analysis=analysis, resource_class=rclass, necessity=analysis.necessity(state),
        actions=roles, obligations=obligations, obligations_truncated=ob_trunc,
        discharge=disc, unresolvable_obligations=unres, why_necessary=why)


def _as_logical(state: FormalState) -> FormalState:
    from dataclasses import replace
    return replace(state, decision_rule=LogicalEntailment())


def _alone(state: FormalState, name: str, logical: bool) -> bool:
    if logical:
        return solver.plan_sufficient(state, (name,))
    return probability.plan_sufficient(state, (name,))


def action_effects(state: FormalState, obligations: list[Obligation]) -> dict[str, list[str]]:
    return action_discharges(state, obligations)
