"""The formal benchmark state S = (W, E, C, M, q, I, K, U).

- W  latent world: values of the world variables (LatentWorld; kept outside
     FormalState so no oracle can read it by accident).
- E  evidence: observed world-variable values.
- C  constraints: rules (formula trees) compiled to CNF.
- M  computational state: computed-variable values already worked out.
- q  target variable.
- I  information actions, K computation actions.
- U  costs (on actions) and the declared decision rule.

The agent's epistemic state is the set of full assignments (world variables
and computed variables) consistent with C, E and M. Computed variables that
have not been computed yet are treated as unknown, although each has a fixed
true value given by its task (logical uncertainty, see ASSUMPTIONS.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from functools import cached_property
from typing import Mapping, Union

from msep.actions.base import Action
from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction

from .compute_tasks import ComputeTask
from .constraints import Clause, Formula, evaluate, to_cnf, variables


class VarKind(str, Enum):
    WORLD = "world"
    COMPUTED = "computed"


@dataclass(frozen=True)
class Variable:
    name: str
    kind: VarKind
    label: str = ""  # natural-language label, rendering only


@dataclass(frozen=True)
class Rule:
    name: str
    formula: Formula


@dataclass(frozen=True)
class LogicalEntailment:
    """Sufficient iff the knowledge entails q or entails not-q."""

    kind = "logical_entailment"

    def to_json(self) -> dict:
        return {"kind": self.kind}


@dataclass(frozen=True)
class PosteriorThreshold:
    """Sufficient iff some answer d has P(q = d | knowledge, c) >= tau for every
    completion c of the not-yet-computed computed variables.

    World variables are random (independent prior, conditioned on C); computed
    variables are not random, so they are handled in the worst case.
    """

    tau: Fraction

    kind = "posterior_threshold"

    def __post_init__(self) -> None:
        if not (Fraction(1, 2) < self.tau <= 1):
            raise ValueError("tau must be in (1/2, 1]")

    def to_json(self) -> dict:
        return {"kind": self.kind, "tau": str(self.tau)}


DecisionRule = Union[LogicalEntailment, PosteriorThreshold]


@dataclass(frozen=True)
class FormalState:
    variables: tuple[Variable, ...]
    rules: tuple[Rule, ...]
    target: int
    evidence: tuple[tuple[int, bool], ...] = ()
    computed: tuple[tuple[int, bool], ...] = ()
    info_actions: tuple[InformationAction, ...] = ()
    comp_actions: tuple[ComputationAction, ...] = ()
    compute_tasks: tuple[tuple[int, ComputeTask], ...] = ()
    decision_rule: DecisionRule = field(default_factory=LogicalEntailment)
    prior: tuple[tuple[int, Fraction], ...] = ()

    def __post_init__(self) -> None:
        n = len(self.variables)
        names = [v.name for v in self.variables]
        if len(set(names)) != n:
            raise ValueError("variable names must be unique")
        if not 0 <= self.target < n:
            raise ValueError("target index out of range")
        for r in self.rules:
            if any(not 0 <= i < n for i in variables(r.formula)):
                raise ValueError(f"rule {r.name} uses an unknown variable")
        for i, _ in self.evidence:
            if self.variables[i].kind is not VarKind.WORLD:
                raise ValueError("evidence may only fix world variables")
        for i, _ in self.computed:
            if self.variables[i].kind is not VarKind.COMPUTED:
                raise ValueError("computational state may only fix computed variables")
        known = [i for i, _ in self.evidence] + [i for i, _ in self.computed]
        if len(set(known)) != len(known):
            raise ValueError("a variable is fixed twice")
        # Information/computation separation is structural, enforced here.
        for a in self.info_actions:
            if not isinstance(a, InformationAction):
                raise TypeError(f"{a.name} is not an InformationAction")
            for v in a.reveals:
                if self.variables[v].kind is not VarKind.WORLD:
                    raise ValueError(f"information action {a.name} may not reveal computed variable "
                                     f"{self.variables[v].name}")
        for a in self.comp_actions:
            if not isinstance(a, ComputationAction):
                raise TypeError(f"{a.name} is not a ComputationAction")
            for v in a.reveals:
                if self.variables[v].kind is not VarKind.COMPUTED:
                    raise ValueError(f"computation action {a.name} may not reveal world variable "
                                     f"{self.variables[v].name}")
        action_names = [a.name for a in self.actions]
        if len(set(action_names)) != len(action_names):
            raise ValueError("action names must be unique")
        tasks = dict(self.compute_tasks)
        for i, v in enumerate(self.variables):
            if v.kind is VarKind.COMPUTED and i not in tasks:
                raise ValueError(f"computed variable {v.name} has no task")
        for i in tasks:
            if self.variables[i].kind is not VarKind.COMPUTED:
                raise ValueError("only computed variables have tasks")
        for i, value in self.computed:
            if getattr(tasks[i], "opaque", False):
                continue  # an agent-side state cannot check a certified value; the environment produced it
            if tasks[i].evaluate() != value:
                raise ValueError(f"computed value of {self.variables[i].name} is wrong")
        if isinstance(self.decision_rule, PosteriorThreshold):
            pri = dict(self.prior)
            for i, v in enumerate(self.variables):
                if v.kind is VarKind.WORLD and not (0 < pri.get(i, Fraction(-1)) < 1):
                    raise ValueError(f"world variable {v.name} needs a prior in (0, 1)")
        for i, _ in self.prior:
            if self.variables[i].kind is not VarKind.WORLD:
                raise ValueError("priors apply to world variables only")

    # -- derived views -------------------------------------------------------
    @property
    def n(self) -> int:
        return len(self.variables)

    @property
    def actions(self) -> tuple[Action, ...]:
        return (*self.info_actions, *self.comp_actions)

    @cached_property
    def action_index(self) -> dict[str, Action]:
        return {a.name: a for a in self.actions}

    @cached_property
    def known(self) -> dict[int, bool]:
        return {**dict(self.evidence), **dict(self.computed)}

    @cached_property
    def tasks(self) -> dict[int, ComputeTask]:
        return dict(self.compute_tasks)

    @cached_property
    def prior_map(self) -> dict[int, Fraction]:
        return dict(self.prior)

    @cached_property
    def cnf(self) -> tuple[Clause, ...]:
        out: list[Clause] = []
        for r in self.rules:
            out.extend(to_cnf(r.formula))
        return tuple(out)

    def world_vars(self) -> list[int]:
        return [i for i, v in enumerate(self.variables) if v.kind is VarKind.WORLD]

    def computed_vars(self) -> list[int]:
        return [i for i, v in enumerate(self.variables) if v.kind is VarKind.COMPUTED]

    def true_computed_values(self) -> dict[int, bool]:
        return {i: t.evaluate() for i, t in self.tasks.items()}

    def plan_reveals(self, plan) -> frozenset[int]:
        out: set[int] = set()
        for name in plan:
            out.update(self.action_index[name].reveals)
        return frozenset(out)

    def with_knowledge(self, extra: Mapping[int, bool]) -> "FormalState":
        """Same state with additional observed / computed values."""
        ev = dict(self.evidence)
        cp = dict(self.computed)
        for i, val in extra.items():
            if i in ev or i in cp:
                if self.known[i] != val:
                    raise ValueError("new value contradicts known value")
                continue
            (ev if self.variables[i].kind is VarKind.WORLD else cp)[i] = val
        return _replace(self, evidence=tuple(sorted(ev.items())), computed=tuple(sorted(cp.items())))


def _replace(state: FormalState, **changes) -> FormalState:
    from dataclasses import replace
    return replace(state, **changes)


@dataclass(frozen=True)
class LatentWorld:
    values: tuple[tuple[int, bool], ...]

    @cached_property
    def as_dict(self) -> dict[int, bool]:
        return dict(self.values)

    def value(self, i: int) -> bool:
        return self.as_dict[i]


@dataclass(frozen=True)
class Instance:
    """A formal state together with its latent world (for execution and ex-post scoring)."""

    state: FormalState
    world: LatentWorld

    def __post_init__(self) -> None:
        s = self.state
        w = self.world.as_dict
        if set(w) != set(s.world_vars()):
            raise ValueError("latent world must assign exactly the world variables")
        for i, val in s.evidence:
            if w[i] != val:
                raise ValueError("evidence disagrees with the latent world")
        full = self.full_assignment()
        for r in s.rules:
            if not evaluate(r.formula, full):
                raise ValueError(f"latent world violates rule {r.name}")

    def full_assignment(self) -> dict[int, bool]:
        return {**self.world.as_dict, **self.state.true_computed_values()}

    def execute(self, action_name: str) -> dict[int, bool]:
        """Run one action. Information reads the world; computation reads only task data."""
        a = self.state.action_index[action_name]
        if isinstance(a, InformationAction):
            return a.execute(self.world)
        if isinstance(a, ComputationAction):
            return a.execute(self.state.tasks)
        raise TypeError(a)
