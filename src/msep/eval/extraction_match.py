"""Does an extracted formal state equal the reference state? (agent-visible content only)

Equal means: same variables with the same kinds, same known values, same actions (name, kind, cost,
revealed variables) and logically equivalent rule sets (the conjunction of the rules has the same truth
table). Rule order, rule splitting and equivalent rewritings do not matter; anything that changes the set
of possible worlds does.
"""

from __future__ import annotations

from itertools import product

from msep.world.constraints import evaluate
from msep.world.state import FormalState

MAX_VARS = 18


def _sig(s: FormalState) -> dict:
    names = [v.name for v in s.variables]
    return {"variables": {v.name: v.kind.value for v in s.variables},
            "known": {names[i]: bool(val) for i, val in s.known.items()},
            "actions": {a.name: (a.resource.value, int(a.cost), tuple(sorted(names[i] for i in a.reveals)))
                        for a in s.actions}}


def _models(s: FormalState, order: list[str]) -> set[tuple[bool, ...]]:
    idx = {v.name: i for i, v in enumerate(s.variables)}
    out = set()
    for vals in product((False, True), repeat=len(order)):
        asg = {idx[n]: v for n, v in zip(order, vals)}
        if all(evaluate(r.formula, asg) for r in s.rules):
            out.add(vals)
    return out


def compare(extracted: FormalState, reference: FormalState) -> dict:
    """Field-by-field agreement; `exact` is True only if every field agrees."""
    a, b = _sig(extracted), _sig(reference)
    out = {k: a[k] == b[k] for k in ("variables", "known", "actions")}
    if out["variables"] and len(b["variables"]) <= MAX_VARS:
        order = sorted(b["variables"])
        out["rules"] = _models(extracted, order) == _models(reference, order)
    else:
        out["rules"] = False if not out["variables"] else None
    out["exact"] = all(v is True for v in out.values())
    return out
