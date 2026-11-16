"""Shared definitions for sufficiency, plans and resource classes.

Definitions (also in ASSUMPTIONS.md, "Phase 1 formal semantics"):

- A static plan is a set of actions, executed without looking at outcomes.
- A plan is *sufficient* if for every outcome it can produce (every assignment
  consistent with C, E, M, projected onto the variables it reveals), the
  resulting knowledge satisfies the declared decision rule.
- A sufficient plan is *inclusion-minimal* if no proper subset is sufficient.
- A sufficient plan is *optimal* (the MSEP) if no sufficient plan is cheaper.
  With positive costs, every optimal plan is inclusion-minimal.
- Resource class: ALREADY_SUFFICIENT if the empty plan is sufficient; NEITHER
  if no plan over the available actions is sufficient; otherwise the shared
  composition of the optimal plans (INFORMATION_ONLY, COMPUTATION_ONLY,
  BOTH), or AMBIGUOUS when optimal plans of different compositions tie.

This module holds only definitions and the result type. The independent
oracles live in brute_force.py, solver.py and probability.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from msep.actions.base import Resource
from msep.world.state import FormalState, Instance, LogicalEntailment

Plan = tuple[str, ...]  # canonical: sorted action names


class ResourceClass(str, Enum):
    ALREADY_SUFFICIENT = "ALREADY_SUFFICIENT"
    INFORMATION_ONLY = "INFORMATION_ONLY"
    COMPUTATION_ONLY = "COMPUTATION_ONLY"
    BOTH = "BOTH"
    NEITHER = "NEITHER"
    AMBIGUOUS = "AMBIGUOUS"


class Status(str, Enum):
    ENTAILED = "entailed"
    CONTRADICTED = "contradicted"
    UNDETERMINED = "undetermined"


class Composition(str, Enum):
    NONE = "none"
    INFORMATION = "information"
    COMPUTATION = "computation"
    BOTH = "both"


def canonical(plan: Iterable[str]) -> Plan:
    return tuple(sorted(set(plan)))


def plan_cost(state: FormalState, plan: Iterable[str]) -> int:
    return sum(state.action_index[a].cost for a in set(plan))


def composition(state: FormalState, plan: Iterable[str]) -> Composition:
    kinds = {state.action_index[a].resource for a in plan}
    info = Resource.INFORMATION in kinds
    comp = Resource.COMPUTATION in kinds
    if info and comp:
        return Composition.BOTH
    if info:
        return Composition.INFORMATION
    if comp:
        return Composition.COMPUTATION
    return Composition.NONE


_CLASS_OF = {
    Composition.INFORMATION: ResourceClass.INFORMATION_ONLY,
    Composition.COMPUTATION: ResourceClass.COMPUTATION_ONLY,
    Composition.BOTH: ResourceClass.BOTH,
}


@dataclass
class PlanAnalysis:
    """What every exact oracle path must agree on."""

    already_sufficient: bool
    optimal_cost: int | None
    optimal_plans: list[Plan]
    minimal_plans: list[Plan]
    minimal_truncated: bool = False
    extras: dict = field(default_factory=dict)

    def resource_class(self, state: FormalState) -> ResourceClass:
        if self.already_sufficient:
            return ResourceClass.ALREADY_SUFFICIENT
        if not self.optimal_plans:
            return ResourceClass.NEITHER
        comps = {composition(state, p) for p in self.optimal_plans}
        if len(comps) > 1:
            return ResourceClass.AMBIGUOUS
        return _CLASS_OF[comps.pop()]

    def necessity(self, state: FormalState) -> dict:
        """Is an information (computation) action part of every sufficient plan?

        Every sufficient plan contains an inclusion-minimal sufficient plan, so it
        is enough to inspect the minimal plans. Undefined if enumeration was cut off.
        """
        if self.minimal_truncated:
            return {"information_necessary": None, "computation_necessary": None,
                    "class_cost_invariant": None}
        if self.already_sufficient or not self.minimal_plans:
            # ALREADY_SUFFICIENT and NEITHER do not depend on costs.
            return {"information_necessary": None, "computation_necessary": None,
                    "class_cost_invariant": True}
        comps = [composition(state, p) for p in self.minimal_plans]
        info = all(c in (Composition.INFORMATION, Composition.BOTH) for c in comps)
        comp = all(c in (Composition.COMPUTATION, Composition.BOTH) for c in comps)
        return {"information_necessary": info, "computation_necessary": comp,
                "class_cost_invariant": len(set(comps)) == 1}

    def key(self) -> dict:
        """Comparable summary used by the validation suite."""
        return {
            "already_sufficient": self.already_sufficient,
            "optimal_cost": self.optimal_cost,
            "optimal_plans": sorted(self.optimal_plans),
            "minimal_plans": None if self.minimal_truncated else sorted(self.minimal_plans),
        }


# -- convenience dispatch ------------------------------------------------------

def is_sufficient(state: FormalState, plan: Iterable[str]) -> bool:
    """Exact ex-ante sufficiency of a static plan under the state's decision rule."""
    if isinstance(state.decision_rule, LogicalEntailment):
        from . import solver
        return solver.plan_sufficient(state, canonical(plan))
    from . import probability
    return probability.plan_sufficient(state, canonical(plan))


def expost_sufficient(instance: Instance, executed: Iterable[str]) -> bool:
    """Is the decision justified after executing these actions in the actual world?"""
    state = instance.state
    learned: dict[int, bool] = {}
    for a in executed:
        learned.update(instance.execute(a))
    return is_sufficient(state.with_knowledge(learned), ())
