"""Template v3: structurally diverse families found by unbiased sampling.

Why: in templates v1/v2 the target rule always lists every requirement directly,
so "act on the unknown variables in Q's rule" is a near-perfect shallow strategy.
v3 draws random theories from several motifs:

    and/or trees        q <-> op(op(..), ..)
    parity              q <-> (a xor b) ...
    threshold           q <-> at least 2 of {a, b, c}
    case split          q <-> (s and A) or (not s and B)        (which input matters depends on s)
    indirection         a <-> op(u1, u2), a has no action          (must act on u1, u2)
    bridges             x -> y, (x and z) -> y among inputs        (an unknown input can be entailed)
    mixed routes        w <-> c, a world fact equivalent to a computed one
    bulk actions        one action reveals several inputs, cheaper or dearer than the parts
    decoys, distractors as in v2

Siblings are NOT built per class. Knowledge states and menus are drawn from ONE
distribution, identical for every class; the oracle labels each draw and draws
are binned by class. A family is kept when every core class (ALREADY_SUFFICIENT,
INFORMATION_ONLY, COMPUTATION_ONLY, BOTH, NEITHER) has a draw; optional trap
siblings (relevant-but-insufficient decoy, dominated alternative, premature stop)
are added when a draw has that property. Selection uses oracle labels only,
never any agent's behaviour.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.oracle import minimal_plan, solver
from msep.oracle.sufficiency import ResourceClass, expost_sufficient
from msep.world.certified_tasks import CERTIFIED_KINDS, make_certified_task
from msep.world.constraints import And, Formula, Iff, Implies, Not, Or, evaluate, lit
from msep.world.state import FormalState, Instance, LatentWorld, Rule, Variable, VarKind

from .families import Family, Sibling, family_id_for

CORE = ("ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER")
MOTIFS = ("and_or", "parity", "threshold", "case_split")


@dataclass
class Theory:
    variables: list[Variable]
    rules: list[Rule]
    values: dict[int, bool]
    tasks: dict
    actions: list
    motif: str
    features: dict = field(default_factory=dict)
    target: int = 0
    knowable: list[int] = field(default_factory=list)  # variables that may be shown as known


def _xor(a: Formula, b: Formula) -> Formula:
    return Iff(a, Not(b))


class _Builder:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.variables: list[Variable] = []
        self.values: dict[int, bool] = {}
        self.rules: list[Rule] = []
        self.tasks: dict = {}

    def var(self, name: str, kind: VarKind, value: bool | None = None) -> int:
        i = len(self.variables)
        self.variables.append(Variable(name, kind))
        if kind is VarKind.COMPUTED:
            v = self.rng.random() < 0.5 if value is None else value
            self.tasks[i] = make_certified_task(self.rng, v, self.rng.choice(CERTIFIED_KINDS), version=2)
            self.values[i] = self.tasks[i].evaluate()
        else:
            self.values[i] = self.rng.random() < 0.5 if value is None else value
        return i

    def rule(self, name: str, f: Formula) -> None:
        assert evaluate(f, self.values), name
        self.rules.append(Rule(name, f))

    def lit(self, i: int) -> Formula:
        return lit(i, self.rng.random() < 0.5)

    def implication(self, name: str, x: int, y: int) -> None:
        """x -> y with both literal signs random. The rule is made true by adjusting the
        antecedent (never by copying y's true value into the consequent), so the rule's
        text does not systematically reveal y's latent or certified value."""
        sy = self.rng.random() < 0.5
        sx = self.rng.random() < 0.5
        if self.values[y] != sy and self.values[x] == sx:  # consequent false and antecedent true: flip antecedent
            sx = not sx
        self.rule(name, Implies(lit(x, sx), lit(y, sy)))


def sample_theory(rng: random.Random) -> Theory:
    b = _Builder(rng)
    q = b.var("q", VarKind.WORLD)
    motif = rng.choice(MOTIFS)
    n_in = {"and_or": rng.randint(3, 4), "parity": 3, "threshold": 3, "case_split": 3}[motif]
    kinds = [VarKind.WORLD, VarKind.COMPUTED] + [rng.choice((VarKind.WORLD, VarKind.COMPUTED)) for _ in range(n_in - 2)]
    rng.shuffle(kinds)
    inputs = [b.var(f"i{k + 1}", kd) for k, kd in enumerate(kinds)]
    features = {"motif": motif, "n_inputs": n_in}

    # indirection: one input becomes a defined node over two new leaves (no action on the node)
    leaves = list(inputs)
    if rng.random() < 0.4:
        node = rng.choice(inputs)
        u = [b.var(f"u{k + 1}", rng.choice((VarKind.WORLD, VarKind.COMPUTED))) for k in range(2)]
        op = And if rng.random() < 0.5 else Or
        # choose the node's value from its definition, keeping the node a world variable
        body = op((b.lit(u[0]), b.lit(u[1])))
        b.values[node] = evaluate(body, b.values)
        if b.variables[node].kind is VarKind.COMPUTED:  # a defined node has no task: make it a world node
            b.variables[node] = Variable(b.variables[node].name, VarKind.WORLD)
            del b.tasks[node]
        b.rule("R_indirection", Iff(lit(node), body))
        leaves = [x for x in inputs if x != node] + u
        features["indirection"] = True

    ins = [b.lit(i) for i in inputs]
    if motif == "and_or":
        inner = (And if rng.random() < 0.5 else Or)(tuple(ins[:2]))
        body = (And if rng.random() < 0.5 else Or)((inner, *ins[2:]))
    elif motif == "parity":
        body = And((_xor(ins[0], ins[1]), ins[2])) if rng.random() < 0.5 else _xor(_xor(ins[0], ins[1]), ins[2])
    elif motif == "threshold":
        a, c, d = ins
        body = Or((And((a, c)), And((a, d)), And((c, d))))
    else:
        s, a, c = ins
        body = Or((And((s, a)), And((Not(s), c))))
    if rng.random() < 0.5:
        body = Not(body)
    b.values[q] = evaluate(body, b.values)
    b.rule("R_target", Iff(lit(q), body))

    # bridges among leaves: x -> y with y's true literal (always true in the latent world)
    for k in range(rng.randint(0, 2)):
        x, y = rng.sample(leaves, 2)
        b.implication(f"R_bridge{k + 1}", x, y)
    # mixed route: a world fact equivalent to a computed leaf (or the reverse)
    if rng.random() < 0.3:
        src = rng.choice(leaves)
        other = VarKind.WORLD if b.variables[src].kind is VarKind.COMPUTED else VarKind.COMPUTED
        m = b.var("m1", other, value=b.values[src])
        b.rule("R_mixed", Iff(lit(m), lit(src)))
        leaves.append(m)
        features["mixed_route"] = True
    # decoys: one-way implications into a leaf
    decoys = []
    for k in range(rng.randint(1, 2)):
        target = rng.choice(leaves)
        d = b.var(f"d{k + 1}", rng.choice((VarKind.WORLD, VarKind.COMPUTED)))
        b.implication(f"R_decoy{k + 1}", d, target)
        decoys.append(d)
    # distractors with same-shaped rules, disconnected from q
    dist = [b.var(f"z{k + 1}", rng.choice((VarKind.WORLD, VarKind.COMPUTED))) for k in range(rng.randint(2, 4))]
    for k in range(len(dist) - 1):
        b.implication(f"R_dist{k + 1}", dist[k], dist[k + 1])

    # actions
    def single(i):
        name = b.variables[i].name
        cost = rng.randint(1, 4)
        if b.variables[i].kind is VarKind.WORLD:
            return InformationAction(f"ASK_{name}", (i,), cost)
        return ComputationAction(f"COMPUTE_{name}", (i,), cost)

    acts = [single(i) for i in leaves + decoys + dist]
    for kind, cls, label in ((VarKind.WORLD, InformationAction, "ASK_BULK"), (VarKind.COMPUTED, ComputationAction, "COMPUTE_BULK")):
        pool = [i for i in leaves if b.variables[i].kind is kind]
        if len(pool) >= 2 and rng.random() < 0.5:
            pick = tuple(sorted(rng.sample(pool, 2)))
            parts = sum(a.cost for a in acts if a.reveals in ((pick[0],), (pick[1],)))
            acts.append(cls(label, pick, max(1, parts + rng.choice((-1, 1, 2)))))
            features[f"bulk_{kind.value}"] = True
    knowable = [i for i in range(len(b.variables)) if i != q]
    return Theory(b.variables, b.rules, b.values, b.tasks, acts, motif, features, q, knowable)


def _draw_state(th: Theory, rng: random.Random) -> FormalState:
    """One knowledge state + menu from the single, class-independent distribution."""
    p_known = rng.choice((0.25, 0.4, 0.55))
    known = [i for i in th.knowable if rng.random() < p_known]
    menu = [a for a in th.actions if rng.random() < 0.85]
    ev = tuple(sorted((i, th.values[i]) for i in known if th.variables[i].kind is VarKind.WORLD))
    cp = tuple(sorted((i, th.values[i]) for i in known if th.variables[i].kind is VarKind.COMPUTED))
    return FormalState(variables=tuple(th.variables), rules=tuple(th.rules), target=th.target, evidence=ev, computed=cp,
                       info_actions=tuple(a for a in menu if isinstance(a, InformationAction)),
                       comp_actions=tuple(a for a in menu if isinstance(a, ComputationAction)),
                       compute_tasks=tuple(sorted(th.tasks.items())))


def _quick_label(st: FormalState) -> str | None:
    a = solver.analyze(st)
    rc = a.resource_class(st)
    if rc is ResourceClass.AMBIGUOUS:
        return None
    if rc.value in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH"):
        nec = a.necessity(st)
        if nec["class_cost_invariant"] is not True:
            return None
        if rc is ResourceClass.BOTH and not (nec["information_necessary"] and nec["computation_necessary"]):
            return None
    return rc.value


def _trap_types(inst: Instance, res) -> list[tuple[str, dict]]:
    out = []
    rc = res.resource_class.value
    if rc not in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH"):
        return out
    roles = {r.name: r for r in res.actions}
    decoys = [r for r in res.actions if r.category == "relevant_insufficient" and not r.alone_sufficient]
    if decoys:
        d = decoys[0]
        t = "RELEVANT_INSUFFICIENT_INFORMATION" if d.resource == "information" else "RELEVANT_INSUFFICIENT_COMPUTATION"
        out.append((t, {"decoy": d.name}))
    dom = [r.name for r in res.actions if r.category == "dominated"]
    if dom:
        out.append(("SUFFICIENT_NON_MINIMAL", {"bulk_actions": dom}))
    plan = res.analysis.optimal_plans[0]
    if len(plan) >= 2 and not any(expost_sufficient(inst, [a]) for a in plan):
        out.append(("PREMATURE_STOP", {}))
    del roles
    return out


def generate_family_v3(seed: int, max_theories: int = 40, draws_per_theory: int = 160) -> Family:
    rejections = []
    for attempt in range(max_theories):
        rng = random.Random(f"v3:{seed}:{attempt}")
        th = sample_theory(rng)
        world = LatentWorld(tuple(sorted((i, v) for i, v in th.values.items() if th.variables[i].kind is VarKind.WORLD)))
        bins: dict[str, FormalState] = {}
        resolvable: list[FormalState] = []
        seen = set()
        for _ in range(draws_per_theory):
            st = _draw_state(th, rng)
            key = (st.known.items().__repr__(), tuple(a.name for a in st.actions))
            if key in seen:
                continue
            seen.add(key)
            lab = _quick_label(st)
            if lab is None:
                continue
            if lab not in bins:
                bins[lab] = st
            elif lab in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH") and len(resolvable) < 12:
                resolvable.append(st)
            if len(bins) == len(CORE) and len(resolvable) >= 6:
                break
        if len(bins) < len(CORE):
            rejections.append(f"theory {attempt} ({th.motif}): bins {sorted(bins)}")
            continue
        sibs = []
        for t in CORE:
            inst = Instance(bins[t], world)
            res = minimal_plan.solve(inst.state)
            assert res.resource_class.value == t
            notes = {"template": "v3", "motif": th.motif, **th.features}
            if t == "NEITHER":
                rel = [r.name for r in res.actions if r.relevant]
                notes["decoy"] = rel[0] if rel else None
            sibs.append(Sibling(t, inst, f"v3 {th.motif}: class {t} drawn from the shared state distribution", res, notes))
        found = set()
        for st in [bins[c] for c in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH")] + resolvable:
            inst = Instance(st, world)
            res = minimal_plan.solve(st)
            for t, extra in _trap_types(inst, res):
                if t in found:
                    continue
                if any(s.instance.state == st for s in sibs):
                    continue  # do not duplicate a core sibling's formal state
                found.add(t)
                sibs.append(Sibling(t, inst, f"v3 {th.motif}: draw with property {t}", res,
                                    {"template": "v3", "motif": th.motif, **th.features, **extra}))
        params = {"template": "v3", "motif": th.motif, **th.features, "rejections": rejections}
        return Family(family_id_for(seed).replace("F", "G", 1), seed, params, sibs, attempt + 1)
    raise RuntimeError(f"v3 family {seed}: no theory filled all core classes: {rejections[-3:]}")
