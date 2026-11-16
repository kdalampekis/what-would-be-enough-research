"""SYNTHETIC mock agents: deterministic test fixtures, NOT research results.

They exist to exercise the experiment pipeline end to end (runner, raw logging,
scoring, statistics, reports) and to check that each metric moves the way it
should for a known behaviour. Several of them read oracle labels to simulate a
behaviour (stated per agent); that is acceptable only because they are fixtures.

Every response they produce is marked synthetic in the raw record, and reports
built from them carry a SYNTHETIC banner.
"""

from __future__ import annotations

import hashlib
import random

AGENTS = ("oracle_perfect", "always_answer", "always_ask", "always_compute", "always_abstain", "random",
          "relevant_insufficient", "expensive_sufficient", "premature_stop",
          "detection_blind", "needs_diagnosis", "noncompliant")

DESCRIPTIONS = {
    "oracle_perfect": "reads the oracle labels and answers them (upper bound; uses oracle)",
    "always_answer": "always claims the state is sufficient and answers 'true' (visible-only)",
    "always_ask": "always proposes every offered ASK action (visible-only)",
    "always_compute": "always proposes every offered computation action (visible-only)",
    "always_abstain": "always says NEITHER, no plan, defer (visible-only)",
    "random": "seeded random class, plan subset and decision (visible-only)",
    "relevant_insufficient": "proposes a relevant but insufficient plan where one exists (uses oracle roles)",
    "expensive_sufficient": "proposes every action that reveals an unknown variable (visible-only)",
    "premature_stop": "proposes only the first action of an optimal plan and stops (uses oracle)",
    "detection_blind": "End-to-End: always claims sufficiency and answers; controlled modes: oracle (uses oracle)",
    "needs_diagnosis": "Diagnosis-Controlled: oracle; otherwise behaves like always_ask (uses oracle)",
    "noncompliant": "controlled modes: contradicts the given facts by claiming sufficiency, plan from oracle (uses oracle)",
}


def _display(rec: dict, formal: list[str]) -> list[str]:
    alias = rec["rendering"]["action_alias"]
    return [alias[a] for a in formal]


def _menu(rec: dict) -> list[tuple[str, str]]:
    """(display name, ASK|COMPUTE) for every offered action, from the record's state."""
    alias = rec["rendering"]["action_alias"]
    out = [(alias[a["name"]], "ASK") for a in rec["state"]["info_actions"]]
    out += [(alias[a["name"]], "COMPUTE") for a in rec["state"]["comp_actions"]]
    return out


def _plan_items(rec: dict, display: list[str]) -> list[dict]:
    kinds = dict(_menu(rec))
    return [{"type": kinds.get(a, "ASK"), "action": a} for a in display]


def _cls(plan_types: set[str]) -> str:
    if {"ASK", "COMPUTE"} <= plan_types:
        return "BOTH"
    if "ASK" in plan_types:
        return "INFORMATION_ONLY"
    if "COMPUTE" in plan_types:
        return "COMPUTATION_ONLY"
    return "NEITHER"


