"""First failure stage of a response (ASSUMPTIONS.md A2). Never one 'action accuracy' number."""

from __future__ import annotations

STAGES = ("detection", "diagnosis", "targeting", "sufficiency", "minimality", "stopping", "correct")


def classify(record: dict, response, scored: dict) -> str:
    oracle = record["oracle"]
    rclass = oracle["resource_class"]
    if not scored["detection_correct"]:
        return "detection"
    if oracle["current_sufficient"]:
        # sufficient already: any action is a stopping failure (acting after sufficiency)
        return "stopping" if scored["plan_cost"] > 0 else "correct"
    if not scored["class_correct"]:
        return "diagnosis"
    if rclass == "NEITHER":
        return "stopping" if (scored["plan_cost"] > 0 or response.decision != "defer") else "correct"
    if not scored["plan_valid"]:
        return "targeting"
    if not scored["plan_sufficient"]:
        relevant = {a["name"]: a["relevant"] for a in oracle["actions"]}
        alias = (record.get("rendering") or {}).get("action_alias") or {}
        inv = {v: k for k, v in alias.items()} or {n: n for n in relevant}
        chosen = [inv.get(p, p) for p in response.plan]
        # relevant-but-not-enough vs aiming at the wrong things entirely
        return "sufficiency" if chosen and all(relevant.get(c, False) for c in chosen) else "targeting"
    if not scored["plan_optimal"]:
        return "minimality"
    if response.decision != "defer" or not response.stop_after_plan:
        return "stopping"
    return "correct"
