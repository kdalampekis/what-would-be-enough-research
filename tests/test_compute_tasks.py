import itertools
import random

from msep.world.compute_tasks import FORMS, SyllogismFollows, make_task, task_from_json


def holds(form, a, b, model):
    if form == "all":
        return not any((r >> a) & 1 and not (r >> b) & 1 for r in model)
    if form == "no":
        return not any((r >> a) & 1 and (r >> b) & 1 for r in model)
    if form == "some":
        return any((r >> a) & 1 and (r >> b) & 1 for r in model)
    return any((r >> a) & 1 and not (r >> b) & 1 for r in model)


def brute_follows(n, premises, claim):
    regions = list(range(1, 1 << n))
    models = []
    for k in range(1 << len(regions)):
        m = {r for i, r in enumerate(regions) if (k >> i) & 1}
        if all(any((r >> i) & 1 for r in m) for i in range(n)) and all(holds(*p, m) for p in premises):
            models.append(m)
    return bool(models) and all(holds(*claim, m) for m in models)


def test_syllogism_semantics_matches_brute_force():
    """The adapted STML region semantics, checked against independent model enumeration."""
    rng = random.Random(3)
    checked = 0
    for _ in range(400):
        prem = tuple((rng.choice(FORMS), rng.randrange(3), rng.randrange(3)) for _ in range(rng.randint(1, 3)))
        claim = (rng.choice(FORMS), rng.randrange(3), rng.randrange(3))
        try:
            t = SyllogismFollows(3, prem, claim)
        except ValueError:
            continue
        assert t.evaluate() == brute_follows(3, prem, claim)
        checked += 1
    assert checked > 100


def test_make_task_values_and_roundtrip():
    rng = random.Random(0)
    for kind in ("divisible", "sum_exceeds", "syllogism_follows"):
        for value in (False, True):
            for _ in range(20):
                t = make_task(rng, value, kind)
                assert t.evaluate() == value
                assert task_from_json(t.to_json()) == t
