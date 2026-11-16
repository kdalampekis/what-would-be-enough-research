"""Computation tasks: the data that defines each computed variable.

A computed variable's value is a fixed function of data the agent can already
see (a number, a list, a set of premises). It does not depend on the latent
world. Only a computation action can reveal it, and the action reads only the
task data, never the world.

The syllogism task's semantics is adapted from STML `stml/logic.py`
(commit 15646ecab33603a060bd97d9e13561e36781e67e): exact region semantics for
the four categorical forms with existential import. See PRIOR_WORK.md.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Union

# -- arithmetic tasks --------------------------------------------------------


@dataclass(frozen=True)
class Divisible:
    n: int
    k: int

    kind = "divisible"

    def evaluate(self) -> bool:
        return self.n % self.k == 0

    def describe(self) -> str:
        return f"{self.n} is divisible by {self.k}"

    def to_json(self) -> dict:
        return {"kind": self.kind, "n": self.n, "k": self.k}


@dataclass(frozen=True)
class SumExceeds:
    values: tuple[int, ...]
    threshold: int

    kind = "sum_exceeds"

    def evaluate(self) -> bool:
        return sum(self.values) > self.threshold

    def describe(self) -> str:
        return f"the sum of {list(self.values)} exceeds {self.threshold}"

    def to_json(self) -> dict:
        return {"kind": self.kind, "values": list(self.values), "threshold": self.threshold}


# -- syllogism task (adapted from STML) --------------------------------------

FORMS = ("all", "no", "some", "some_not")
_NEG = {"all": "some_not", "some_not": "all", "no": "some", "some": "no"}
KIND_NAMES = ("wugs", "daxes", "blickets", "feps", "tomas", "zorbs")


def _region_set(n: int, form: str, a: int, b: int) -> int:
    ma, mb = 1 << a, 1 << b
    want_b = form in ("no", "some")
    bits = 0
    for r in range(1, 1 << n):
        if (r & ma) and bool(r & mb) == want_b:
            bits |= 1 << r
    return bits


def _satisfiable(n: int, claims: tuple[tuple[str, int, int], ...]) -> bool:
    full = 0
    for r in range(1, 1 << n):
        full |= 1 << r
    forced = 0
    for form, a, b in claims:
        if form in ("all", "no"):
            forced |= _region_set(n, form, a, b)
    allowed = full & ~forced
    needs = [c for c in claims if c[0] in ("some", "some_not")]
    needs += [("some", i, i) for i in range(n)]  # existential import
    return all(_region_set(n, f, a, b) & allowed for f, a, b in needs)


@dataclass(frozen=True)
class SyllogismFollows:
    n_kinds: int
    premises: tuple[tuple[str, int, int], ...]
    claim: tuple[str, int, int]

    kind = "syllogism_follows"

    def __post_init__(self) -> None:
        if not _satisfiable(self.n_kinds, self.premises):
            raise ValueError("syllogism premises are inconsistent")

    def evaluate(self) -> bool:
        form, a, b = self.claim
        return not _satisfiable(self.n_kinds, (*self.premises, (_NEG[form], a, b)))

    def describe(self) -> str:
        names = KIND_NAMES
        prem = "; ".join(_claim_text(c, names) for c in self.premises)
        return f"'{_claim_text(self.claim, names)}' follows from: {prem}"

    def to_json(self) -> dict:
        return {"kind": self.kind, "n_kinds": self.n_kinds,
                "premises": [list(p) for p in self.premises], "claim": list(self.claim)}


def _claim_text(c: tuple[str, int, int], names) -> str:
    form, a, b = c
    A, B = names[a], names[b]
    return {"all": f"All {A} are {B}", "no": f"No {A} are {B}",
            "some": f"Some {A} are {B}", "some_not": f"Some {A} are not {B}"}[form]


ComputeTask = Union[Divisible, SumExceeds, SyllogismFollows]
"""Simple task kinds. Used only by the random oracle-validation instances, where task
difficulty is irrelevant. Benchmark families use the certified tasks in certified_tasks.py."""


def task_from_json(d: dict) -> ComputeTask:
    from .certified_tasks import certified_from_json
    cert = certified_from_json(d)
    if cert is not None:
        return cert
    kind = d["kind"]
    if kind == "divisible":
        return Divisible(int(d["n"]), int(d["k"]))
    if kind == "sum_exceeds":
        return SumExceeds(tuple(int(v) for v in d["values"]), int(d["threshold"]))
    if kind == "syllogism_follows":
        return SyllogismFollows(int(d["n_kinds"]), tuple(tuple(p) for p in d["premises"]),
                                tuple(d["claim"]))
    raise ValueError(f"unknown task kind {kind!r}")


def make_task(rng: random.Random, value: bool, kind: str | None = None) -> ComputeTask:
    """A task whose (verified) value is `value`."""
    kind = kind or rng.choice(("divisible", "sum_exceeds", "syllogism_follows"))
    for _ in range(1000):
        if kind == "divisible":
            k = rng.choice((7, 11, 13, 17, 19, 23, 29, 31, 37))
            m = rng.randint(20, 400)
            n = k * m if value else k * m + rng.randint(1, k - 1)
            task: ComputeTask = Divisible(n, k)
        elif kind == "sum_exceeds":
            values = tuple(rng.randint(10, 99) for _ in range(rng.randint(5, 8)))
            s = sum(values)
            threshold = s - rng.randint(1, 15) if value else s + rng.randint(0, 15)
            task = SumExceeds(values, threshold)
        else:
            n = 3
            premises = tuple((rng.choice(FORMS), rng.randrange(n), rng.randrange(n))
                             for _ in range(rng.randint(2, 3)))
            premises = tuple(p for p in premises if p[1] != p[2]) or (("all", 0, 1),)
            if not _satisfiable(n, premises):
                continue
            claim = (rng.choice(FORMS), rng.randrange(n), rng.randrange(n))
            if claim[1] == claim[2] or claim in premises:
                continue
            task = SyllogismFollows(n, premises, claim)
        if task.evaluate() == value:
            return task
    raise RuntimeError(f"could not build a {kind} task with value {value}")
