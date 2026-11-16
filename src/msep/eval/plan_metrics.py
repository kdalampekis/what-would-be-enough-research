"""Score a structured response against the exact oracle.

Every plan is re-checked with the oracle (`is_sufficient`), so scores do not
depend on matching the oracle's plan text.

Value and regret (normalised cost model, ASSUMPTIONS.md A15):
    L = 1 + total cost of all available actions   (penalty for an unjustified outcome)
    resolvable instance:  V(plan) = -cost(plan) - L * [plan insufficient]
    NEITHER instance:     V(plan) = -cost(plan) - L * [response commits to an answer]
    regret = V(oracle plan) - V(model plan)   (always >= 0)
"""

from __future__ import annotations

from msep.benchmark.schemas import instance_from_record
from msep.models.schemas import ModelResponse
from msep.oracle.sufficiency import canonical, is_sufficient, plan_cost


def score(record: dict, response: ModelResponse, action_alias: dict[str, str] | None = None) -> dict:
    inst = instance_from_record(record)
    state = inst.state
    oracle = record["oracle"]
    alias = action_alias or (record.get("rendering") or {}).get("action_alias") or {a.name: a.name for a in state.actions}
    inv = {v: k for k, v in alias.items()}
    unknown_actions = [p for p in response.plan if p not in inv]
    plan = canonical(inv[p] for p in response.plan if p in inv)
    rclass = oracle["resource_class"]
    sufficient = is_sufficient(state, plan)
    cost = plan_cost(state, plan)
    best = oracle["optimal_cost"]
    minimal = [tuple(m["plan"]) for m in oracle["minimal_sufficient_plans"]]
    optimal = [tuple(p) for p in oracle["optimal_plans"]]
    penalty = 1 + sum(a.cost for a in state.actions)
    if rclass == "NEITHER":
        v_star = 0
        v_model = -cost - penalty * (response.decision != "defer")
    else:
        v_star = -best
        v_model = -cost - penalty * (not sufficient)
    truth = record["true_target_value"]
    decision_correct = None
    if response.decision in ("true", "false"):
        decision_correct = (response.decision == "true") == truth
    return {
        "detection_correct": response.state_sufficient == oracle["current_sufficient"],
        "class_correct": response.resource_class == rclass,
        "plan_valid": not unknown_actions,
        "unknown_actions": unknown_actions,
        "plan_exact_match": plan in optimal,
        "plan_sufficient": sufficient,
        "plan_minimal": plan in minimal,
        "plan_optimal": sufficient and best is not None and cost == best,
        "plan_cost": cost,
        "excess_cost": (cost - best) if (sufficient and best is not None) else None,
        "answered_prematurely": response.decision != "defer" and not oracle["current_sufficient"],
        "decision_correct": decision_correct,
        "value": v_model,
        "regret": v_star - v_model,
    }
