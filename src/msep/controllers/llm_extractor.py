"""LLM state extractor (mitigation condition S2): a language model reads the prompt text and
returns the formal state as JSON; the realistic planner then plans on it.

Nothing here calls a model by itself: `LLMStateExtractor` takes a `complete(prompt, schema,
name)` function (a provider from models/providers/). Until real runs exist, the tests use a
fake provider. Computation tasks stay opaque: the extracted state never contains certified
results the agent has not paid for.

Whether this condition helps any model is UNKNOWN until real experiments are run.
"""

from __future__ import annotations

import json
import re

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.benchmark.parsing import ParseError, _FormulaParser
from msep.world.certified_tasks import OpaqueTask
from msep.world.state import FormalState, LogicalEntailment, Rule, Variable, VarKind

EXTRACTION_VERSION = "msep-extraction-v1"

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "variables": {"type": "array", "items": {
            "type": "object",
            "properties": {"handle": {"type": "string"}, "kind": {"type": "string", "enum": ["world", "computed"]}},
            "required": ["handle", "kind"], "additionalProperties": False}},
        "rules": {"type": "array", "items": {"type": "string"}},
        "known": {"type": "array", "items": {
            "type": "object",
            "properties": {"handle": {"type": "string"}, "value": {"type": "boolean"}},
            "required": ["handle", "value"], "additionalProperties": False}},
        "actions": {"type": "array", "items": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "kind": {"type": "string", "enum": ["information", "computation"]},
                           "cost": {"type": "integer"}, "reveals": {"type": "array", "items": {"type": "string"}}},
            "required": ["name", "kind", "cost", "reveals"], "additionalProperties": False}},
    },
    "required": ["variables", "rules", "known", "actions"],
    "additionalProperties": False,
}

INSTRUCTIONS = """Extract the formal state from the problem above. Do not solve it.
Return one JSON object:
- "variables": every fact handle (F1, F2, ...) with kind "world" and every computational fact (K1, ...) with kind "computed". Do not include Q.
- "rules": each rule copied exactly in the same notation (use the handles, "and", "or", "not", "if ... then ...", "if and only if", parentheses).
- "known": each value listed under "Known so far".
- "actions": each available action with its exact name, kind, cost and the handles it reveals."""


def extraction_prompt(text: str) -> str:
    return text + "\n\n" + INSTRUCTIONS


# -- Amendment 1 (2026-11-14, PREREG_EOP.md "Amendment 1"): the v1 instructions above describe the fields in
# prose only, while the parser requires one exact layout; providers without schema enforcement returned
# equivalent content in other layouts (e.g. variables as a mapping). v2 adds the exact JSON template, as the
# plan prompt has always had. v1 is kept unchanged for the registered condition C.
EXTRACTION_VERSION_V2 = "msep-extraction-v2"

INSTRUCTIONS_V2 = INSTRUCTIONS + """
Use exactly this JSON layout (lists of objects with these keys; the values here are only an example):
{
  "variables": [{"handle": "F1", "kind": "world"}, {"handle": "K1", "kind": "computed"}],
  "rules": ["if F1 then not K1", "Q if and only if (F2 and K1)"],
  "known": [{"handle": "F2", "value": true}],
  "actions": [{"name": "ASK_F1", "kind": "information", "cost": 3, "reveals": ["F1"]},
              {"name": "COMPUTE_K1", "kind": "computation", "cost": 2, "reveals": ["K1"]}]
}
Answer with this one JSON object and nothing else."""


def extraction_prompt_v2(text: str) -> str:
    return text + "\n\n" + INSTRUCTIONS_V2


def state_from_extraction(d: dict, descriptions: dict[str, str] | None = None) -> FormalState:
    handles = ["Q"] + [v["handle"] for v in d["variables"] if v["handle"] != "Q"]
    index = {h: i for i, h in enumerate(handles)}
    kinds = {v["handle"]: v["kind"] for v in d["variables"]}
    variables = tuple(Variable(h, VarKind.WORLD if h == "Q" or kinds.get(h) == "world" else VarKind.COMPUTED)
                      for h in handles)
    rules = []
    for k, txt in enumerate(d["rules"]):
        txt = re.sub(r"^\s*\d+\.\s*", "", txt)
        rules.append(Rule(f"R{k + 1}", _FormulaParser(txt, index).parse()))
    evidence, computed = [], []
    for kv in d["known"]:
        if kv["handle"] not in index:
            raise ParseError(f"unknown handle {kv['handle']}")
        (computed if variables[index[kv["handle"]]].kind is VarKind.COMPUTED else evidence).append(
            (index[kv["handle"]], bool(kv["value"])))
    info, comp = [], []
    for a in d["actions"]:
        idx = tuple(index[h] for h in a["reveals"])
        if a["kind"] == "information":
            info.append(InformationAction(a["name"], idx, int(a["cost"])))
        else:
            comp.append(ComputationAction(a["name"], idx, int(a["cost"])))
    desc = descriptions or {}
    tasks = tuple((i, OpaqueTask(desc.get(h, h))) for h, i in index.items() if variables[i].kind is VarKind.COMPUTED)
    return FormalState(variables=variables, rules=tuple(rules), target=0, evidence=tuple(sorted(evidence)),
                       computed=tuple(sorted(computed)), info_actions=tuple(info), comp_actions=tuple(comp),
                       compute_tasks=tasks, decision_rule=LogicalEntailment())


class LLMStateExtractor:
    """StateExtractor backed by a model. `complete` is a provider's complete(prompt, schema, name)."""

    def __init__(self, complete):
        self.complete = complete
        self.last_raw = None

    def extract(self, text: str) -> FormalState:
        res = self.complete(extraction_prompt(text), EXTRACTION_SCHEMA, "msep_state_extraction")
        self.last_raw = res
        if res.status != "ok" or not res.text:
            raise ParseError(f"extraction failed: {res.status} {res.error}")
        return state_from_extraction(json.loads(re.search(r"\{.*\}", res.text, re.S).group(0)))
