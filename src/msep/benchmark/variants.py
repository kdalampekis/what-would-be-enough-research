"""Counterfactual variants of benchmark records for E10 (cost), E11 (risk) and E12 (structural shift).

Every variant is derived from one record, keeps its family id and split (so
family-level splitting still holds), is relabelled from scratch by the oracle,
and records what was changed. Nothing here selects variants by how a model
would perform.
"""

from __future__ import annotations

import random
from dataclasses import replace
from fractions import Fraction

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.oracle import minimal_plan
from msep.world.constraints import And, Iff, Not, Or, evaluate, lit
from msep.world.probabilities import PRIOR_CHOICES
from msep.world.state import FormalState, Instance, LatentWorld, PosteriorThreshold, Rule, Variable, VarKind

from .rendering import Rendering, extend_rendering, make_rendering, render_state, rendering_from_json
from .schemas import instance_from_record, instance_record


def _record(src: dict, inst: Instance, tag: str, variant: dict, rendering: Rendering | None = None) -> dict:
    r = rendering or rendering_from_json(src["rendering"])
    text = render_state(inst.state, r)
    res = minimal_plan.solve(inst.state)
    rec = instance_record(family_id=src["family_id"], instance_id=f"{src['instance_id']}-{tag}",
                          sibling_type=src["sibling_type"], split=src["split"], instance=inst, oracle=res,
                          transformation=f"{src['transformation']} | variant: {variant}",
                          rendering={**r.to_json(), "action_alias": dict(r.action_alias)}, prompt_text=text,
                          notes=src.get("notes"))
    rec["variant"] = {"of": src["instance_id"], **variant}
    rec["base_params"] = src.get("base_params")
    return rec


# -- E10: cost sweeps ----------------------------------------------------------------

def with_cost(state: FormalState, action: str, cost: int) -> FormalState:
    info = tuple(replace(a, cost=cost) if a.name == action else a for a in state.info_actions)
    comp = tuple(replace(a, cost=cost) if a.name == action else a for a in state.comp_actions)
    return replace(state, info_actions=info, comp_actions=comp)


COST_SWEEPS = {
    # sibling type -> (action whose cost is swept, competing action)
    "MULTIPLE_PLANS_DIFFERENT_COSTS": ("ASK_wa", "ASK_w1"),
    "SUFFICIENT_NON_MINIMAL": ("ASK_REPORT", "ASK_w1"),
}


def generic_cost_sweep(rec: dict) -> list[dict]:
    """Any template: take a dominated action d (in some minimal sufficient plan, in no optimal
    plan) and sweep its cost around the exact value at which its plan becomes optimal."""
    o = rec["oracle"]
    dom = [a["name"] for a in o["actions"] if a["category"] == "dominated"]
    if not dom or o["optimal_cost"] is None:
        return []
    d = sorted(dom)[0]
    inst = instance_from_record(rec)
    base = inst.state.action_index[d].cost
    best_with_d = min(m["cost"] for m in o["minimal_sufficient_plans"] if d in m["plan"])
    boundary = base - (best_with_d - o["optimal_cost"])  # at this cost d's plan ties the optimum
    rival = sorted({a for p in o["optimal_plans"] for a in p})
    out = []
    for c in sorted({boundary - 1, boundary, boundary + 1, base}):
        if c < 1:
            continue
        st = with_cost(inst.state, d, c)
        out.append(_record(rec, Instance(st, inst.world), f"cost{d}{c}",
                           {"kind": "cost_sweep", "action": d, "rival": "+".join(rival), "cost": c,
                            "boundary_cost": boundary, "relation": "below" if c < boundary else
                            ("equal" if c == boundary else "above")}))
    return out


def cost_sweep(rec: dict) -> list[dict]:
    """Sweep one action's cost across the boundary where the optimal plan should switch.
    The epistemic structure (variables, rules, knowledge, menu) is unchanged."""
    if (rec.get("notes") or {}).get("template") == "v3":
        return generic_cost_sweep(rec)
    if rec["sibling_type"] not in COST_SWEEPS:
        return []
    swept, rival = COST_SWEEPS[rec["sibling_type"]]
    inst = instance_from_record(rec)
    rival_cost = inst.state.action_index[rival].cost
    out = []
    for c in sorted({1, max(1, rival_cost - 1), rival_cost, rival_cost + 1, rival_cost + 3}):
        st = with_cost(inst.state, swept, c)
        out.append(_record(rec, Instance(st, inst.world), f"cost{swept}{c}",
                           {"kind": "cost_sweep", "action": swept, "rival": rival, "cost": c,
                            "rival_cost": rival_cost, "relation": "below" if c < rival_cost else
                            ("equal" if c == rival_cost else "above")}))
    return out


# -- E11: risk (posterior threshold) ----------------------------------------------------

TAUS = (Fraction(3, 5), Fraction(4, 5), Fraction(19, 20), Fraction(1))


def risk_variants(rec: dict, seed: int) -> list[dict]:
    """Same state under the posterior-threshold rule at several thresholds tau.

    tau corresponds to a wrong-answer penalty: with payoff +1 correct, -lam wrong,
    0 defer, answering is worthwhile iff P(correct) >= lam / (1 + lam) = tau.
    Priors on world variables are drawn once per family (seeded) and shown in the
    prompt; the target's prior is 1/2, which cancels because q is defined by a rule."""
    inst = instance_from_record(rec)
    rng = random.Random(f"risk:{rec['family_id']}:{seed}")
    prior = tuple((i, Fraction(1, 2) if i == inst.state.target else rng.choice(PRIOR_CHOICES))
                  for i in inst.state.world_vars())
    out = []
    for tau in TAUS:
        st = replace(inst.state, decision_rule=PosteriorThreshold(tau), prior=prior)
        lam = None if tau == 1 else tau / (1 - tau)
        out.append(_record(rec, Instance(st, inst.world), f"tau{tau.numerator}-{tau.denominator}",
                           {"kind": "risk", "tau": str(tau),
                            "equivalent_wrong_answer_penalty": None if lam is None else str(lam)}))
    return out


