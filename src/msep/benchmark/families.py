"""Benchmark families: one base scenario, eleven matched static siblings.

Base theory (shared by every sibling of a family):

    q  <->  [not] OP( l(w1), l(w2), B )        OP in {and, or}
    B   =   l(c1)  or  OP_c( l(c1), l(c2) )
    wa <->  w1                                 alias: another way to learn w1
    dw  ->  l*(w1)                             decoy: pins w1 only if dw is true
    dc  ->  l*(c1)                             decoy: pins c1 only if dc is true
    z1 -> z2, zc1 -> zc2, z3 -> zc3            distractors: same rule shapes, disconnected from q

w*, dw, wa, z* are world variables; c*, dc, zc* are computed variables (each
has a certified task: code execution, a primality test, a SAT solver
run or an exact posterior; see world/certified_tasks.py). l(x) is x or not x.
The latent world makes every requirement "non-dominating" for OP (true under
and, false under or), so no single requirement settles q on its own in the
actual world.

The eleven siblings change only what is known and which actions are offered.
Every label is computed by the oracle; a family is kept only if each sibling
has the intended property (checked in `_accept`), otherwise the base is
resampled. The order-matters family is deferred to Level 4 (conditional plans).
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.oracle import minimal_plan
from msep.oracle.sufficiency import ResourceClass, expost_sufficient
from msep.world.certified_tasks import CERTIFIED_KINDS, make_certified_task
from msep.world.constraints import And, Formula, Iff, Implies, Not, Or, evaluate, lit
from msep.world.state import FormalState, Instance, LatentWorld, Rule, Variable, VarKind

from .counterfactuals import describe_knowledge, set_known, set_menu

SIBLING_TYPES = (
    "ALREADY_SUFFICIENT",
    "INFORMATION_ONLY",
    "COMPUTATION_ONLY",
    "BOTH",
    "NEITHER",
    "RELEVANT_INSUFFICIENT_INFORMATION",
    "RELEVANT_INSUFFICIENT_COMPUTATION",
    "SUFFICIENT_NON_MINIMAL",
    "MULTIPLE_PLANS_DIFFERENT_COSTS",
    "PREMATURE_STOP",
    "UNNECESSARY_EXTRA_ACTION",
)


@dataclass
class Sibling:
    sibling_type: str
    instance: Instance
    transformation: str
    oracle: minimal_plan.OracleResult
    notes: dict = field(default_factory=dict)


@dataclass
class Family:
    family_id: str
    seed: int
    base_params: dict
    siblings: list[Sibling]
    attempts: int


# -- base scenario -------------------------------------------------------------

class _Base:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.op_and = rng.random() < 0.5
        nd = self.op_and  # non-dominating value of a requirement under OP
        self.n_c = rng.choice((1, 2))
        names = (["q", "w1", "w2", "c1"] + (["c2"] if self.n_c == 2 else [])
                 + ["wa", "dw", "dc", "z1", "z2", "z3", "zc1", "zc2", "zc3"])
        kinds = {"q": VarKind.WORLD, "w1": VarKind.WORLD, "w2": VarKind.WORLD, "wa": VarKind.WORLD,
                 "dw": VarKind.WORLD, "z1": VarKind.WORLD, "z2": VarKind.WORLD, "z3": VarKind.WORLD}
        self.idx = {n: i for i, n in enumerate(names)}
        self.variables = tuple(Variable(n, kinds.get(n, VarKind.COMPUTED)) for n in names)
        I = self.idx
        # latent values
        val: dict[int, bool] = {}
        self.sign = {}
        for w in ("w1", "w2"):
            s = rng.random() < 0.5
            self.sign[w] = s
            val[I[w]] = nd if s else not nd  # literal value = nd
        if self.n_c == 1:
            s = rng.random() < 0.5
            self.sign["c1"] = s
            val[I["c1"]] = nd if s else not nd
            b_formula: Formula = lit(I["c1"], s)
            self.op_c_and = None
        else:
            self.op_c_and = rng.random() < 0.5
            for c in ("c1", "c2"):
                self.sign[c] = rng.random() < 0.5
            # choose c values so that op_c(lits) == nd
            while True:
                lv = {c: rng.random() < 0.5 for c in ("c1", "c2")}
                b = all(lv.values()) if self.op_c_and else any(lv.values())
                if b == nd:
                    break
            for c in ("c1", "c2"):
                val[I[c]] = lv[c] if self.sign[c] else not lv[c]
            parts = tuple(lit(I[c], self.sign[c]) for c in ("c1", "c2"))
            b_formula = And(parts) if self.op_c_and else Or(parts)
        body_parts = (lit(I["w1"], self.sign["w1"]), lit(I["w2"], self.sign["w2"]), b_formula)
        body: Formula = And(body_parts) if self.op_and else Or(body_parts)
        self.q_negated = rng.random() < 0.5
        if self.q_negated:
            body = Not(body)
        val[I["wa"]] = val[I["w1"]]
        val[I["dw"]] = rng.random() < 0.5
        for z in ("z1", "z2", "z3"):
            val[I[z]] = rng.random() < 0.5
        task_kinds = CERTIFIED_KINDS
        comp_names = ["c1"] + (["c2"] if self.n_c == 2 else []) + ["dc", "zc1", "zc2", "zc3"]
        tasks = {}
        for c in comp_names:
            if c in ("dc", "zc1", "zc2", "zc3"):
                v = rng.random() < 0.5
            else:
                v = val[I[c]]
            tasks[I[c]] = make_certified_task(rng, v, rng.choice(task_kinds))
        for c in ("dc", "zc1", "zc2", "zc3"):
            val[I[c]] = tasks[I[c]].evaluate()
        val[I["q"]] = evaluate(body, val)
        # Distractors (v2, 2026-11-04): two world and two computed variables, linked to each
        # other by rules of the same shape as the decoys but disconnected from q, so that
        # "unknown variable with a rule" is not a cue for relevance.
        self.rules = (
            Rule("R_target", Iff(lit(I["q"]), body)),
            Rule("R_alias", Iff(lit(I["wa"]), lit(I["w1"]))),
            Rule("R_decoy_info", Implies(lit(I["dw"]), lit(I["w1"], val[I["w1"]]))),
            Rule("R_decoy_comp", Implies(lit(I["dc"]), lit(I["c1"], val[I["c1"]]))),
            Rule("R_distractor_info", Implies(lit(I["z1"], rng.random() < 0.5), lit(I["z2"], val[I["z2"]]))),
            Rule("R_distractor_comp", Implies(lit(I["zc1"], rng.random() < 0.5), lit(I["zc2"], val[I["zc2"]]))),
            Rule("R_distractor_mixed", Implies(lit(I["z3"], rng.random() < 0.5), lit(I["zc3"], val[I["zc3"]]))),
        )
        self.sib_seed = rng.randrange(2 ** 32)
        for r in self.rules:
            assert evaluate(r.formula, val), r.name
        self.tasks = tasks
        self.values = val
        # costs
        c_w1 = rng.choice((2, 3))
        c_alias = rng.choice((1, c_w1 + 2))
        self.cost = {"ASK_w1": c_w1, "ASK_w2": rng.choice((1, 2, 3)), "ASK_wa": c_alias,
                     "ASK_dw": 1, "COMPUTE_dc": 1}
        for d in ("z1", "z2", "z3"):
            self.cost[f"ASK_{d}"] = rng.choice((1, 2, 3))
        for d in ("zc1", "zc2", "zc3"):
            self.cost[f"COMPUTE_{d}"] = rng.choice((1, 2, 3))
        for c in ("c1", "c2")[: self.n_c]:
            self.cost[f"COMPUTE_{c}"] = rng.choice((2, 3)) if c == "c1" else rng.choice((1, 2, 3))
        w_req = self.cost["ASK_w1"] + self.cost["ASK_w2"]
        c_req = sum(self.cost[f"COMPUTE_{c}"] for c in ("c1", "c2")[: self.n_c])
        self.cost["ASK_REPORT"] = w_req + 2
        self.cost["COMPUTE_ALL"] = c_req + 2
        world_vals = tuple(sorted((i, v) for i, v in val.items() if self.variables[i].kind is VarKind.WORLD))
        state = FormalState(variables=self.variables, rules=self.rules, target=I["q"],
                            compute_tasks=tuple(sorted(tasks.items())))
        self.instance = Instance(state, LatentWorld(world_vals))

    def ask(self, name: str) -> InformationAction:
        return InformationAction(f"ASK_{name}", (self.idx[name],), self.cost[f"ASK_{name}"])

    def compute(self, name: str) -> ComputationAction:
        return ComputationAction(f"COMPUTE_{name}", (self.idx[name],), self.cost[f"COMPUTE_{name}"])

    @property
    def cs(self) -> list[str]:
        return ["c1", "c2"][: self.n_c]

    def params(self) -> dict:
        return {"op": "and" if self.op_and else "or", "n_computed_requirements": self.n_c,
                "op_c": None if self.op_c_and is None else ("and" if self.op_c_and else "or"),
                "q_negated": self.q_negated, "signs": self.sign, "costs": self.cost}


def _menu_state(base: _Base, known: list[str], menu: list) -> tuple[FormalState, Instance]:
    st = set_known(base.instance, [base.idx[k] for k in known])
    st = set_menu(st, menu)
    return st, Instance(st, base.instance.world)


DISTRACTORS = ("z1", "z2", "z3", "zc1", "zc2", "zc3")


def _build(base: _Base) -> list[tuple[str, Instance, str, dict]]:
    """(sibling_type, instance, transformation, notes) for all eleven siblings.

    v2 (2026-11-04), after the shortcut audit: menus and knowledge no longer have a
    fixed composition per sibling type. In every sibling, independently of its type,
    (a) actions on already-known requirements are offered at random (each with
    probability 1/2), (b) each of six distractor variables (three world, three
    computed) is known with probability 1/2 and has an action offered with
    probability 1/2, and (c) a decoy whose true value is false is shown as known
    with probability 1/2 (except where it is the sibling's trap). The randomness is seeded
    per family and sibling type."""
    b = base
    out = []
    reqs = ["w1", "w2", *b.cs]

    def act(name):
        return b.ask(name) if b.variables[b.idx[name]].kind is VarKind.WORLD else b.compute(name)

    def add(t, known, core, text, notes=None, redundant="random"):
        srng = random.Random(f"{b.sib_seed}:{t}")
        notes = dict(notes or {})
        known_reqs = [r for r in reqs if r in known]
        if redundant == "all":
            red = list(known_reqs)
        else:
            red = [r for r in known_reqs if srng.random() < 0.5]
            if redundant == "not_all" and known_reqs and len(red) == len(known_reqs):
                red.remove(srng.choice(red))
        menu = list(core) + [act(r) for r in red]
        dknown = []
        for d in DISTRACTORS:
            if srng.random() < 0.5:
                dknown.append(d)
            if srng.random() < 0.5:
                menu.append(act(d))
        # A decoy whose true value is false carries no information about the requirement it
        # points to, so knowing it cannot change the class. Show it as known at random,
        # except in siblings whose trap is that decoy.
        for d in ("dw", "dc"):
            if not b.values[b.idx[d]] and notes.get("decoy") not in (f"ASK_{d}", f"COMPUTE_{d}") \
                    and srng.random() < 0.5:
                dknown.append(d)
        notes["redundant_offered"] = [act(r).name for r in red]
        _, inst = _menu_state(b, list(known) + dknown, menu)
        out.append((t, inst, text, notes))

    comp_req = [b.compute(c) for c in b.cs]
    add("ALREADY_SUFFICIENT", reqs, [],
        "All requirements already known; any offered action is redundant or irrelevant.")
    add("INFORMATION_ONLY", ["w2", *b.cs], [b.ask("w1")],
        "w2 and the computed requirements are known; only w1 is open.", redundant="not_all")
    add("COMPUTATION_ONLY", ["w1", "w2"], comp_req,
        "w1 and w2 are known; only the computed requirements are open.")
    add("BOTH", ["w2"], [b.ask("w1"), *comp_req],
        "w1 and the computed requirements are open; one of each kind is required.")
    neither_side = b.rng.choice(("information", "computation"))
    if neither_side == "information":
        add("NEITHER", ["w2"], [b.ask("dw"), *comp_req],
            "BOTH state with ASK_w1 removed; only the one-way decoy ASK_dw bears on w1.",
            {"neither_side": "information", "decoy": "ASK_dw"})
    else:
        add("NEITHER", ["w2"], [b.ask("w1"), b.compute("dc"), *[b.compute(c) for c in b.cs if c != "c1"]],
            "BOTH state with COMPUTE_c1 removed; only the one-way decoy COMPUTE_dc bears on c1.",
            {"neither_side": "computation", "decoy": "COMPUTE_dc"})
    add("RELEVANT_INSUFFICIENT_INFORMATION", ["w2", *b.cs], [b.ask("w1"), b.ask("dw")],
        "INFORMATION_ONLY plus a cheaper decoy ASK_dw that settles w1 only if dw is true.",
        {"decoy": "ASK_dw"})
    add("RELEVANT_INSUFFICIENT_COMPUTATION", ["w1", "w2"], [*comp_req, b.compute("dc")],
        "COMPUTATION_ONLY plus a cheaper decoy COMPUTE_dc that settles c1 only if dc is true.",
        {"decoy": "COMPUTE_dc"})
    report = InformationAction("ASK_REPORT", (b.idx["w1"], b.idx["w2"], b.idx["z1"]), b.cost["ASK_REPORT"])
    batch = ComputationAction("COMPUTE_ALL", tuple(b.idx[c] for c in (*b.cs, "zc1")), b.cost["COMPUTE_ALL"])
    add("SUFFICIENT_NON_MINIMAL", ["w2"], [b.ask("w1"), *comp_req, report, batch],
        "BOTH plus bulk actions (ASK_REPORT, COMPUTE_ALL) that are sufficient but cost more.",
        {"bulk_actions": ["ASK_REPORT", "COMPUTE_ALL"]})
    add("MULTIPLE_PLANS_DIFFERENT_COSTS", ["w2", *b.cs], [b.ask("w1"), b.ask("wa")],
        "INFORMATION_ONLY plus ASK_wa (wa is equivalent to w1) at a different cost.",
        {"alternatives": ["ASK_w1", "ASK_wa"]})
    add("PREMATURE_STOP", list(b.cs), [b.ask("w1"), b.ask("w2")],
        "Both w1 and w2 are open. Either answer alone could settle q in some outcome, "
        "but in the actual world neither does.")
    add("UNNECESSARY_EXTRA_ACTION", ["w2", *b.cs], [b.ask("w1")],
        "INFORMATION_ONLY with every already-known requirement also offered (ASK_w2, COMPUTE_c*).",
        {"redundant": ["ASK_w2", *[f"COMPUTE_{c}" for c in b.cs]]}, redundant="all")
    return out


# -- acceptance checks (all against the oracle) -----------------------------------

def _role(res: minimal_plan.OracleResult, name: str):
    return next(r for r in res.actions if r.name == name)


def _accept(t: str, inst: Instance, res: minimal_plan.OracleResult, notes: dict) -> str | None:
    """None if the sibling has its intended property, else the reason it does not."""
    rc = res.resource_class
    inv = res.necessity.get("class_cost_invariant")
    a = res.analysis
    want = {
        "ALREADY_SUFFICIENT": ResourceClass.ALREADY_SUFFICIENT,
        "INFORMATION_ONLY": ResourceClass.INFORMATION_ONLY,
        "COMPUTATION_ONLY": ResourceClass.COMPUTATION_ONLY,
        "BOTH": ResourceClass.BOTH,
        "NEITHER": ResourceClass.NEITHER,
        "RELEVANT_INSUFFICIENT_INFORMATION": ResourceClass.INFORMATION_ONLY,
        "RELEVANT_INSUFFICIENT_COMPUTATION": ResourceClass.COMPUTATION_ONLY,
        "SUFFICIENT_NON_MINIMAL": ResourceClass.BOTH,
        "MULTIPLE_PLANS_DIFFERENT_COSTS": ResourceClass.INFORMATION_ONLY,
        "PREMATURE_STOP": ResourceClass.INFORMATION_ONLY,
        "UNNECESSARY_EXTRA_ACTION": ResourceClass.INFORMATION_ONLY,
    }[t]
    if rc is not want:
        return f"class {rc.value}, wanted {want.value}"
    if t in ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH") and inv is not True:
        return "class depends on costs"
    if t == "BOTH" and not (res.necessity["information_necessary"] and res.necessity["computation_necessary"]):
        return "BOTH but one resource is avoidable"
    if t == "NEITHER" and not _role(res, notes["decoy"]).relevant:
        return "NEITHER decoy is not relevant"
    if t.startswith("RELEVANT_INSUFFICIENT"):
        r = _role(res, notes["decoy"])
        if r.category != "relevant_insufficient" or r.alone_sufficient:
            return f"decoy category {r.category}"
    if t == "SUFFICIENT_NON_MINIMAL":
        if not any(_role(res, n).category == "dominated" for n in notes["bulk_actions"]):
            return "no bulk action is a dominated (sufficient, non-optimal) choice"
    if t == "MULTIPLE_PLANS_DIFFERENT_COSTS":
        costs = {sum(inst.state.action_index[x].cost for x in p) for p in a.minimal_plans}
        if len(a.minimal_plans) < 2 or len(costs) < 2:
            return "no two sufficient plans with different costs"
    if t == "PREMATURE_STOP":
        plan = a.optimal_plans[0]
        if len(plan) < 2:
            return "optimal plan has one action"
        for name in plan:
            if expost_sufficient(inst, [name]):
                return f"{name} alone settles q in the actual world"
        if not any(_settles_in_some_outcome(inst.state, name) for name in plan):
            return "no single action could ever settle q"
    if t == "UNNECESSARY_EXTRA_ACTION":
        for n in notes["redundant"]:
            r = _role(res, n)
            if not r.already_known or r.category != "irrelevant":
                return f"{n} is not a redundant extra action"
    return None


def _settles_in_some_outcome(state: FormalState, name: str) -> bool:
    from msep.oracle.logic import SingleSolver
    a = state.action_index[name]
    s = SingleSolver(state)
    try:
        for v in a.reveals:
            for val in (False, True):
                if s.consistent({v: val}) and s.determined(state.target, {v: val}):
                    return True
        return False
    finally:
        s.close()


# -- public API -----------------------------------------------------------------

def family_id_for(seed: int) -> str:
    return "F" + hashlib.sha256(f"msep-family-{seed}".encode()).hexdigest()[:10]


def generate_family(seed: int, max_attempts: int = 50) -> Family:
    rejections: list[str] = []
    for attempt in range(max_attempts):
        rng = random.Random(f"{seed}:{attempt}")
        base = _Base(rng)
        sibs = []
        ok = True
        for t, inst, text, notes in _build(base):
            res = minimal_plan.solve(inst.state)
            why = _accept(t, inst, res, notes)
            if why is not None:
                rejections.append(f"attempt {attempt}: {t}: {why}")
                ok = False
                break
            sibs.append(Sibling(t, inst, f"{text} ({describe_knowledge(inst.state)})", res, notes))
        if ok:
            params = base.params()
            params["rejections"] = rejections
            return Family(family_id_for(seed), seed, params, sibs, attempt + 1)
    raise RuntimeError(f"family {seed}: no acceptable base in {max_attempts} attempts: {rejections[-3:]}")
