"""Computation cannot reveal hidden world facts: its outcomes do not depend on the world."""

import itertools
import random

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.constraints import evaluate
from msep.world.generator import random_instance
from msep.world.state import Instance, LatentWorld


def consistent_worlds(state):
    """Every latent world compatible with the rules, the evidence and the true computed values."""
    true_c = state.true_computed_values()
    wv = state.world_vars()
    for bits in itertools.product((False, True), repeat=len(wv)):
        w = dict(zip(wv, bits))
        if any(w[i] != v for i, v in state.evidence):
            continue
        full = {**w, **true_c}
        if all(evaluate(r.formula, full) for r in state.rules):
            yield LatentWorld(tuple(sorted(w.items())))


def test_computation_outcomes_are_world_invariant():
    info_varies = 0
    for seed in range(400):
        st = random_instance(random.Random(seed)).state
        worlds = list(consistent_worlds(st))
        assert worlds
        for a in st.actions:
            outcomes = {tuple(sorted(Instance(st, w).execute(a.name).items())) for w in worlds}
            if isinstance(a, ComputationAction):
                assert len(outcomes) == 1, (seed, a.name)
            elif isinstance(a, InformationAction) and len(outcomes) > 1:
                info_varies += 1
    assert info_varies > 50  # information really does depend on the world