def respond(agent: str, job, rec: dict) -> dict:
    kind = job.pool.split("_")[0]
    # mode-dependent fixtures for validating the mode decomposition
    if agent == "detection_blind":
        agent = "always_answer" if (kind == "plan" and job.mode == "end_to_end") else "oracle_perfect"
    elif agent == "needs_diagnosis":
        agent = "oracle_perfect" if (kind != "plan" or job.mode == "diagnosis_controlled") else "always_ask"
    elif agent == "noncompliant":
        out = respond("oracle_perfect", job, rec)
        if kind == "plan" and job.mode in ("detection_controlled", "diagnosis_controlled"):
            out["state_sufficient"] = True
        return out
    o = rec["oracle"]
    truth = "true" if rec["true_target_value"] else "false"
    h = int(hashlib.sha256(f"{agent}:{job.prompt}".encode()).hexdigest()[:12], 16)
    rng = random.Random(h)

    if kind == "capability":
        var = (job.meta or {}).get("var")
        truth = rec["true_computed_values"].get(var)
        if agent == "oracle_perfect":
            val = truth
        elif agent in ("always_answer", "relevant_insufficient"):
            val = True
        else:
            val = rng.random() < 0.5
        return {"value": "true" if val else "false", "confidence": 0.5, "short_justification": f"synthetic:{agent}"}
    if kind == "decision":
        ans = {"oracle_perfect": truth, "random": rng.choice(["true", "false"]), "always_abstain": "false"}.get(agent, "true")
        return {"decision": ans, "confidence": 0.5, "short_justification": f"synthetic:{agent}"}

    if kind == "judgment":
        cand = list(job.candidate)
        menu_kind = {a["name"]: "ASK" for a in rec["state"]["info_actions"]}
        menu_kind.update({a["name"]: "COMPUTE" for a in rec["state"]["comp_actions"]})
        if agent == "oracle_perfect":
            label = (job.meta or {}).get("kind") == "optimal"
        elif agent == "always_answer" or agent == "relevant_insufficient":
            label = True        # relevance bias: any plan "would be enough"
        elif agent == "always_abstain":
            label = False
        elif agent == "always_ask":
            label = any(menu_kind.get(a) == "ASK" for a in cand)
        elif agent == "always_compute":
            label = any(menu_kind.get(a) == "COMPUTE" for a in cand)
        elif agent == "random":
            label = rng.random() < 0.5
        elif agent == "expensive_sufficient":
            label = (job.meta or {}).get("kind") == "optimal"
        else:  # premature_stop: judges a partial plan as enough
            label = True
        return {"plan_sufficient": label, "confidence": 0.5, "short_justification": f"synthetic:{agent}"}

    # plan responses
    menu = _menu(rec)
    optimal = list(o["optimal_plans"][0]) if o["optimal_plans"] else []
    if agent == "oracle_perfect":
        plan = _display(rec, optimal) if not o["current_sufficient"] else []
        return _plan(rec, o["current_sufficient"], o["resource_class"], plan,
                     truth if o["current_sufficient"] else "defer")
    if agent == "always_answer":
        return _plan(rec, True, "ALREADY_SUFFICIENT", [], "true")
    if agent == "always_ask":
        plan = [a for a, k in menu if k == "ASK"]
        return _plan(rec, False, "INFORMATION_ONLY", plan, "defer")
    if agent == "always_compute":
        plan = [a for a, k in menu if k == "COMPUTE"]
        return _plan(rec, False, "COMPUTATION_ONLY", plan, "defer")
    if agent == "always_abstain":
        return _plan(rec, False, "NEITHER", [], "defer")
    if agent == "random":
        plan = [a for a, _ in menu if rng.random() < 0.4]
        cls = rng.choice(["ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER"])
        return _plan(rec, cls == "ALREADY_SUFFICIENT", cls, plan, rng.choice(["true", "false", "defer"]))
    if agent == "expensive_sufficient":
        known = set(rec["state"]["evidence"]) | set(rec["state"]["computed"])
        acts = [a for a in rec["state"]["info_actions"] + rec["state"]["comp_actions"]
                if any(v not in known for v in a["reveals"])]
        plan = _display(rec, [a["name"] for a in acts])
        types = {dict(menu)[p] for p in plan}
        return _plan(rec, not plan, _cls(types) if plan else "ALREADY_SUFFICIENT", plan, "defer" if plan else truth)
    if agent == "relevant_insufficient":
        decoys = [a["name"] for a in o["actions"] if a["category"] == "relevant_insufficient"]
        if decoys:
            formal = [decoys[0]]
        elif len(optimal) >= 2:
            formal = optimal[:-1]
        else:
            formal = optimal
        plan = _display(rec, formal)
        types = {dict(menu)[p] for p in plan}
        return _plan(rec, False, _cls(types) if plan else "NEITHER", plan, "defer")
    if agent == "premature_stop":
        plan = _display(rec, optimal[:1])
        types = {dict(menu)[p] for p in plan}
        return _plan(rec, o["current_sufficient"], _cls(types) if plan else o["resource_class"], plan,
                     truth if not plan else "defer", stop=True)
    raise ValueError(agent)


def _plan(rec, sufficient, cls, plan, decision, stop=True) -> dict:
    return {"state_sufficient": sufficient, "resource_class": cls, "plan": _plan_items(rec, plan),
            "stop_after_plan": stop, "decision": decision, "confidence": 0.5, "short_justification": "synthetic"}
