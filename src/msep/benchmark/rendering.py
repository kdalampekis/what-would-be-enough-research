"""Natural-language rendering of a formal state. Downstream of the formal layer.

Nothing here is read by any oracle. Variables and actions get neutral display
names (F1..., K1..., Q) assigned by a per-family random permutation, so the
internal role names (w1, dw, wa, ...) never reach the model. The mapping is
stored with each instance so model outputs can be translated back.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from msep.actions.base import Resource
from msep.world.constraints import render
from msep.world.state import FormalState, LogicalEntailment, VarKind

SKINS = {
    "warehouse": {
        "target": "the order can ship today",
        "facts": ["the customs form is signed", "the forklift inspection passed", "the courier slot is confirmed",
                  "the pallet was weighed", "the supplier invoice arrived", "the dock door is free",
                  "the label printer is online", "the night shift is staffed"],
    },
    "lab": {
        "target": "the experiment run is approved",
        "facts": ["the freezer log was checked", "the safety officer signed off", "the reagent batch arrived",
                  "the centrifuge is calibrated", "the protocol version is current", "the waste bin was emptied",
                  "the backup generator is tested", "the visitor list is closed"],
    },
    "abstract": {
        "target": "Q holds",
        "facts": [f"fact {chr(65 + i)} holds" for i in range(8)],
    },
    # held out: used only for the E12 linguistic-shift variants, never in the main pool
    "harbour": {
        "target": "the vessel may leave the harbour tonight",
        "facts": ["the pilot boat is available", "the cargo manifest is stamped", "the tide gauge was read",
                  "the crew roster is complete", "the fuel receipt is filed", "the berth fee is paid",
                  "the radio check passed", "the weather bulletin was received", "the hull inspection is logged",
                  "the customs seal is intact"],
    },
}
TRAIN_SKINS = ("abstract", "lab", "warehouse")
SHIFT_SKINS = ("harbour",)


@dataclass
class Rendering:
    skin: str
    var_alias: dict[str, str]      # formal name -> display handle
    var_label: dict[str, str]      # display handle -> phrase
    action_alias: dict[str, str]   # formal action name -> display action name
    order_seed: int | None = None  # None: rules sorted by text (pool_v1/v2); else a seeded shuffle per family

    def to_json(self) -> dict:
        d = {"skin": self.skin, "var_alias": self.var_alias, "var_label": self.var_label,
             "action_alias": self.action_alias}
        if self.order_seed is not None:  # omitted when unused, so pool_v1/v2 records are unchanged
            d["order_seed"] = self.order_seed
        return d

    def formal_action(self, display_name: str) -> str | None:
        inv = {v: k for k, v in self.action_alias.items()}
        return inv.get(display_name)


def rendering_from_json(d: dict) -> Rendering:
    return Rendering(d["skin"], dict(d["var_alias"]), dict(d["var_label"]), dict(d.get("action_alias", {})),
                     d.get("order_seed"))


def extend_rendering(r: Rendering, state: FormalState, rng: random.Random) -> Rendering:
    """Add handles for variables the rendering does not know yet (used by counterfactual
    variants that add variables). Existing handles and labels are kept."""
    used = set(r.var_label)
    pool = [f for f in SKINS[r.skin]["facts"] if f not in r.var_label.values()]
    extra_facts = [f"fact {chr(65 + i)}{i} holds" for i in range(20)]
    rng.shuffle(pool)
    out = Rendering(r.skin, dict(r.var_alias), dict(r.var_label), {}, r.order_seed)
    for i, v in enumerate(state.variables):
        if v.name in out.var_alias:
            continue
        prefix = "F" if v.kind is VarKind.WORLD else "K"
        k = 1
        while f"{prefix}{k}" in used:
            k += 1
        h = f"{prefix}{k}"
        used.add(h)
        out.var_alias[v.name] = h
        if v.kind is VarKind.WORLD:
            out.var_label[h] = pool.pop() if pool else extra_facts.pop(0)
        else:
            out.var_label[h] = state.tasks[i].describe()
    return out


def make_rendering(state: FormalState, rng: random.Random, skin: str | None = None,
                   shuffle_rules: bool = False) -> Rendering:
    """Rendering for a whole family: call once per family with the base state."""
    skin = skin or rng.choice(TRAIN_SKINS)
    pool = list(SKINS[skin]["facts"])
    rng.shuffle(pool)
    world = [i for i in state.world_vars() if i != state.target]
    comp = state.computed_vars()
    w_handles = [f"F{k + 1}" for k in range(len(world))]
    c_handles = [f"K{k + 1}" for k in range(len(comp))]
    rng.shuffle(w_handles)
    rng.shuffle(c_handles)
    alias = {state.variables[state.target].name: "Q"}
    label = {"Q": SKINS[skin]["target"]}
    for i, h in zip(world, w_handles):
        alias[state.variables[i].name] = h
        label[h] = pool.pop() if pool else f"condition {h} is met"  # fallback when a skin runs out
    for i, h in zip(comp, c_handles):
        alias[state.variables[i].name] = h
        label[h] = state.tasks[i].describe()
    # The order seed is drawn last, so renderings without shuffling are unchanged from before.
    return Rendering(skin, alias, label, {}, rng.randrange(2 ** 32) if shuffle_rules else None)


def _action_display(state: FormalState, r: Rendering, a) -> str:
    if a.resource is Resource.INFORMATION:
        verb = "ASK"
    elif len(a.reveals) == 1 and hasattr(state.tasks[a.reveals[0]], "verb"):
        verb = state.tasks[a.reveals[0]].verb  # e.g. RUN_SOLVER, EXECUTE_CODE
    else:
        verb = "COMPUTE"
    handles = sorted(r.var_alias[state.variables[v].name] for v in a.reveals)
    return f"{verb}_{'_'.join(handles)}"


def render_state(state: FormalState, r: Rendering) -> str:
    """Neutral description of a state, independent of evaluation mode."""
    v = state.variables
    handle = {i: r.var_alias[x.name] for i, x in enumerate(v)}
    r.action_alias = {a.name: _action_display(state, r, a) for a in state.actions}
    if len(set(r.action_alias.values())) != len(r.action_alias):
        raise ValueError("two actions render to the same display name")
    lines = [f"Decision: is it true that {r.var_label['Q']} (Q)?", ""]
    lines.append("Facts about the world (each is true or false):")
    for i in sorted(state.world_vars(), key=lambda i: handle[i]):
        if i != state.target:
            lines.append(f"  {handle[i]}: {r.var_label[handle[i]]}")
    if state.computed_vars():
        lines.append("Computational facts (each is fully determined by inputs shown here; its certified "
                     "value is not yet known):")
        for i in sorted(state.computed_vars(), key=lambda i: handle[i]):
            lines.append(f"  {handle[i]}: {r.var_label[handle[i]]}")
    lines.append("")
    lines.append("Rules (all of these are true):")
    ordered = sorted(state.rules, key=lambda x: render(x.formula, handle))
    if r.order_seed is not None:  # no positional cue: the rule about Q is not always in the same place
        random.Random(r.order_seed).shuffle(ordered)
    for k, rule in enumerate(ordered, 1):
        lines.append(f"  {k}. {render(rule.formula, handle)}")
    lines.append("")
    known = [f"{handle[i]} is {'true' if val else 'false'}" for i, val in sorted(state.known.items(), key=lambda t: handle[t[0]])]
    lines.append("Known so far: " + ("; ".join(known) if known else "nothing"))
    lines.append("")
    lines.append("Available actions:")
    for a in sorted(state.actions, key=lambda a: r.action_alias[a.name]):
        what = ", ".join(sorted(handle[x] for x in a.reveals))
        kind = "information" if a.resource is Resource.INFORMATION else "computation"
        verb = "find out" if a.resource is Resource.INFORMATION else "run the certified procedure and record"
        lines.append(f"  {r.action_alias[a.name]} ({kind}, cost {a.cost}): {verb} the value of {what}")
    lines.append("")
    if not isinstance(state.decision_rule, LogicalEntailment):
        lines.append("Prior probabilities (independent before the rules are taken into account; the rules then "
                     "rule out impossible combinations):")
        for i, p in sorted(state.prior, key=lambda t: handle[t[0]]):
            if i != state.target:
                lines.append(f"  P({handle[i]} is true) = {p}")
        lines.append("")
    if isinstance(state.decision_rule, LogicalEntailment):
        lines.append("Decision rule: a decision about Q is justified only if it follows with certainty from "
                     "the rules and the known values.")
    else:
        lines.append(f"Decision rule: a decision about Q is justified only if its probability is at least "
                     f"{state.decision_rule.tau}, whatever the not-yet-computed computational facts turn out to be.")
    lines.append("Information actions (ASK_...) are the only way to obtain new evidence about the world. "
                 "Computation actions run a certified procedure (code execution, a primality test, a SAT solver, "
                 "or an exact posterior calculation) on inputs you already have; a computational fact becomes "
                 "part of the decision state only through its certified result, not through an uncertified "
                 "estimate. You are choosing a plan before running anything: actions are chosen together, "
                 "before any result is seen.")
    return "\n".join(lines)
