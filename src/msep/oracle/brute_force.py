"""Brute-force oracle: exhaustive enumeration, the gold validation path.

Independent of the SAT path: it never reads the CNF and never calls a solver.
It enumerates every full assignment, keeps those that satisfy the rule
formulas (evaluated directly) and the known values, and decides everything by
set operations on those assignments. Exponential; intended for small worlds.
"""

from __future__ import annotations

import itertools
from fractions import Fraction

from msep.world.constraints import evaluate, variables
from msep.world.state import FormalState, LogicalEntailment, PosteriorThreshold, VarKind

from .sufficiency import PlanAnalysis, Status, canonical

MAX_VARS = 16
MAX_ACTIONS = 14


class BruteForce:
    def __init__(self, state: FormalState):
        if state.n > MAX_VARS or len(state.actions) > MAX_ACTIONS:
            raise ValueError("instance too large for brute force")
        self.state = state
        n = state.n
        # Per rule: the set of satisfying local patterns over its variables.
        checks = []
        for rule in state.rules:
            vs = sorted(variables(rule.formula))
            ok = set()
            for bits in itertools.product((False, True), repeat=len(vs)):
                if evaluate(rule.formula, dict(zip(vs, bits))):
                    ok.add(bits)
            checks.append((vs, ok))
        known = state.known
        self.known_mask = sum(1 << i for i in known)
        known_bits = sum(1 << i for i, v in known.items() if v)
        self.assignments: list[int] = []
        for a in range(1 << n):
            if a & self.known_mask != known_bits:
                continue
            if all(tuple(bool((a >> v) & 1) for v in vs) in ok for vs, ok in checks):
                self.assignments.append(a)
        if not self.assignments:
            raise ValueError("state is inconsistent")
        self.q = state.target
        self.T = [a for a in self.assignments if (a >> self.q) & 1]
        self.F = [a for a in self.assignments if not (a >> self.q) & 1]
        self.actions = list(state.actions)
        self.action_masks = [sum(1 << v for v in a.reveals) for a in self.actions]
        self.c_mask = sum(1 << i for i, v in enumerate(state.variables) if v.kind is VarKind.COMPUTED)
        rule = state.decision_rule
        if isinstance(rule, PosteriorThreshold):
            prior = state.prior_map
            self.weight = {}
            for a in self.assignments:
                w = Fraction(1)
                for i, p in prior.items():
                    w *= p if (a >> i) & 1 else 1 - p
                self.weight[a] = w

    # -- status ----------------------------------------------------------------
    def status(self) -> Status:
        if not self.F:
            return Status.ENTAILED
        if not self.T:
            return Status.CONTRADICTED
        return Status.UNDETERMINED

    # -- sufficiency -------------------------------------------------------------
    def _logical_sufficient(self, mask: int) -> bool:
        return {a & mask for a in self.T}.isdisjoint({a & mask for a in self.F})

    def _decision_ok(self, group: list[int], mask: int) -> bool:
        """Posterior rule on one branch (assignments sharing values on `mask`)."""
        tau = self.state.decision_rule.tau
        free_c = self.c_mask & ~mask
        by_gamma: dict[int, list[Fraction]] = {}
        for a in group:
            z = by_gamma.setdefault(a & free_c, [Fraction(0), Fraction(0)])
            z[0] += self.weight[a]
            if (a >> self.q) & 1:
                z[1] += self.weight[a]
        for answer_true in (True, False):
            if all(((zq if answer_true else z - zq) / z) >= tau for z, zq in by_gamma.values()):
                return True
        return False

    def _posterior_sufficient(self, mask: int) -> bool:
        branches: dict[int, list[int]] = {}
        for a in self.assignments:
            branches.setdefault(a & mask, []).append(a)
        return all(self._decision_ok(g, mask) for g in branches.values())

    def sufficient_mask(self, reveal_mask: int) -> bool:
        mask = self.known_mask | reveal_mask
        if isinstance(self.state.decision_rule, LogicalEntailment):
            return self._logical_sufficient(mask)
        return self._posterior_sufficient(mask)

    def plan_sufficient(self, plan) -> bool:
        idx = {a.name: i for i, a in enumerate(self.actions)}
        mask = 0
        for name in plan:
            mask |= self.action_masks[idx[name]]
        return self.sufficient_mask(mask)

    # -- full plan analysis ------------------------------------------------------
    def analyze(self) -> PlanAnalysis:
        m = len(self.actions)
        costs = [a.cost for a in self.actions]
        suff = [False] * (1 << m)
        reveal = [0] * (1 << m)
        cache: dict[int, bool] = {}
        for p in range(1 << m):
            if p:
                low = p & -p
                reveal[p] = reveal[p ^ low] | self.action_masks[low.bit_length() - 1]
            r = reveal[p]
            if r not in cache:
                cache[r] = self.sufficient_mask(r)
            suff[p] = cache[r]
        # any_sub[p]: some subset of p (including p) is sufficient
        any_sub = suff[:]
        for p in range(1 << m):
            if not any_sub[p]:
                for i in range(m):
                    if (p >> i) & 1 and any_sub[p ^ (1 << i)]:
                        any_sub[p] = True
                        break
        names = [a.name for a in self.actions]

        def plan_of(p: int):
            return canonical(names[i] for i in range(m) if (p >> i) & 1)

        minimal = []
        for p in range(1 << m):
            if suff[p] and not any(((p >> i) & 1) and any_sub[p ^ (1 << i)] for i in range(m)):
                minimal.append(p)
        cost_of = {p: sum(costs[i] for i in range(m) if (p >> i) & 1) for p in range(1 << m) if suff[p]}
        best = min(cost_of.values()) if cost_of else None
        optimal = [p for p, c in cost_of.items() if c == best]
        return PlanAnalysis(
            already_sufficient=suff[0],
            optimal_cost=best,
            optimal_plans=sorted(plan_of(p) for p in optimal),
            minimal_plans=sorted(plan_of(p) for p in minimal),
            extras={"sufficient_plans": sorted(plan_of(p) for p in range(1 << m) if suff[p])},
        )

    # -- obligations -------------------------------------------------------------
    def obligation_sets(self) -> list[frozenset[int]]:
        """Minimal sets of unknown non-target variables on which a q-true and a
        q-false consistent assignment differ (logical semantics)."""
        free = ((1 << self.state.n) - 1) & ~self.known_mask & ~(1 << self.q)
        diffs = {(t ^ f) & free for t in self.T for f in self.F}
        minimal = [d for d in diffs if not any(o != d and (o & d) == o for o in diffs)]
        return sorted((frozenset(i for i in range(self.state.n) if (d >> i) & 1) for d in minimal),
                      key=lambda s: (len(s), sorted(s)))

    def determined(self, var: int, group: list[int]) -> bool:
        vals = {(a >> var) & 1 for a in group}
        return len(vals) == 1

    def relevant(self, action_name: str, obligation_vars: frozenset[int]) -> bool:
        """Some outcome of the action determines a currently undetermined variable
        that matters for the decision (an obligation variable or q itself)."""
        idx = [a.name for a in self.actions].index(action_name)
        mask = self.action_masks[idx]
        targets = [v for v in (*obligation_vars, self.q) if not self.determined(v, self.assignments)]
        if not targets:
            return False
        branches: dict[int, list[int]] = {}
        for a in self.assignments:
            branches.setdefault(a & mask, []).append(a)
        return any(self.determined(v, g) for g in branches.values() for v in targets)

    # -- posterior (for cross-checking the WMC path) -------------------------------
    def posteriors(self) -> dict[int, Fraction]:
        """P(q | knowledge, gamma) for each completion gamma of the uncomputed computed variables."""
        free_c = self.c_mask & ~self.known_mask
        out: dict[int, list[Fraction]] = {}
        for a in self.assignments:
            z = out.setdefault(a & free_c, [Fraction(0), Fraction(0)])
            z[0] += self.weight[a]
            if (a >> self.q) & 1:
                z[1] += self.weight[a]
        return {g: zq / z for g, (z, zq) in out.items()}
