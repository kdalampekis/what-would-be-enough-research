"""Propositional formulas over indexed variables, and their exact CNF compilation.

Rules are authored as small formula trees (used for rendering and for the
brute-force oracle). The SAT-based oracle uses the CNF compiled here. The CNF
is produced from the formula's truth table, so it is exact by construction;
tests also check it against direct formula evaluation.

CNF clauses use DIMACS conventions: variable index i is literal i + 1 (true)
or -(i + 1) (false).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Mapping, Union

Clause = tuple[int, ...]
MAX_FORMULA_VARS = 10


@dataclass(frozen=True)
class Var:
    index: int


@dataclass(frozen=True)
class Not:
    arg: "Formula"


@dataclass(frozen=True)
class And:
    args: tuple["Formula", ...]


@dataclass(frozen=True)
class Or:
    args: tuple["Formula", ...]


@dataclass(frozen=True)
class Implies:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True)
class Iff:
    left: "Formula"
    right: "Formula"


Formula = Union[Var, Not, And, Or, Implies, Iff]


def lit(index: int, positive: bool = True) -> Formula:
    return Var(index) if positive else Not(Var(index))


def evaluate(f: Formula, assignment: Mapping[int, bool]) -> bool:
    if isinstance(f, Var):
        return assignment[f.index]
    if isinstance(f, Not):
        return not evaluate(f.arg, assignment)
    if isinstance(f, And):
        return all(evaluate(a, assignment) for a in f.args)
    if isinstance(f, Or):
        return any(evaluate(a, assignment) for a in f.args)
    if isinstance(f, Implies):
        return (not evaluate(f.left, assignment)) or evaluate(f.right, assignment)
    if isinstance(f, Iff):
        return evaluate(f.left, assignment) == evaluate(f.right, assignment)
    raise TypeError(f"not a formula: {f!r}")


def variables(f: Formula) -> frozenset[int]:
    if isinstance(f, Var):
        return frozenset({f.index})
    if isinstance(f, Not):
        return variables(f.arg)
    if isinstance(f, (And, Or)):
        out: frozenset[int] = frozenset()
        for a in f.args:
            out |= variables(a)
        return out
    if isinstance(f, (Implies, Iff)):
        return variables(f.left) | variables(f.right)
    raise TypeError(f"not a formula: {f!r}")


def to_cnf(f: Formula) -> list[Clause]:
    """Exact CNF: one blocking clause per falsifying assignment of the formula's variables."""
    vs = sorted(variables(f))
    if len(vs) > MAX_FORMULA_VARS:
        raise ValueError(f"formula has {len(vs)} variables; limit is {MAX_FORMULA_VARS}")
    clauses: list[Clause] = []
    for values in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, values))
        if not evaluate(f, assignment):
            clauses.append(tuple(-(v + 1) if val else (v + 1) for v, val in assignment.items()))
    return clauses


def render(f: Formula, names: Mapping[int, str]) -> str:
    """Plain-text rendering used only for display, never by any oracle."""
    if isinstance(f, Var):
        return names[f.index]
    if isinstance(f, Not):
        inner = render(f.arg, names)
        return f"not {inner}" if isinstance(f.arg, Var) else f"not ({inner})"
    if isinstance(f, And):
        return " and ".join(_paren(a, names) for a in f.args)
    if isinstance(f, Or):
        return " or ".join(_paren(a, names) for a in f.args)
    if isinstance(f, Implies):
        # "then" delimits and/or unambiguously; nested conditionals/biconditionals need parentheses
        return f"if {_paren_cond(f.left, names)} then {_paren_cond(f.right, names)}"
    if isinstance(f, Iff):
        # A complex left side must be parenthesised: "a iff not b iff not c" is ambiguous.
        return f"{_paren(f.left, names)} if and only if {_paren(f.right, names)}"
    raise TypeError(f"not a formula: {f!r}")


def _paren_cond(f: Formula, names: Mapping[int, str]) -> str:
    text = render(f, names)
    return f"({text})" if isinstance(f, (Implies, Iff)) else text


def _paren(f: Formula, names: Mapping[int, str]) -> str:
    text = render(f, names)
    return f"({text})" if isinstance(f, (And, Or, Implies, Iff)) else text


def to_json(f: Formula) -> dict:
    if isinstance(f, Var):
        return {"op": "var", "index": f.index}
    if isinstance(f, Not):
        return {"op": "not", "arg": to_json(f.arg)}
    if isinstance(f, And):
        return {"op": "and", "args": [to_json(a) for a in f.args]}
    if isinstance(f, Or):
        return {"op": "or", "args": [to_json(a) for a in f.args]}
    if isinstance(f, Implies):
        return {"op": "implies", "left": to_json(f.left), "right": to_json(f.right)}
    if isinstance(f, Iff):
        return {"op": "iff", "left": to_json(f.left), "right": to_json(f.right)}
    raise TypeError(f"not a formula: {f!r}")


def from_json(d: dict) -> Formula:
    op = d["op"]
    if op == "var":
        return Var(int(d["index"]))
    if op == "not":
        return Not(from_json(d["arg"]))
    if op == "and":
        return And(tuple(from_json(a) for a in d["args"]))
    if op == "or":
        return Or(tuple(from_json(a) for a in d["args"]))
    if op == "implies":
        return Implies(from_json(d["left"]), from_json(d["right"]))
    if op == "iff":
        return Iff(from_json(d["left"]), from_json(d["right"]))
    raise ValueError(f"unknown op {op!r}")
