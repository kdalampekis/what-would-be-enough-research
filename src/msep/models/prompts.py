"""Prompts for the three evaluation modes. No model is called in Phase 1.

A. END_TO_END            the model must detect, diagnose and plan.
B. DETECTION_CONTROLLED  told the state is insufficient (primary mode).
C. DIAGNOSIS_CONTROLLED  additionally told the correct resource class.

Eligibility: mode B excludes ALREADY_SUFFICIENT instances (the statement would
be false). Mode C also excludes NEITHER (no plan to construct) and AMBIGUOUS.
"""

from __future__ import annotations

from enum import Enum

OUTPUT_INSTRUCTIONS = """Answer with one JSON object and nothing else:
{
  "state_sufficient": true or false,
  "resource_class": "ALREADY_SUFFICIENT" | "INFORMATION_ONLY" | "COMPUTATION_ONLY" | "BOTH" | "NEITHER",
  "plan": [{"type": "ASK" or "COMPUTE", "action": "<action name exactly as listed>"}],
  "stop_after_plan": true or false,
  "decision": "true" | "false" | "defer",
  "confidence": number between 0 and 1,
  "short_justification": "<one or two sentences>"
}
"plan" is the cheapest set of actions that would make the decision justified whatever their results are.
Use an empty plan if the decision is already justified, or if no available plan can justify it.
"decision" is your answer about Q now if the decision is already justified, otherwise "defer"."""


class Mode(str, Enum):
    END_TO_END = "end_to_end"
    DETECTION_CONTROLLED = "detection_controlled"
    DIAGNOSIS_CONTROLLED = "diagnosis_controlled"


CLASS_SENTENCE = {
    "INFORMATION_ONLY": "Resolving this state requires additional information only.",
    "COMPUTATION_ONLY": "Resolving this state requires additional computation only.",
    "BOTH": "Resolving this state requires both additional information and additional computation.",
}


def eligible(mode: Mode, resource_class: str) -> bool:
    if resource_class == "AMBIGUOUS":
        return False
    if mode is Mode.DETECTION_CONTROLLED:
        return resource_class != "ALREADY_SUFFICIENT"
    if mode is Mode.DIAGNOSIS_CONTROLLED:
        return resource_class in CLASS_SENTENCE
    return True


def build_prompt(state_text: str, mode: Mode, resource_class: str) -> str:
    if not eligible(mode, resource_class):
        raise ValueError(f"{resource_class} instances are not used in mode {mode.value}")
    parts = [state_text, ""]
    if mode in (Mode.DETECTION_CONTROLLED, Mode.DIAGNOSIS_CONTROLLED):
        parts.append("The current state is not yet sufficient to justify a reliable decision.")
    if mode is Mode.DIAGNOSIS_CONTROLLED:
        parts.append(CLASS_SENTENCE[resource_class])
    parts += ["", OUTPUT_INSTRUCTIONS]
    return "\n".join(parts)


PROMPT_VERSION = "msep-prompts-v2-certified-compute"


def build_judgment_prompt(state_text: str, candidate_display: list[str]) -> str:
    """E5: is this specific plan sufficient? (States are known to be insufficient.)"""
    plan = ", ".join(candidate_display) if candidate_display else "(no actions)"
    return "\n".join([
        state_text, "",
        "The current state is not yet sufficient to justify a reliable decision.",
        f"Proposed plan: run exactly these actions: {plan}.",
        "Question: if exactly these actions are run (their results are not known in advance), will a decision "
        "about Q be justified whatever their results turn out to be?",
        "",
        'Answer with one JSON object and nothing else: {"plan_sufficient": true or false, '
        '"confidence": number between 0 and 1, "short_justification": "<one or two sentences>"}',
    ])


def build_decision_prompt(state_text: str) -> str:
    """E1: base competence on already-sufficient states."""
    return "\n".join([
        state_text, "",
        "The current state already justifies a decision about Q. No action is needed.",
        "Question: is Q true or false?",
        "",
        'Answer with one JSON object and nothing else: {"decision": "true" or "false", '
        '"confidence": number between 0 and 1, "short_justification": "<one or two sentences>"}',
    ])


def build_capability_prompt(task_description: str) -> str:
    """E14 control: can the model settle the computational fact itself, with no planning context?"""
    return "\n".join([
        "Decide whether the following statement is true or false. Work it out yourself; no tools are available.",
        "",
        f"Statement: {task_description}",
        "",
        'Answer with one JSON object and nothing else: {"value": "true" or "false", '
        '"confidence": number between 0 and 1, "short_justification": "<one or two sentences>"}',
    ])
