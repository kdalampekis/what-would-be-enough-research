"""The agreement checks must be able to fail: planted solver bugs are detected."""

import random
from dataclasses import replace

from msep.oracle import logic, solver
from msep.oracle.brute_force import BruteForce
from msep.world.generator import random_instance
from msep.world.state import LogicalEntailment


def disagreements(n=400):
    bad = 0
    for seed in range(n):
        st = random_instance(random.Random(seed)).state
        if isinstance(st.decision_rule, LogicalEntailment) and solver.analyze(st).key() != BruteForce(st).analyze().key():
            bad += 1
    return bad


def test_truncated_difference_sets_are_caught(monkeypatch):
    orig = logic.PairSolver.difference
    monkeypatch.setattr(logic.PairSolver, "difference", staticmethod(lambda p: frozenset(sorted(orig(p))[:1])))
    assert disagreements() > 0


def test_unfixed_knowledge_is_caught(monkeypatch):
    orig = logic.PairSolver.__init__

    def bad_init(self, state):
        orig(self, replace(state, evidence=(), computed=()))
        for i, v in state.known.items():
            self.solver.add_clause([(i + 1) if v else -(i + 1)])

    monkeypatch.setattr(logic.PairSolver, "__init__", bad_init)
    assert disagreements() > 0
