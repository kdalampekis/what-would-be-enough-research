"""Mitigation condition B (S1): structured obligation-reasoning prompt.

The base prompt (models/prompts.py, unchanged) is followed by step-by-step instructions to reason about
epistemic obligations before answering. The output JSON and its scoring are identical to the native
condition, so A (native) and B differ only in these instructions. Kept in its own module so the frozen
prompt file is untouched.

With a forced-schema provider condition (structured function tool) the model can only reason
internally; the reasoning text, if any, is not scored.
"""

S1_VERSION = "msep-s1-obligations-v1"

S1_INSTRUCTIONS = """Before answering, reason about the epistemic obligations step by step:
1. List what is already known.
2. Decide whether the known facts already settle Q under the rules. If they do, the plan is empty.
3. If not, list the obligations: each unknown fact or uncertified computational result whose value could still change the answer about Q.
4. For each obligation, list the available actions that would settle it. An action that settles no obligation is unnecessary.
5. Choose the cheapest set of actions that settles every obligation whatever the results are, and remove any action that is not needed. If some obligation cannot be settled by any available action, no plan can justify the decision: use an empty plan and decision "defer".
You may write this reasoning briefly before the JSON object, without curly braces; the JSON object must come last."""


def s1_prompt(base_prompt: str) -> str:
    return base_prompt + "\n\n" + S1_INSTRUCTIONS
