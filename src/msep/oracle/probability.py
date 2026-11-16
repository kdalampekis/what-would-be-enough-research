"""Exact probabilistic oracle for the posterior-threshold decision rule.

Second, independent path for probabilities: weighted model counting by
DPLL-style splitting over the CNF, with exact rational arithmetic. The brute
force oracle computes the same quantities by enumeration; the validation
suite requires them to be equal.

Semantics (declared in the instance's decision rule):
- World variables are random: independent priors, conditioned on C, E and
  the observed values.
- Computed variables are fixed facts, not random. Those not yet computed are
  handled in the worst case: the decision "q = d" is justified iff
  P(q = d | knowledge, c) >= tau for every completion c of the uncomputed
  computed variables that is consistent.
- A static plan is sufficient iff the decision is justified on every
  reachable branch of its outcomes.

This rule is not monotone: revealing more can move a posterior below tau.
Plan search therefore enumerates all plans instead of using refinement.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Mapping

from msep.world.state import FormalState, PosteriorThreshold, VarKind

from .sufficiency import Plan, PlanAnalysis, canonical

MAX_ACTIONS = 14


def _simplify(clauses, fixed: Mapping[int, bool]):
    out = []
    for c in clauses:
        keep = []
        sat = False
        for l in c:
            v = abs(l) - 1
            if v in fixed:
                if fixed[v] == (l > 0):
                    sat = True
                    break
            else:
                keep.append(l)
        if sat:
            continue
        if not keep:
            return None
        out.append(tuple(keep))
    return out


def _wmc(clauses, prior: Mapping[int, Fraction]) -> Fraction:
    """Sum over assignments of the variables in `clauses` of their prior weight,
    restricted to satisfying ones. Variables absent from the clauses sum to 1."""
    if clauses is None:
        return Fraction(0)
    if not clauses:
        return Fraction(1)
    shortest = min(clauses, key=len)
    v = abs(shortest[0]) - 1
    p = prior[v]
    total = Fraction(0)
    for val, w in ((True, p), (False, 1 - p)):
        sub = _simplify(clauses, {v: val})
        if sub is not None:
            total += w * _wmc(sub, prior)
    return total


def mass(state: FormalState, fixed: Mapping[int, bool]) -> Fraction:
    """Prior mass of world assignments consistent with C and `fixed`.

    Every computed variable must be fixed (they carry no prior)."""
    for i in state.computed_vars():
        if i not in fixed:
            raise ValueError("all computed variables must be fixed before weighting")
    prior = state.prior_map
    w = Fraction(1)
    for i, val in fixed.items():
        if state.variables[i].kind is VarKind.WORLD:
            w *= prior[i] if val else 1 - prior[i]
    return w * _wmc(_simplify(state.cnf, fixed), prior)


def posteriors(state: FormalState, extra: Mapping[int, bool] | None = None) -> dict[tuple, Fraction]:
    """P(q | knowledge + extra, gamma) for every consistent completion gamma."""
    fixed = {**state.known, **(extra or {})}
    free_c = [i for i in state.computed_vars() if i not in fixed]
    q = state.target
    out: dict[tuple, Fraction] = {}
    for values in itertools.product((False, True), repeat=len(free_c)):
        gamma = dict(zip(free_c, values))
        f = {**fixed, **gamma}
        z = mass(state, f)
        if z == 0:
            continue
        if q in f:
            zq = z if f[q] else Fraction(0)
        else:
            zq = mass(state, {**f, q: True})
        out[tuple(sorted(gamma.items()))] = zq / z
    return out


def decision_ok(state: FormalState, extra: Mapping[int, bool] | None = None) -> bool | None:
    """None if the knowledge is inconsistent; else whether the rule is met."""
    rule = state.decision_rule
    if not isinstance(rule, PosteriorThreshold):
        raise ValueError("probability.py handles the posterior-threshold rule")
    post = posteriors(state, extra)
    if not post:
        return None
    return all(p >= rule.tau for p in post.values()) or all(1 - p >= rule.tau for p in post.values())


class _Checker:
    def __init__(self, state: FormalState):
        self.state = state
        self.memo: dict[tuple, bool | None] = {}

    def branch(self, extra: dict[int, bool]) -> bool | None:
        key = tuple(sorted(extra.items()))
        if key not in self.memo:
            self.memo[key] = decision_ok(self.state, extra)
        return self.memo[key]

    def sufficient(self, reveals: frozenset[int]) -> bool:
        unknown = sorted(v for v in reveals if v not in self.state.known)
        reachable = False
        for values in itertools.product((False, True), repeat=len(unknown)):
            ok = self.branch(dict(zip(unknown, values)))
            if ok is None:
                continue
            reachable = True
            if not ok:
                return False
        return reachable


def plan_sufficient(state: FormalState, plan: Plan) -> bool:
    return _Checker(state).sufficient(state.plan_reveals(plan))


def analyze(state: FormalState) -> PlanAnalysis:
    actions = list(state.actions)
    m = len(actions)
    if m > MAX_ACTIONS:
        raise ValueError("too many actions for exhaustive plan search")
    checker = _Checker(state)
    by_reveal: dict[frozenset[int], bool] = {}
    suff: dict[frozenset[str], bool] = {}
    for k in range(m + 1):
        for combo in itertools.combinations(actions, k):
            r = frozenset(v for a in combo for v in a.reveals)
            if r not in by_reveal:
                by_reveal[r] = checker.sufficient(r)
            suff[frozenset(a.name for a in combo)] = by_reveal[r]
    sufficient = [p for p, ok in suff.items() if ok]
    minimal = [p for p in sufficient if not any(q < p for q in sufficient)]
    cost = {p: sum(state.action_index[a].cost for a in p) for p in sufficient}
    best = min(cost.values()) if cost else None
    return PlanAnalysis(
        already_sufficient=suff[frozenset()],
        optimal_cost=best,
        optimal_plans=sorted(canonical(p) for p, c in cost.items() if c == best),
        minimal_plans=sorted(canonical(p) for p in minimal),
        extras={"sufficient_plans": sorted(canonical(p) for p in sufficient)},
    )
