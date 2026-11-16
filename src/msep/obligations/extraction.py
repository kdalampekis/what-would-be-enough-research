"""Exact obligation extraction with SAT (logical decision rule).

Enumerates the minimal difference sets of distinguishing pairs:

    repeat:
      find a pair whose difference set contains no known obligation
        (for each known obligation D: some variable in D is equal across the pair)
      shrink it: for each variable v in the current set, look for a pair whose
        difference avoids v while staying inside the current set; adopt it
      record the shrunk set as a new obligation

A shrunk set S is minimal: for every v in S, no pair differs only within
S \\ {v}. The brute-force oracle computes the same family by enumeration.
"""

from __future__ import annotations

from msep.oracle.logic import PairSolver
from msep.world.state import FormalState, LogicalEntailment

from .model import Obligation, make_obligations

DEFAULT_CAP = 512


def extract(state: FormalState, cap: int = DEFAULT_CAP) -> tuple[list[Obligation], bool]:
    """Returns (obligations, truncated)."""
    if not isinstance(state.decision_rule, LogicalEntailment):
        raise ValueError("obligations are defined for the logical-entailment rule")
    q = state.target
    free = [v for v in range(state.n) if v not in state.known and v != q]
    pairs = PairSolver(state)
    found: list[frozenset[int]] = []
    truncated = False
    try:
        while True:
            pair = pairs.find_pair(())
            if pair is None:
                break
            current = PairSolver.difference(pair) - {q}
            changed = True
            while changed:
                changed = False
                for v in sorted(current):
                    keep = current - {v}
                    equal = [u for u in free if u not in keep]
                    smaller = pairs.find_pair(equal)
                    if smaller is not None:
                        current = PairSolver.difference(smaller) - {q}
                        changed = True
                        break
            found.append(current)
            if not current:
                break  # the empty set subsumes every other obligation
            if len(found) >= cap:
                truncated = True
                break
            pairs.add_clause([pairs.eq(v) for v in current])
    finally:
        pairs.close()
    if frozenset() in found:
        found = [frozenset()]
    return make_obligations(state, found), truncated
