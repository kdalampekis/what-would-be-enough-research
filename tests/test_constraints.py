import itertools
import random

from msep.world.constraints import And, Iff, Implies, Not, Or, evaluate, from_json, lit, to_cnf, to_json, variables


def random_formula(rng, depth=0):
    if depth > 2 or rng.random() < 0.3:
        return lit(rng.randrange(5), rng.random() < 0.5)
    op = rng.randrange(5)
    if op == 0:
        return Not(random_formula(rng, depth + 1))
    if op == 1:
        return And(tuple(random_formula(rng, depth + 1) for _ in range(rng.randint(1, 3))))
    if op == 2:
        return Or(tuple(random_formula(rng, depth + 1) for _ in range(rng.randint(1, 3))))
    if op == 3:
        return Implies(random_formula(rng, depth + 1), random_formula(rng, depth + 1))
    return Iff(random_formula(rng, depth + 1), random_formula(rng, depth + 1))


def cnf_holds(cnf, a):
    return all(any(a[abs(l) - 1] == (l > 0) for l in c) for c in cnf)


def test_cnf_is_exact():
    rng = random.Random(1)
    for _ in range(300):
        f = random_formula(rng)
        cnf = to_cnf(f)
        vs = sorted(variables(f))
        for bits in itertools.product((False, True), repeat=5):
            a = dict(enumerate(bits))
            assert evaluate(f, a) == cnf_holds(cnf, a)
        assert from_json(to_json(f)) == f
