"""Random small formal instances, used to validate the oracles (E0).

The latent world is sampled first; only rules that are true in it are kept, so
every generated instance is consistent by construction. Benchmark families
(structured scenarios with matched siblings) are built in benchmark/families.py.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction

from .compute_tasks import make_task
from .constraints import And, Formula, Iff, Implies, Or, evaluate, lit
from .probabilities import random_prior
from .state import FormalState, Instance, LatentWorld, LogicalEntailment, PosteriorThreshold, Rule, Variable, VarKind

TAUS = (Fraction(2, 3), Fraction(3, 4), Fraction(4, 5), Fraction(9, 10), Fraction(1))


@dataclass(frozen=True)
class RandomConfig:
    min_world: int = 2          # including the target
    max_world: int = 5
    max_computed: int = 3
    max_rules: int = 5
    max_actions: int = 7
    p_posterior: float = 0.25
    p_known: float = 0.25
    task_kinds: tuple[str, ...] = ("divisible", "sum_exceeds")


def _random_formula(rng: random.Random, pool: list[int]) -> Formula:
    k = min(len(pool), rng.choice((2, 2, 3)))
    vs = rng.sample(pool, k)
    lits = [lit(v, rng.random() < 0.5) for v in vs]
    shape = rng.randrange(4)
    if shape == 0:
        return Or(tuple(lits))
    if shape == 1:
        return Implies(And(tuple(lits[:-1])) if len(lits) > 2 else lits[0], lits[-1])
    if shape == 2:
        rest = tuple(lits[1:])
        return Iff(lits[0], rest[0] if len(rest) == 1 else (And(rest) if rng.random() < 0.5 else Or(rest)))
    return Implies(lits[0], Or(tuple(lits[1:])) if len(lits) > 2 else lits[1])


def random_instance(rng: random.Random, cfg: RandomConfig = RandomConfig()) -> Instance:
    n_world = rng.randint(cfg.min_world, cfg.max_world)
    n_comp = rng.randint(0, cfg.max_computed)
    variables = [Variable("q", VarKind.WORLD)]
    variables += [Variable(f"w{i}", VarKind.WORLD) for i in range(1, n_world)]
    variables += [Variable(f"c{i}", VarKind.COMPUTED) for i in range(1, n_comp + 1)]
    n = len(variables)
    world_idx = list(range(n_world))
    comp_idx = list(range(n_world, n))

    world_vals = {i: rng.random() < 0.5 for i in world_idx}
    tasks = {i: make_task(rng, rng.random() < 0.5, rng.choice(cfg.task_kinds)) for i in comp_idx}
    full = {**world_vals, **{i: t.evaluate() for i, t in tasks.items()}}

    rules = []
    pool = list(range(n))
    # Usually define the target from other variables, mixing both kinds when possible,
    # so all resource classes occur often enough to be tested.
    if rng.random() < 0.7 and n > 2:
        others = [i for i in pool if i != 0]
        k = min(len(others), rng.choice((2, 2, 3)))
        picks = rng.sample(others, k)
        if comp_idx and world_idx[1:] and not any(i in comp_idx for i in picks):
            picks[-1] = rng.choice(comp_idx)
        body = tuple(lit(i, full[i] if rng.random() < 0.6 else not full[i]) for i in picks)
        f = Iff(lit(0, True), And(body) if rng.random() < 0.5 else Or(body))
        world_vals[0] = evaluate(f.right, full)  # make q agree with its definition
        full[0] = world_vals[0]
        rules.append(Rule("R1", f))
    for r in range(len(rules), rng.randint(1, cfg.max_rules)):
        for _ in range(50):
            f = _random_formula(rng, pool)
            # bias: most rules mention the target
            if r == 0 and 0 not in _vars(f):
                continue
            if evaluate(f, full):
                rules.append(Rule(f"R{len(rules) + 1}", f))
                break

    evidence = tuple(sorted((i, world_vals[i]) for i in world_idx[1:] if rng.random() < cfg.p_known))
    computed = tuple(sorted((i, full[i]) for i in comp_idx if rng.random() < cfg.p_known))

    info, comp = [], []
    for i in world_idx:
        if rng.random() < (0.15 if i == 0 else 0.7):
            info.append(InformationAction(f"ASK_{variables[i].name}", (i,), rng.randint(1, 3)))
    if len(world_idx) > 2 and rng.random() < 0.3:
        vs = tuple(sorted(rng.sample(world_idx[1:], 2)))
        info.append(InformationAction("ASK_REPORT", vs, rng.randint(2, 4)))
    for i in comp_idx:
        if rng.random() < 0.7:
            comp.append(ComputationAction(f"COMPUTE_{variables[i].name}", (i,), rng.randint(1, 3)))
    if len(comp_idx) >= 2 and rng.random() < 0.25:
        vs = tuple(sorted(rng.sample(comp_idx, 2)))
        comp.append(ComputationAction("COMPUTE_BATCH", vs, rng.randint(2, 4)))
    while len(info) + len(comp) > cfg.max_actions:
        (info if len(info) >= len(comp) else comp).pop(rng.randrange(max(len(info), len(comp))))

    if rng.random() < cfg.p_posterior:
        decision_rule = PosteriorThreshold(rng.choice(TAUS))
        prior = random_prior(rng, world_idx)
    else:
        decision_rule = LogicalEntailment()
        prior = ()
    state = FormalState(
        variables=tuple(variables), rules=tuple(rules), target=0,
        evidence=evidence, computed=computed,
        info_actions=tuple(info), comp_actions=tuple(comp),
        compute_tasks=tuple(sorted(tasks.items())), decision_rule=decision_rule, prior=prior)
    return Instance(state, LatentWorld(tuple(sorted(world_vals.items()))))


def _vars(f: Formula) -> frozenset[int]:
    from .constraints import variables
    return variables(f)
