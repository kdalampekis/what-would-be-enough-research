"""Structured model output: parsing and validation. Fields are scored, not prose."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

CLASSES = ("ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER")


@dataclass
class ModelResponse:
    state_sufficient: bool
    resource_class: str
    plan: list[str]            # display action names
    plan_types: list[str]
    stop_after_plan: bool
    decision: str
    confidence: float | None
    short_justification: str


class ParseError(ValueError):
    pass


def parse_response(text: str) -> ModelResponse:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ParseError("no JSON object found")
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ParseError(f"invalid JSON: {e}") from e
    if not isinstance(d.get("state_sufficient"), bool):
        raise ParseError("state_sufficient must be a boolean")
    if d.get("resource_class") not in CLASSES:
        raise ParseError("resource_class not recognised")
    plan = d.get("plan")
    if not isinstance(plan, list) or not all(isinstance(p, dict) and isinstance(p.get("action"), str) for p in plan):
        raise ParseError("plan must be a list of {type, action} objects")
    decision = str(d.get("decision", "defer")).lower()
    if decision not in ("true", "false", "defer"):
        raise ParseError("decision must be true, false or defer")
    conf = d.get("confidence")
    if conf is not None and not (isinstance(conf, (int, float)) and 0 <= conf <= 1):
        raise ParseError("confidence must be in [0, 1]")
    return ModelResponse(
        state_sufficient=d["state_sufficient"], resource_class=d["resource_class"],
        plan=[p["action"] for p in plan], plan_types=[str(p.get("type", "")).upper() for p in plan],
        stop_after_plan=bool(d.get("stop_after_plan", True)), decision=decision,
        confidence=None if conf is None else float(conf),
        short_justification=str(d.get("short_justification", "")))


# -- JSON schemas sent to both providers (identical for both) ------------------------
# Changing any schema requires bumping SCHEMA_VERSION; tests/test_inference_readiness.py
# holds a snapshot of every schema and fails on any unversioned change.
SCHEMA_VERSION = "msep-schemas-v2"  # v2 adds CAPABILITY_SCHEMA (E14); v1 schemas unchanged
# Kept within the common subset of strict structured outputs: every property
# required, additionalProperties false, no numeric bounds (checked in parsing).

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "state_sufficient": {"type": "boolean"},
        "resource_class": {"type": "string", "enum": list(CLASSES)},
        "plan": {"type": "array", "items": {
            "type": "object",
            "properties": {"type": {"type": "string", "enum": ["ASK", "COMPUTE"]}, "action": {"type": "string"}},
            "required": ["type", "action"], "additionalProperties": False}},
        "stop_after_plan": {"type": "boolean"},
        "decision": {"type": "string", "enum": ["true", "false", "defer"]},
        "confidence": {"type": "number"},
        "short_justification": {"type": "string"},
    },
    "required": ["state_sufficient", "resource_class", "plan", "stop_after_plan", "decision", "confidence",
                 "short_justification"],
    "additionalProperties": False,
}

JUDGMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_sufficient": {"type": "boolean"},
        "confidence": {"type": "number"},
        "short_justification": {"type": "string"},
    },
    "required": ["plan_sufficient", "confidence", "short_justification"],
    "additionalProperties": False,
}

DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["true", "false"]},
        "confidence": {"type": "number"},
        "short_justification": {"type": "string"},
    },
    "required": ["decision", "confidence", "short_justification"],
    "additionalProperties": False,
}


def _obj(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ParseError("no JSON object found")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ParseError(f"invalid JSON: {e}") from e


def parse_judgment(text: str) -> dict:
    d = _obj(text)
    if not isinstance(d.get("plan_sufficient"), bool):
        raise ParseError("plan_sufficient must be a boolean")
    return {"plan_sufficient": d["plan_sufficient"], "confidence": d.get("confidence")}


def parse_decision(text: str) -> dict:
    d = _obj(text)
    if d.get("decision") not in ("true", "false"):
        raise ParseError("decision must be 'true' or 'false'")
    return {"decision": d["decision"], "confidence": d.get("confidence")}


CAPABILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string", "enum": ["true", "false"]},
        "confidence": {"type": "number"},
        "short_justification": {"type": "string"},
    },
    "required": ["value", "confidence", "short_justification"],
    "additionalProperties": False,
}


def parse_capability(text: str) -> dict:
    d = _obj(text)
    if d.get("value") not in ("true", "false"):
        raise ParseError("value must be 'true' or 'false'")
    return {"value": d["value"], "confidence": d.get("confidence")}
