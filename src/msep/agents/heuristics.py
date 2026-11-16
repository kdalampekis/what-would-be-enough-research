"""Shallow, visible-only HEURISTIC baselines (no language model, no oracle).

Found by the independent adversarial audit (2026-11-04): reading only the rule
that defines Q solves template v2 completely. These baselines are reported next
to every model result. A benchmark on which they score near the oracle cannot
show that a model reasons about sufficiency.

They read only the prompt text (parsed with benchmark/parsing.py, which needs
nothing hidden). Unlike the mock agents these are genuine deterministic
baselines, so their scores are real results about the benchmark, not about LLMs.

    h1    unknown variables in Q's rule -> class by their kinds; plan = actions on them
    h1p   h1, plus: use an equivalent variable ("X if and only if Y") when its action is
          cheaper, and answer NEITHER when an unknown Q-rule variable has no action
    h1pp  h1p, plus: a Q-rule variable with no action that is defined by a rule
          ("X if and only if <formula>") is replaced by the unknown variables of that formula
"""

from __future__ import annotations

from msep.benchmark.parsing import parse_state
from msep.world.constraints import Iff, Not, Var, evaluate, variables
from msep.world.state import VarKind

HEURISTICS = ("h1", "h1p", "h1pp")


def _q_rule(st):
    for r in st.rules:
        f = r.formula
        if isinstance(f, Iff) and isinstance(f.left, Var) and f.left.index == st.target:
            return f
    return None


def _definitions(st):
    """var index -> defining formula, for rules 'X iff <formula>' (X a variable, not Q)."""
    out = {}
    for r in st.rules:
        f = r.formula
        if isinstance(f, Iff) and isinstance(f.left, Var) and f.left.index != st.target:
            out[f.left.index] = f.right
    return out


def _cheapest_action(st, v):
    acts = [a for a in st.actions if a.reveals == (v,)]
    return min(acts, key=lambda a: (a.cost, a.name)) if acts else None


def _alias_of(st, v):
    """Variables declared equivalent to v by a rule 'X if and only if Y' (both plain variables)."""
    out = []
    for r in st.rules:
        f = r.formula
        if isinstance(f, Iff):
            l, rr = f.left, f.right
            if isinstance(l, Var) and isinstance(rr, Var):
                if l.index == v:
                    out.append(rr.index)
                elif rr.index == v:
                    out.append(l.index)
    return out


def plan_for(agent: str, text: str) -> dict:
    st = parse_state(text)
    qr = _q_rule(st)
    if qr is None:
        return {"state_sufficient": False, "resource_class": "NEITHER", "plan": [], "decision": "defer"}
    needed = sorted(v for v in variables(qr.right) if v not in st.known)
    if agent == "h1pp":
        defs = _definitions(st)
        expanded, frontier = [], list(needed)
        seen = set()
        while frontier:
            v = frontier.pop()
            if v in seen:
                continue
            seen.add(v)
            if _cheapest_action(st, v) is None and v in defs:
                frontier += [u for u in variables(defs[v]) if u not in st.known]
            else:
                expanded.append(v)
        needed = sorted(set(expanded))
    if not needed:
        decided = evaluate(qr.right, {**{v: False for v in range(st.n)}, **st.known})
        return {"state_sufficient": True, "resource_class": "ALREADY_SUFFICIENT", "plan": [],
                "decision": "true" if decided else "false"}
    plan, kinds, missing = [], set(), False
    for v in needed:
        a = _cheapest_action(st, v)
        if agent in ("h1p", "h1pp"):
            for w in _alias_of(st, v):
                b = _cheapest_action(st, w)
                if b is not None and (a is None or b.cost < a.cost):
                    a = b
        if a is None:
            missing = True
            continue
        plan.append(a)
        kinds.add(st.variables[a.reveals[0]].kind)
    if missing and agent in ("h1p", "h1pp"):
        return {"state_sufficient": False, "resource_class": "NEITHER", "plan": [], "decision": "defer"}
    cls = ("BOTH" if kinds == {VarKind.WORLD, VarKind.COMPUTED} else
           "INFORMATION_ONLY" if kinds == {VarKind.WORLD} else
           "COMPUTATION_ONLY" if kinds == {VarKind.COMPUTED} else "NEITHER")
    return {"state_sufficient": False, "resource_class": cls, "plan": sorted({a.name for a in plan}), "decision": "defer"}


def respond(agent: str, job, rec: dict) -> dict:
    """Same output schema as a model. Uses rec['prompt_text'] only (plus the job's candidate)."""
    kind = job.pool.split("_")[0]
    text = rec["prompt_text"]
    out = plan_for(agent, text)
    if kind == "capability":
        return {"value": "true", "confidence": 0.5, "short_justification": f"heuristic:{agent}"}
    if kind == "decision":
        d = out.get("decision")
        return {"decision": d if d in ("true", "false") else "true", "confidence": 0.5,
                "short_justification": f"heuristic:{agent}"}
    if kind == "judgment":
        alias = rec["rendering"]["action_alias"]
        shown = {alias[a] for a in job.candidate}
        # sufficient iff the candidate covers the heuristic's own plan
        ok = out["resource_class"] not in ("NEITHER",) and set(out["plan"]) <= shown
        return {"plan_sufficient": ok, "confidence": 0.5, "short_justification": f"heuristic:{agent}"}
    st_names = {a.name: ("ASK" if a.name.startswith("ASK") else "COMPUTE") for a in parse_state(text).actions}
    return {"state_sufficient": out["state_sufficient"], "resource_class": out["resource_class"],
            "plan": [{"type": st_names.get(a, "ASK"), "action": a} for a in out["plan"]],
            "stop_after_plan": True, "decision": out["decision"], "confidence": 0.5,
            "short_justification": f"heuristic:{agent}"}
