"""T1 (Challenge Tier v4): single-edit counterfactual intervention flips.

A pair is (A, B). A is a frozen v3 record re-rendered unchanged; B is the same state with exactly one
more variable fixed at its true value:
- E_OBS: a world variable becomes observed evidence (one more observed fact);
- E_CERT: a computed variable gets its certified result (one more certified computation).
Rules, latent world, action menu, costs and rendering are identical, so the two prompts differ only in
the line(s) that state what is known. Both members are labelled from scratch by the exact oracle, and a
pair is kept only if the set of optimal plans changes.

Transition types (oracle properties, fixed before any model run):
- direct: every optimal B plan is an optimal A plan minus the actions that reveal the edited variable,
  and vice versa (dropping what became known is enough);
- indirect: anything else (the plan restructures, e.g. another branch of the rules becomes relevant).
`drop_rule_ok` records whether the shallow rule "drop the actions that reveal the now-known variable"
maps at least one optimal A plan to an optimal B plan (a shortcut a model could use).

Selection is by formal properties only: one edit per base record, drawn with a seed derived from the
base record id, uniformly over the non-empty (edit kind, transition type) groups. Nothing here looks at
model behaviour.
"""

from __future__ import annotations

import hashlib
import random

from msep.oracle import minimal_plan
from msep.world.state import Instance, VarKind

from .counterfactuals import set_known
from .rendering import render_state, rendering_from_json
from .schemas import instance_from_record, instance_record

GENERATOR_VERSION = "t1-v1"


def _plans(oracle: dict) -> set[frozenset[str]]:
    return {frozenset(p) for p in oracle["optimal_plans"]}


def _solve(src: dict, inst: Instance) -> tuple[dict, str]:
    r = rendering_from_json(src["rendering"])
    return minimal_plan.solve(inst.state).to_json(inst.state), render_state(inst.state, r)


def candidate_edits(src: dict) -> list[dict]:
    """Every single-variable edit of this record that changes the set of optimal plans."""
    inst = instance_from_record(src)
    st = inst.state
    a_oracle = src["oracle"]
    a_plans = _plans(a_oracle)
    out = []
    for i, v in enumerate(st.variables):
        if i == st.target or i in st.known:
            continue
        b_state = set_known(inst, [i])
        b_inst = Instance(b_state, inst.world)
        b_oracle, b_text = _solve(src, b_inst)
        b_plans = _plans(b_oracle)
        if b_oracle["resource_class"] == "AMBIGUOUS" or b_plans == a_plans and \
                b_oracle["resource_class"] == a_oracle["resource_class"]:
            continue
        revealing = sorted(a.name for a in st.actions if i in a.reveals)
        dropped = {p - frozenset(revealing) for p in a_plans}
        direct = bool(a_plans) and bool(b_plans) and dropped == b_plans
        out.append({
            "var": v.name, "var_index": i,
            "edit": "E_OBS" if v.kind is VarKind.WORLD else "E_CERT",
            "revealing_actions": revealing,
            "transition": "direct" if direct else "indirect",
            "drop_rule_ok": bool(dropped & b_plans),
            "class_a": a_oracle["resource_class"], "class_b": b_oracle["resource_class"],
            "class_change": a_oracle["resource_class"] != b_oracle["resource_class"],
            "_b": (b_inst, b_oracle, b_text),
        })
    return out


def choose(src: dict, cands: list[dict]) -> dict | None:
    if not cands:
        return None
    rng = random.Random(int(hashlib.sha256(f"{GENERATOR_VERSION}:{src['instance_id']}".encode()).hexdigest(), 16))
    groups: dict[tuple, list[dict]] = {}
    for c in cands:
        groups.setdefault((c["edit"], c["transition"]), []).append(c)
    key = rng.choice(sorted(groups))
    return rng.choice(sorted(groups[key], key=lambda c: c["var_index"]))


def _member(src: dict, inst: Instance, oracle_json: dict | None, text: str, role: str, pair_id: str,
            edit: dict) -> dict:
    res = minimal_plan.solve(inst.state)
    rec = instance_record(family_id=src["family_id"], instance_id=f"{pair_id}-{role}",
                          sibling_type=src["sibling_type"], split=src["split"], instance=inst, oracle=res,
                          transformation=f"{src['transformation']} | T1 {role}: "
                                         + ("unchanged base" if role == "A" else f"{edit['edit']} {edit['var']}"),
                          rendering=src["rendering"], prompt_text=text, notes=src.get("notes"))
    rec["base_params"] = src.get("base_params")
    rec["t1"] = {"pair_id": pair_id, "role": role, "of": src["instance_id"], "generator": GENERATOR_VERSION,
                 **{k: v for k, v in edit.items() if not k.startswith("_")}}
    return rec


def make_pair(src: dict) -> list[dict]:
    """[A, B] for this base record, or [] if no single edit changes the optimal plans."""
    c = choose(src, candidate_edits(src))
    if c is None:
        return []
    inst = instance_from_record(src)
    a_oracle, a_text = _solve(src, inst)
    b_inst, b_oracle, b_text = c["_b"]
    pair_id = f"{src['instance_id']}-T1{c['edit'][2]}{c['var']}"
    return [_member(src, inst, a_oracle, a_text, "A", pair_id, c),
            _member(src, b_inst, b_oracle, b_text, "B", pair_id, c)]
