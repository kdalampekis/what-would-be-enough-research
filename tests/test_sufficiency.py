"""Hand-checked cases for sufficiency, classes, relevance and the posterior rule."""

from fractions import Fraction

from msep.oracle import minimal_plan, probability, solver
from msep.oracle.brute_force import BruteForce
from msep.oracle.sufficiency import ResourceClass, Status
from msep.world.state import PosteriorThreshold

from helpers import A, C, Q, and_state


def test_both():
    st = and_state()
    res = minimal_plan.solve(st)
    assert res.status is Status.UNDETERMINED
    assert res.resource_class is ResourceClass.BOTH
    assert res.analysis.optimal_plans == [("ASK_A", "COMPUTE_C")]
    assert res.analysis.optimal_cost == 3
    assert res.necessity["information_necessary"] and res.necessity["computation_necessary"]


def test_information_only_and_computation_only():
    assert minimal_plan.solve(and_state(known=((C, True),))).resource_class is ResourceClass.INFORMATION_ONLY
    assert minimal_plan.solve(and_state(known=((A, True),))).resource_class is ResourceClass.COMPUTATION_ONLY


def test_already_sufficient_when_one_conjunct_false():
    res = minimal_plan.solve(and_state(known=((A, False),)))
    assert res.resource_class is ResourceClass.ALREADY_SUFFICIENT
    assert res.status is Status.CONTRADICTED
    assert res.obligations == []


def test_neither_when_ask_missing():
    res = minimal_plan.solve(and_state(actions=("COMPUTE_C",)))
    assert res.resource_class is ResourceClass.NEITHER
    assert res.unresolvable_obligations  # truth of A cannot be discharged


def test_relevant_but_insufficient_decoy():
    st = and_state(known=((C, True),), actions=("ASK_A", "ASK_D"), decoy=True)
    res = minimal_plan.solve(st)
    roles = {r.name: r for r in res.actions}
    assert roles["ASK_D"].relevant and not roles["ASK_D"].alone_sufficient
    assert roles["ASK_D"].category == "relevant_insufficient"
    assert roles["ASK_A"].category == "optimal"


def test_observing_target_discharges_everything():
    res = minimal_plan.solve(and_state(actions=("ASK_q",)))
    assert res.analysis.optimal_plans == [("ASK_q",)]
    assert res.resource_class is ResourceClass.INFORMATION_ONLY


def test_high_probability_is_not_entailment():
    """P(q) = 0.99 with C computed true: answering is justified at tau = 0.9, not at tau = 1."""
    prior = ((Q, Fraction(1, 2)), (A, Fraction(99, 100)), (3, Fraction(1, 2)))
    st90 = and_state(known=((C, True),), rule=PosteriorThreshold(Fraction(9, 10)), prior=prior)
    st100 = and_state(known=((C, True),), rule=PosteriorThreshold(Fraction(1)), prior=prior)
    assert probability.decision_ok(st90) is True
    assert probability.decision_ok(st100) is False
    assert minimal_plan.solve(st90).resource_class is ResourceClass.ALREADY_SUFFICIENT
    assert minimal_plan.solve(st100).resource_class is ResourceClass.INFORMATION_ONLY


def test_posterior_rule_is_not_monotone():
    """Already justified at tau = 0.9, but revealing the decoy D can push a branch below tau.

    q <-> A (C known true), D -> A, P(A) = 0.85, P(D) = 0.5 before conditioning on the rule.
    Overall P(A) = 0.85 / 0.925 > 0.9; after D = false, P(A) = 0.85 < 0.9."""
    prior = ((Q, Fraction(1, 2)), (A, Fraction(85, 100)), (3, Fraction(1, 2)))
    st = and_state(known=((C, True),), actions=("ASK_D",), decoy=True,
                   rule=PosteriorThreshold(Fraction(9, 10)), prior=prior)
    bf = BruteForce(st)
    assert bf.plan_sufficient(()) is True
    assert bf.plan_sufficient(("ASK_D",)) is False   # D = false lowers P(A) below 0.9
    assert probability.plan_sufficient(st, ("ASK_D",)) is False


def test_uncomputed_value_is_worst_case():
    """C is not random: until computed, both values count, so the decision is not justified."""
    prior = ((Q, Fraction(1, 2)), (A, Fraction(999, 1000)), (3, Fraction(1, 2)))
    st = and_state(rule=PosteriorThreshold(Fraction(9, 10)), prior=prior)
    assert probability.decision_ok(st) is False
    assert probability.plan_sufficient(st, ("COMPUTE_C",)) is True


def test_solver_matches_brute_on_hand_cases():
    for st in (and_state(), and_state(known=((C, True),)), and_state(actions=("COMPUTE_C",)),
               and_state(known=((C, True),), actions=("ASK_A", "ASK_D"), decoy=True)):
        assert solver.analyze(st).key() == BruteForce(st).analyze().key()
