import random
import re

import pytest

from msep.benchmark.families import SIBLING_TYPES, generate_family
from msep.benchmark.rendering import make_rendering, render_state
from msep.benchmark.schemas import instance_from_record, instance_record
from msep.benchmark.splits import split_of
from msep.oracle import minimal_plan
from msep.oracle.brute_force import BruteForce
from msep.world.state import Instance

FAMILIES = [generate_family(s) for s in range(12)]


def test_eleven_distinct_siblings():
    for f in FAMILIES:
        assert [s.sibling_type for s in f.siblings] == list(SIBLING_TYPES)
        keys = {(s.instance.state.known.items().__repr__(), tuple(a.name for a in s.instance.state.actions))
                for s in f.siblings}
        assert len(keys) == len(SIBLING_TYPES)  # no two siblings are the same formal state


def test_siblings_share_theory_and_world():
    for f in FAMILIES:
        base = f.siblings[0].instance
        for s in f.siblings[1:]:
            assert s.instance.state.rules == base.state.rules
            assert s.instance.state.compute_tasks == base.state.compute_tasks
            assert s.instance.world == base.world


def test_labels_agree_with_brute_force():
    for f in FAMILIES:
        for s in f.siblings:
            assert BruteForce(s.instance.state).analyze().key() == s.oracle.analysis.key()


def test_split_is_per_family():
    for f in FAMILIES:
        assert len({split_of(f.family_id) for _ in f.siblings}) == 1
    assert {split_of(f"F{i}") for i in range(200)} == {"train", "dev", "test"}


def test_record_roundtrip_reproduces_labels():
    f = FAMILIES[0]
    for s in f.siblings:
        rec = instance_record(family_id=f.family_id, instance_id="x", sibling_type=s.sibling_type, split="test",
                              instance=s.instance, oracle=s.oracle, transformation=s.transformation)
        inst = instance_from_record(rec)
        assert minimal_plan.solve(inst.state).to_json(inst.state) == rec["oracle"]
        assert inst.world == s.instance.world


def test_rendering_hides_role_names_and_maps_back():
    f = FAMILIES[1]
    r = make_rendering(f.siblings[3].instance.state, random.Random(0))
    for s in f.siblings:
        text = render_state(s.instance.state, r)
        for internal in ("w1", "w2", "wa", "dw", "dc", "z1", "zc1", "zc3", "c1", "c2", "decoy", "alias", "distractor", "R_target"):
            assert not re.search(rf"\b{internal}\b", text), internal
        for formal, shown in r.action_alias.items():
            assert r.formal_action(shown) == formal
            assert shown in text
