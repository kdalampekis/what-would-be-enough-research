"""Small hand-built states shared by tests."""

from fractions import Fraction

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.compute_tasks import Divisible
from msep.world.constraints import And, Iff, Implies, lit
from msep.world.state import FormalState, Instance, LatentWorld, LogicalEntailment, PosteriorThreshold, Rule, Variable, VarKind

Q, A, C, D = 0, 1, 2, 3


def and_state(known=(), actions=("ASK_A", "COMPUTE_C"), decoy=False, rule=None, prior=None):
    """q <-> (A and C); A world, C computed (391 = 17*23 is divisible by 17: C true).
    Optional decoy D (world): D -> A."""
    variables = (Variable("q", VarKind.WORLD), Variable("A", VarKind.WORLD), Variable("C", VarKind.COMPUTED),
                 Variable("D", VarKind.WORLD))
    rules = [Rule("R1", Iff(lit(Q), And((lit(A), lit(C)))))]
    if decoy:
        rules.append(Rule("R2", Implies(lit(D), lit(A))))
    menu = {"ASK_A": InformationAction("ASK_A", (A,), 2), "COMPUTE_C": ComputationAction("COMPUTE_C", (C,), 1),
            "ASK_D": InformationAction("ASK_D", (D,), 1), "ASK_q": InformationAction("ASK_q", (Q,), 5)}
    info = tuple(menu[n] for n in actions if n.startswith("ASK"))
    comp = tuple(menu[n] for n in actions if n.startswith("COMPUTE"))
    ev = tuple((i, v) for i, v in known if i != C)
    cp = tuple((i, v) for i, v in known if i == C)
    st = FormalState(variables=variables, rules=tuple(rules), target=Q, evidence=ev, computed=cp,
                     info_actions=info, comp_actions=comp, compute_tasks=((C, Divisible(391, 17)),),
                     decision_rule=rule or LogicalEntailment(),
                     prior=prior or ())
    return st


def and_instance(**kw):
    st = and_state(**kw)
    return Instance(st, LatentWorld(((Q, True), (A, True), (D, True))))
