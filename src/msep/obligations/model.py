"""Epistemic obligations: explicit representations of what is unresolved.

Under the logical decision rule, the decision is blocked exactly by
"distinguishing pairs": two assignments consistent with everything known that
disagree on q. An obligation is a minimal set D of unknown variables such
that some distinguishing pair differs on D (and on q) and on nothing else.
Revealing any variable in D (or q itself) discharges it.

Facts (checked in the test suite):
- The current state is sufficient iff there are no obligations.
- A plan is sufficient iff it discharges every obligation.
- The MSEP is a minimum-cost set of actions discharging all obligations.

Obligation kinds, by the variables that can discharge them:
- TRUTH     only world variables ("truth(A) unresolved")
- COMPUTE   only computed variables ("value of computation c unresolved")
- EITHER    either kind can discharge it
- TARGET    no other variable can: only observing q itself helps
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from msep.world.state import FormalState, VarKind


class ObligationKind(str, Enum):
    TRUTH = "truth"
    COMPUTE = "compute"
    EITHER = "either"
    TARGET = "target"


@dataclass(frozen=True)
class Obligation:
    id: str
    variables: frozenset[int]  # unknown non-target variables; q always discharges too
    kind: ObligationKind

    def describe(self, state: FormalState) -> str:
        names = sorted(state.variables[v].name for v in self.variables)
        q = state.variables[state.target].name
        if not names:
            return f"{q} is not determined by any other variable; only observing {q} resolves it"
        if self.kind is ObligationKind.TRUTH:
            what = "truth of"
        elif self.kind is ObligationKind.COMPUTE:
            what = "value of computation"
        else:
            what = "value of"
        if len(names) == 1:
            return f"{what} {names[0]} unresolved"
        return f"{what} one of {{{', '.join(names)}}} unresolved"

    def to_json(self, state: FormalState) -> dict:
        return {"id": self.id, "kind": self.kind.value,
                "variables": sorted(state.variables[v].name for v in self.variables),
                "description": self.describe(state)}


def kind_of(state: FormalState, vs: frozenset[int]) -> ObligationKind:
    if not vs:
        return ObligationKind.TARGET
    kinds = {state.variables[v].kind for v in vs}
    if kinds == {VarKind.WORLD}:
        return ObligationKind.TRUTH
    if kinds == {VarKind.COMPUTED}:
        return ObligationKind.COMPUTE
    return ObligationKind.EITHER


def make_obligations(state: FormalState, sets) -> list[Obligation]:
    ordered = sorted(set(sets), key=lambda s: (len(s), sorted(s)))
    return [Obligation(f"O{i + 1}", s, kind_of(state, s)) for i, s in enumerate(ordered)]
