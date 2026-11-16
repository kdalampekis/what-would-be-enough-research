"""Benchmark record schema: serialization and exact round-trip of formal states.

A record carries the full formal state, the latent world and the oracle
labels, so it can be audited without this codebase's generator. `state_from_record`
rebuilds the FormalState; the test suite checks that re-solving it reproduces
the stored labels.
"""

from __future__ import annotations

from fractions import Fraction

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.obligations.discharge import action_discharges
from msep.oracle.minimal_plan import OracleResult
from msep.world.compute_tasks import task_from_json
from msep.world.constraints import from_json, render, to_json
from msep.world.state import (FormalState, Instance, LatentWorld, LogicalEntailment, PosteriorThreshold, Rule,
                              Variable, VarKind)

SCHEMA_VERSION = "msep-record-v1"


def state_to_json(state: FormalState) -> dict:
    v = state.variables
    names = {i: x.name for i, x in enumerate(v)}
    return {
        "variables": [{"name": x.name, "kind": x.kind.value} for x in v],
        "target": v[state.target].name,
        "rules": [{"name": r.name, "formula": to_json(r.formula), "text": render(r.formula, names)}
                  for r in state.rules],
        "cnf": [list(c) for c in state.cnf],
        "evidence": {v[i].name: val for i, val in state.evidence},
        "computed": {v[i].name: val for i, val in state.computed},
        "compute_tasks": {v[i].name: t.to_json() for i, t in state.compute_tasks},
        "info_actions": [{**a.to_json(), "reveals": [v[i].name for i in a.reveals]} for a in state.info_actions],
        "comp_actions": [{**a.to_json(), "reveals": [v[i].name for i in a.reveals]} for a in state.comp_actions],
        "decision_rule": state.decision_rule.to_json(),
        "prior": {v[i].name: str(p) for i, p in state.prior},
    }


def state_from_json(d: dict) -> FormalState:
    variables = tuple(Variable(x["name"], VarKind(x["kind"])) for x in d["variables"])
    idx = {x.name: i for i, x in enumerate(variables)}
    rule = d["decision_rule"]
    dr = LogicalEntailment() if rule["kind"] == "logical_entailment" else PosteriorThreshold(Fraction(rule["tau"]))
    return FormalState(
        variables=variables,
        rules=tuple(Rule(r["name"], from_json(r["formula"])) for r in d["rules"]),
        target=idx[d["target"]],
        evidence=tuple(sorted((idx[k], bool(val)) for k, val in d["evidence"].items())),
        computed=tuple(sorted((idx[k], bool(val)) for k, val in d["computed"].items())),
        info_actions=tuple(InformationAction(a["name"], tuple(idx[x] for x in a["reveals"]), a["cost"])
                           for a in d["info_actions"]),
        comp_actions=tuple(ComputationAction(a["name"], tuple(idx[x] for x in a["reveals"]), a["cost"])
                           for a in d["comp_actions"]),
        compute_tasks=tuple(sorted((idx[k], task_from_json(t)) for k, t in d["compute_tasks"].items())),
        decision_rule=dr,
        prior=tuple(sorted((idx[k], Fraction(p)) for k, p in d["prior"].items())),
    )


def instance_record(*, family_id: str, instance_id: str, sibling_type: str, split: str,
                    instance: Instance, oracle: OracleResult, transformation: str,
                    rendering: dict | None = None, prompt_text: str | None = None, notes: dict | None = None) -> dict:
    s = instance.state
    v = s.variables
    oj = oracle.to_json(s)
    effects = {a.name: {"reveals": [v[i].name for i in a.reveals],
                        "discharges": None} for a in s.actions}
    if oracle.obligations is not None:
        for name, obs in action_discharges(s, oracle.obligations).items():
            effects[name]["discharges"] = obs
    return {
        "schema_version": SCHEMA_VERSION,
        "family_id": family_id,
        "instance_id": instance_id,
        "sibling_type": sibling_type,
        "split": split,
        "level": _level(oj["resource_class"], oj["optimal_plans"]),
        "transformation": transformation,
        "state": state_to_json(s),
        "latent_world": {v[i].name: val for i, val in instance.world.values},
        "true_computed_values": {v[i].name: val for i, val in sorted(s.true_computed_values().items())},
        "true_target_value": instance.full_assignment()[s.target],
        "action_effects": effects,
        "oracle": oj,
        "notes": notes or {},
        "rendering": rendering,
        "prompt_text": prompt_text,
    }


def _level(rclass: str, plans: list) -> int:
    """Difficulty level (PROBLEM_SPEC section 12) for static instances."""
    if rclass == "ALREADY_SUFFICIENT":
        return 0
    if rclass == "NEITHER":
        return 3
    if rclass == "BOTH":
        return 2
    return 1


def instance_from_record(rec: dict) -> Instance:
    state = state_from_json(rec["state"])
    idx = {x.name: i for i, x in enumerate(state.variables)}
    world = LatentWorld(tuple(sorted((idx[k], bool(val)) for k, val in rec["latent_world"].items())))
    return Instance(state, world)
