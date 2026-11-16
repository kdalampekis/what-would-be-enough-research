"""Each certified task is checked against an independent method."""

import itertools
import random
from fractions import Fraction

from pysat.solvers import Solver

from msep.world.certified_tasks import (CERTIFIED_KINDS, CnfSatisfiable, ModPow, PosteriorAbove, Primality, is_prime,
                                        make_certified_task)
from msep.world.compute_tasks import task_from_json


def test_miller_rabin_matches_trial_division():
    def trial(n):
        return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))
    assert all(is_prime(n) == trial(n) for n in range(0, 20000))
    rng = random.Random(0)
    for _ in range(300):
        n = rng.randrange(10 ** 6, 10 ** 8)
        assert is_prime(n) == trial(n)


def test_modpow_matches_square_and_multiply_by_hand():
    def slow(a, b, m):
        r, base = 1, a % m
        for bit in bin(b)[2:]:
            r = r * r % m
            if bit == "1":
                r = r * base % m
        return r
    rng = random.Random(1)
    for _ in range(200):
        a, b, m = rng.randrange(10 ** 9, 10 ** 11), rng.randrange(10 ** 9, 10 ** 11), rng.randrange(10 ** 10, 10 ** 12)
        assert ModPow(a, b, m, slow(a, b, m)).evaluate()


def test_cnf_value_certified_by_model_or_second_solver():
    rng = random.Random(2)
    for _ in range(40):
        for value in (False, True):
            t = make_certified_task(rng, value, "cnf_sat")
            with Solver(name="glucose4", bootstrap_with=[list(c) for c in t.clauses]) as s:
                sat = s.solve()
                if sat:  # certificate: the model satisfies every clause
                    model = set(s.get_model())
                    assert all(any(l in model for l in c) for c in t.clauses)
            assert sat == value


def test_cnf_small_instances_match_brute_force():
    rng = random.Random(3)
    for _ in range(200):
        n = 8
        clauses = tuple(tuple(v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), 3)) for _ in range(34))
        brute = any(all(any((l > 0) == bits[abs(l) - 1] for l in c) for c in clauses)
                    for bits in itertools.product((False, True), repeat=n))
        assert CnfSatisfiable(n, clauses).evaluate() == brute


def test_posterior_matches_joint_enumeration():
    rng = random.Random(4)
    for _ in range(100):
        t = make_certified_task(rng, rng.random() < 0.5, "posterior_above")
        joint_h = t.prior
        joint_n = 1 - t.prior
        for ph, pn in t.likelihoods:  # enumerate the joint over (H, e1..e6) restricted to all-seen
            joint_h *= ph
            joint_n *= pn
        assert t.posterior() == joint_h / (joint_h + joint_n)
        assert abs(t.posterior() - t.threshold) >= Fraction(4, 1000)  # not a borderline case


def test_values_and_roundtrip():
    rng = random.Random(5)
    for kind in CERTIFIED_KINDS:
        for value in (False, True):
            for _ in range(10):
                t = make_certified_task(rng, value, kind)
                assert t.evaluate() == value
                assert task_from_json(t.to_json()) == t


def test_nonprimes_are_hard_semiprimes():
    rng = random.Random(6)
    for _ in range(20):
        t = make_certified_task(rng, False, "primality")
        assert not any(t.n % p == 0 for p in range(2, 10 ** 4))
