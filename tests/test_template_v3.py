"""Template v3: diverse structures, unbiased class sampling, exact labels, faithful rendering."""

import random

from msep.benchmark.parsing import parse_state
from msep.benchmark.rendering import make_rendering, render_state
from msep.benchmark.template_v3 import CORE, MOTIFS, generate_family_v3
from msep.oracle import minimal_plan
from msep.oracle.brute_force import BruteForce

FAMS = [generate_family_v3(s) for s in range(10)]


def test_core_classes_present_and_labels_exact():
    for f in FAMS:
        types = [s.sibling_type for s in f.siblings]
        assert all(t in types for t in CORE)
        for s in f.siblings:
            assert BruteForce(s.instance.state).analyze().key() == s.oracle.analysis.key()
            if s.sibling_type in CORE:
                assert s.oracle.resource_class.value == s.sibling_type


def test_siblings_share_theory_and_are_distinct():
    for f in FAMS:
        base = f.siblings[0].instance
        assert all(s.instance.state.rules == base.state.rules and s.instance.world == base.world for s in f.siblings)
        keys = {(repr(sorted(s.instance.state.known.items())), tuple(a.name for a in s.instance.state.actions))
                for s in f.siblings}
        assert len(keys) == len(f.siblings)


def test_motif_diversity():
    motifs = {f.base_params["motif"] for f in (generate_family_v3(s) for s in range(30))}
    assert motifs == set(MOTIFS)


def test_rendering_roundtrip_v3():
    for f in FAMS[:5]:
        r = make_rendering(f.siblings[0].instance.state, random.Random(0))
        for s in f.siblings:
            parsed = parse_state(render_state(s.instance.state, r))
            res = minimal_plan.solve(parsed)
            assert res.resource_class == s.oracle.resource_class
            assert res.analysis.optimal_cost == s.oracle.analysis.optimal_cost