# -- E12: structural shift --------------------------------------------------------------

def _target_rule_parts(rec: dict, state: FormalState):
    rule = next(r for r in state.rules if r.name == "R_target")
    body = rule.formula.right
    negated = isinstance(body, Not)
    core = body.arg if negated else body
    return rule, core, negated


def _rebuild_target(state: FormalState, core, negated: bool) -> tuple[Rule, ...]:
    body = Not(core) if negated else core
    q = state.target
    return tuple(Rule("R_target", Iff(lit(q), body)) if r.name == "R_target" else r for r in state.rules)


def _extend(state: FormalState, world: LatentWorld, new_vars: list[tuple[str, bool]]):
    """Append world variables (name, latent value)."""
    variables = list(state.variables)
    wv = dict(world.values)
    idx = {}
    for name, val in new_vars:
        idx[name] = len(variables)
        variables.append(Variable(name, VarKind.WORLD))
        wv[idx[name]] = val
    return tuple(variables), LatentWorld(tuple(sorted(wv.items()))), idx


def shift_width(rec: dict) -> dict | None:
    """Add a third world requirement w3 (same role as w1, non-dominating latent value).
    w3 is unknown exactly where w1 is unknown, and ASK_w3 is offered wherever ASK_w1 is."""
    if (rec.get("notes") or {}).get("template") == "v3":
        return None  # width/depth shifts are defined on the v2 roles only
    inst = instance_from_record(rec)
    st = inst.state
    rule, core, negated = _target_rule_parts(rec, st)
    if not isinstance(core, (And, Or)):
        return None
    is_and = isinstance(core, And)
    nd = is_and
    sign = random.Random(f"w3:{rec['family_id']}").random() < 0.5
    w3_val = nd if sign else not nd
    variables, world, idx = _extend(st, inst.world, [("w3", w3_val)])
    new_core = type(core)((*core.args, lit(idx["w3"], sign)))
    st2 = replace(st, variables=variables, rules=_rebuild_target(st, new_core, negated))
    names = {v.name: i for i, v in enumerate(st.variables)}
    w1 = names["w1"]
    ask_w1 = next((a for a in st.info_actions if a.reveals == (w1,)), None)
    info = list(st2.info_actions)
    if w1 in st.known:
        ev = dict(st2.evidence)
        ev[idx["w3"]] = w3_val
        st2 = replace(st2, evidence=tuple(sorted(ev.items())))
    if ask_w1 is not None:
        info.append(InformationAction("ASK_w3", (idx["w3"],), ask_w1.cost))
    st2 = replace(st2, info_actions=tuple(info))
    inst2 = Instance(st2, world)
    r = extend_rendering(rendering_from_json(rec["rendering"]), st2, random.Random(rec["family_id"]))
    return _record(rec, inst2, "shiftwidth", {"kind": "shift", "axis": "width"}, r)


def shift_depth(rec: dict) -> dict | None:
    """Indirection: w1 can no longer be asked directly. It is defined as u1 AND u2 (or OR,
    matching w1's latent value), and ASK_u1, ASK_u2 replace ASK_w1."""
    if (rec.get("notes") or {}).get("template") == "v3":
        return None
    inst = instance_from_record(rec)
    st = inst.state
    names = {v.name: i for i, v in enumerate(st.variables)}
    w1 = names["w1"]
    ask_w1 = next((a for a in st.info_actions if a.reveals == (w1,)), None)
    if ask_w1 is None or w1 in st.known:
        return None
    w1_val = inst.world.as_dict[w1]
    rng = random.Random(f"depth:{rec['family_id']}")
    use_and = rng.random() < 0.5
    while True:
        u = (rng.random() < 0.5, rng.random() < 0.5)
        if (all(u) if use_and else any(u)) == w1_val:
            break
    variables, world, idx = _extend(st, inst.world, [("u1", u[0]), ("u2", u[1])])
    parts = (lit(idx["u1"]), lit(idx["u2"]))
    rules = (*st.rules, Rule("R_depth", Iff(lit(w1), And(parts) if use_and else Or(parts))))
    info = [a for a in st.info_actions if a.name != ask_w1.name]
    c = max(1, ask_w1.cost - 1)
    info += [InformationAction("ASK_u1", (idx["u1"],), c), InformationAction("ASK_u2", (idx["u2"],), c)]
    st2 = replace(st, variables=variables, rules=rules, info_actions=tuple(info))
    inst2 = Instance(st2, world)
    full = inst2.full_assignment()
    assert all(evaluate(r.formula, full) for r in rules)
    r = extend_rendering(rendering_from_json(rec["rendering"]), st2, random.Random(rec["family_id"]))
    return _record(rec, inst2, "shiftdepth", {"kind": "shift", "axis": "depth"}, r)


def shift_skin(rec: dict) -> dict:
    """Same formal state, rendered with the held-out skin."""
    inst = instance_from_record(rec)
    r = make_rendering(inst.state, random.Random(f"skin:{rec['family_id']}"), skin="harbour",
                       shuffle_rules=bool(rec["rendering"].get("order_seed") is not None))
    return _record(rec, inst, "shiftskin", {"kind": "shift", "axis": "skin"}, r)
