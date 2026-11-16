"""SAT-based logical reasoning (pysat, CaDiCaL).

Single-copy checks (status, entailment of a variable) and a two-copy
"distinguishing pair" encoding used by the plan solver and by obligation
extraction:

    copy 1 satisfies C, E, M and q;  copy 2 satisfies C, E, M and not q;
    e_v <-> (v in copy 1 == v in copy 2)  for every variable v.

A plan revealing the variables R is sufficient (logical rule) iff the
encoding is UNSAT under the assumptions {e_v : v in R}: no two assignments
that the plan cannot tell apart disagree on q.

The encoding style (selector/assumption literals on a persistent solver)
follows the STML referee; no STML code is used. See PRIOR_WORK.md.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from pysat.solvers import Solver

from msep.world.state import FormalState

from .sufficiency import Status

SOLVER = "cadical153"


def _shift(clause, offset: int):
    return [l + offset if l > 0 else l - offset for l in clause]


def satisfiable(state: FormalState, extra: Mapping[int, bool] | None = None) -> bool:
    fixed = {**state.known, **(extra or {})}
    with Solver(name=SOLVER, bootstrap_with=[list(c) for c in state.cnf]) as s:
        return s.solve(assumptions=[(i + 1) if v else -(i + 1) for i, v in fixed.items()])


def status(state: FormalState) -> Status:
    q = state.target
    can_true = satisfiable(state, {q: True})
    can_false = satisfiable(state, {q: False})
    if not can_true and not can_false:
        raise ValueError("state is inconsistent")
    if not can_false:
        return Status.ENTAILED
    if not can_true:
        return Status.CONTRADICTED
    return Status.UNDETERMINED


class SingleSolver:
    """Persistent solver over one copy, for many entailment queries."""

    def __init__(self, state: FormalState):
        self.state = state
        self.solver = Solver(name=SOLVER, bootstrap_with=[list(c) for c in state.cnf])
        self.base = [(i + 1) if v else -(i + 1) for i, v in state.known.items()]

    def close(self) -> None:
        self.solver.delete()

    def consistent(self, extra: Mapping[int, bool]) -> bool:
        assum = self.base + [(i + 1) if v else -(i + 1) for i, v in extra.items()]
        return self.solver.solve(assumptions=assum)

    def determined(self, var: int, extra: Mapping[int, bool]) -> bool:
        """Is `var` forced to one value by knowledge + extra (assumed consistent)?"""
        if var in extra or var in self.state.known:
            return True
        can_t = self.consistent({**extra, var: True})
        can_f = self.consistent({**extra, var: False})
        return not (can_t and can_f)


class PairSolver:
    """Two-copy distinguishing-pair encoding on a persistent incremental solver."""

    def __init__(self, state: FormalState):
        self.state = state
        n = state.n
        self.n = n
        self.solver = Solver(name=SOLVER)
        for c in state.cnf:
            self.solver.add_clause(list(c))
            self.solver.add_clause(_shift(c, n))
        for i, v in state.known.items():
            self.solver.add_clause([(i + 1) if v else -(i + 1)])
            self.solver.add_clause([(i + 1 + n) if v else -(i + 1 + n)])
        q = state.target
        self.solver.add_clause([q + 1])
        self.solver.add_clause([-(q + 1 + n)])
        for v in range(n):
            e, x1, x2 = self.eq(v), v + 1, v + 1 + n
            self.solver.add_clause([-e, -x1, x2])
            self.solver.add_clause([-e, x1, -x2])
            self.solver.add_clause([e, x1, x2])
            self.solver.add_clause([e, -x1, -x2])

    def eq(self, v: int) -> int:
        return 2 * self.n + 1 + v

    def close(self) -> None:
        self.solver.delete()

    def add_clause(self, clause: Iterable[int]) -> None:
        self.solver.add_clause(list(clause))

    def find_pair(self, equal_vars: Iterable[int]) -> tuple[dict[int, bool], dict[int, bool]] | None:
        """A q-true / q-false pair that agrees on `equal_vars`, or None."""
        if not self.solver.solve(assumptions=[self.eq(v) for v in equal_vars]):
            return None
        model = set(l for l in self.solver.get_model() if l > 0)
        a1 = {v: (v + 1) in model for v in range(self.n)}
        a2 = {v: (v + 1 + self.n) in model for v in range(self.n)}
        return a1, a2

    @staticmethod
    def difference(pair) -> frozenset[int]:
        a1, a2 = pair
        return frozenset(v for v in a1 if a1[v] != a2[v])
