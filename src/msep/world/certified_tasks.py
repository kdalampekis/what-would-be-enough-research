"""Certified computation tasks used by the benchmark families.

COMPUTE means: run a certified procedure (code execution, a primality test, a
SAT solver, an exact posterior calculation) on inputs the agent already has.
The inputs are known; the certified result is not yet part of the decision
state. Each task is chosen so that working it out mentally while picking
actions is impractical:

- ModPow           EXECUTE_CODE       pow(a, b, m) == r, with 10-12 digit numbers
- Primality        RUN_PRIMALITY_TEST N is prime, N has 13-14 digits (non-primes are
                                      products of two 7-digit primes)
- CnfSatisfiable   RUN_SOLVER         a random 3-CNF near the satisfiability threshold
                                      (20 variables, about 85 clauses) is satisfiable
- PosteriorAbove   COMPUTE_POSTERIOR  P(H | six observations) under a naive-Bayes model
                                      exceeds a threshold within 0.04 of the true value

Each value is computed exactly. The test suite checks every evaluator against
an independent method (naive exponentiation, trial division, model checking
plus a second SAT solver, enumeration over the joint distribution).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

# -- helpers -------------------------------------------------------------------

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)  # deterministic below 3.3e24


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _random_prime(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        n = rng.randrange(lo, hi) | 1
        if is_prime(n):
            return n


# -- tasks -----------------------------------------------------------------------

@dataclass(frozen=True)
class ModPow:
    a: int
    b: int
    m: int
    r: int

    kind = "modpow"
    verb = "EXECUTE_CODE"

    def evaluate(self) -> bool:
        return pow(self.a, self.b, self.m) == self.r

    def describe(self) -> str:
        return f"pow({self.a}, {self.b}, {self.m}) equals {self.r}"

    def to_json(self) -> dict:
        return {"kind": self.kind, "a": self.a, "b": self.b, "m": self.m, "r": self.r}


@dataclass(frozen=True)
class Primality:
    n: int

    kind = "primality"
    verb = "RUN_PRIMALITY_TEST"

    def evaluate(self) -> bool:
        return is_prime(self.n)

    def describe(self) -> str:
        return f"{self.n} is a prime number"

    def to_json(self) -> dict:
        return {"kind": self.kind, "n": self.n}


@dataclass(frozen=True)
class CnfSatisfiable:
    n_vars: int
    clauses: tuple[tuple[int, ...], ...]

    kind = "cnf_sat"
    verb = "RUN_SOLVER"

    def evaluate(self) -> bool:
        from pysat.solvers import Solver
        with Solver(name="cadical153", bootstrap_with=[list(c) for c in self.clauses]) as s:
            return s.solve()

    def describe(self) -> str:
        def lit(l):
            return f"x{abs(l)}" if l > 0 else f"not x{abs(l)}"
        body = "; ".join("(" + " or ".join(lit(l) for l in c) + ")" for c in self.clauses)
        return (f"the following constraint set over x1..x{self.n_vars} is satisfiable "
                f"(all {len(self.clauses)} clauses true at once): {body}")

    def to_json(self) -> dict:
        return {"kind": self.kind, "n_vars": self.n_vars, "clauses": [list(c) for c in self.clauses]}


@dataclass(frozen=True)
class PosteriorAbove:
    """Naive Bayes: prior P(H); per observation i, P(e_i | H) and P(e_i | not H); all e_i observed true."""

    prior: Fraction
    likelihoods: tuple[tuple[Fraction, Fraction], ...]
    threshold: Fraction

    kind = "posterior_above"
    verb = "COMPUTE_POSTERIOR"

    def posterior(self) -> Fraction:
        num = self.prior
        den = 1 - self.prior
        for ph, pn in self.likelihoods:
            num *= ph
            den *= pn
        return num / (num + den)

    def evaluate(self) -> bool:
        return self.posterior() > self.threshold

    def describe(self) -> str:
        obs = "; ".join(f"observation {i + 1}: P(seen | H) = {ph}, P(seen | not H) = {pn}"
                        for i, (ph, pn) in enumerate(self.likelihoods))
        n = _NUMBER_WORDS.get(len(self.likelihoods), str(len(self.likelihoods)))
        digits = 3 if (self.threshold * 1000).denominator == 1 else 4
        return (f"P(H | all {n} observations seen) exceeds {float(self.threshold):.{digits}f}, where P(H) = {self.prior}, "
                f"the observations are independent given H and given not H, and {obs}")

    def to_json(self) -> dict:
        return {"kind": self.kind, "prior": str(self.prior),
                "likelihoods": [[str(a), str(b)] for a, b in self.likelihoods], "threshold": str(self.threshold)}


CERTIFIED_KINDS = ("modpow", "primality", "cnf_sat", "posterior_above")
_NUMBER_WORDS = {6: "six", 10: "ten", 16: "sixteen"}


def certified_from_json(d: dict):
    k = d["kind"]
    if k == "modpow":
        return ModPow(int(d["a"]), int(d["b"]), int(d["m"]), int(d["r"]))
    if k == "primality":
        return Primality(int(d["n"]))
    if k == "cnf_sat":
        return CnfSatisfiable(int(d["n_vars"]), tuple(tuple(int(x) for x in c) for c in d["clauses"]))
    if k == "posterior_above":
        return PosteriorAbove(Fraction(d["prior"]), tuple((Fraction(a), Fraction(b)) for a, b in d["likelihoods"]),
                              Fraction(d["threshold"]))
    return None


def _next_prime(n: int) -> int:
    n |= 1
    while not is_prime(n):
        n += 2
    return n


def _make_v2(rng: random.Random, value: bool, kind: str):
    for _ in range(2000):
        if kind == "modpow":
            a = rng.randrange(10 ** 9, 10 ** 11)
            b = rng.randrange(10 ** 9, 10 ** 11)
            m = _next_prime(rng.randrange(10 ** 10, 10 ** 12))
            true_r = pow(a, b, m)
            r = true_r if value else (true_r + rng.randrange(1, m)) % m
            t = ModPow(a, b, m, r)
        elif kind == "primality":
            target = rng.randrange(2 * 10 ** 12, 10 ** 14)
            if value:
                n = _next_prime(target)
            else:
                p = _random_prime(rng, 10 ** 6, 10 ** 7)
                n = p * _next_prime(max(10 ** 6, target // p))
            t = Primality(n)
        elif kind == "cnf_sat":
            nv = 20
            clauses = tuple(tuple(v if rng.random() < 0.5 else -v for v in rng.sample(range(1, nv + 1), 3))
                            for _ in range(85))
            t = CnfSatisfiable(nv, clauses)
        else:
            prior = Fraction(rng.randint(10, 90), 100)
            lik = tuple((Fraction(rng.randint(5, 95), 100), Fraction(rng.randint(5, 95), 100)) for _ in range(16))
            p = PosteriorAbove(prior, lik, Fraction(1, 2)).posterior()
            if not (Fraction(1, 10) < p < Fraction(9, 10)):
                continue
            gap = Fraction(rng.randint(2, 15), 10000)  # rounded log-sums score at chance at this margin
            thr = Fraction(round((p - gap if value else p + gap) * 10000), 10000)
            t = PosteriorAbove(prior, lik, thr)
        if t.evaluate() == value:
            return t
    raise RuntimeError(f"could not build a v2 {kind} task with value {value}")


def make_certified_task(rng: random.Random, value: bool, kind: str | None = None, version: int = 1):
    """version 1: the tasks used by pool_v1/pool_v2 (kept so those pools regenerate exactly).
    version 2 (2026-11-04, after the adversarial audit) removes mental shortcuts:
      modpow     prime modulus, so residue checks against small factors of m are impossible
      primality  primes and semiprimes drawn from the same size distribution
      posterior  sixteen observations, likelihoods in hundredths, threshold within 0.0002-0.0015 of the truth
    """
    if version == 2:
        return _make_v2(rng, value, kind or rng.choice(CERTIFIED_KINDS))
    kind = kind or rng.choice(CERTIFIED_KINDS)
    for _ in range(2000):
        if kind == "modpow":
            a = rng.randrange(10 ** 9, 10 ** 11)
            b = rng.randrange(10 ** 9, 10 ** 11)
            m = rng.randrange(10 ** 10, 10 ** 12)
            true_r = pow(a, b, m)
            r = true_r if value else (true_r + rng.randrange(1, m)) % m
            t = ModPow(a, b, m, r)
        elif kind == "primality":
            if value:
                n = _random_prime(rng, 10 ** 12, 10 ** 14)
            else:
                n = _random_prime(rng, 10 ** 6, 10 ** 7) * _random_prime(rng, 10 ** 6, 10 ** 7)
            t = Primality(n)
        elif kind == "cnf_sat":
            nv = 20
            clauses = []
            for _ in range(85):
                vs = rng.sample(range(1, nv + 1), 3)
                clauses.append(tuple(v if rng.random() < 0.5 else -v for v in vs))
            t = CnfSatisfiable(nv, tuple(clauses))
        else:
            prior = Fraction(rng.randint(1, 9), 10)
            lik = tuple((Fraction(rng.randint(2, 18), 20), Fraction(rng.randint(2, 18), 20)) for _ in range(6))
            base = PosteriorAbove(prior, lik, Fraction(1, 2))
            p = base.posterior()
            if not (Fraction(1, 10) < p < Fraction(9, 10)):
                continue
            gap = Fraction(rng.randint(5, 40), 1000)
            thr = p - gap if value else p + gap
            if not (0 < thr < 1):
                continue
            thr = Fraction(round(thr * 1000), 1000)  # shown with three decimals
            t = PosteriorAbove(prior, lik, thr)
        if t.evaluate() == value:
            return t
    raise RuntimeError(f"could not build a {kind} task with value {value}")


class OpaqueTaskError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpaqueTask:
    """Agent-side view of a computation task: its description only.

    It cannot be evaluated. An agent that wants the certified result must run the
    computation action in the environment (and pay for it). Used by the realistic
    planner so it cannot compute certified values for free."""

    description: str
    opaque = True
    kind = "opaque"
    verb = "COMPUTE"

    def evaluate(self) -> bool:
        raise OpaqueTaskError("opaque task: run its computation action in the environment")

    def describe(self) -> str:
        return self.description

    def to_json(self) -> dict:
        return {"kind": "opaque", "description": self.description}
