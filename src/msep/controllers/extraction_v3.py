"""Extraction prompt v3 (robustness study only, PREREG_ROBUST.md): a normalising variant of prompt v2.

Prompt v2 (the frozen EOP extraction) tells the model to copy each rule "exactly in the same notation" and
refers to the canonical section name "Known so far". On reworded text those instructions do not literally
apply. v3 asks for the same JSON but tells the model to translate differently worded content into the
fixed notation. Registered before any robustness response as a secondary condition; never used on the test
split. Kept in its own module so the frozen extractor file is untouched.
"""

from msep.controllers.llm_extractor import INSTRUCTIONS, INSTRUCTIONS_V2

EXTRACTION_VERSION_V3 = "msep-extraction-v3-normalising"

INSTRUCTIONS_V3 = """Extract the formal state from the problem above. Do not solve it.
The problem may word things in its own way; report its content in the fixed form below.
Return one JSON object:
- "variables": every fact about the world (handles F1, F2, ...) with kind "world" and every computational or derived fact (handles K1, ...) with kind "computed". Do not include Q.
- "rules": every rule or constraint the problem states, each written in this notation: the handles, "and", "or", "not", "if ... then ...", "if and only if", parentheses. If the problem states a rule in other words, translate it faithfully into this notation (for example "K1 is false whenever F1 is true" becomes "if F1 then not K1").
- "known": every value the problem says is already known or established.
- "actions": every available action or step with its exact name, its kind ("information" if it obtains evidence about the world, "computation" if it runs a procedure), its cost and the handles it reveals.""" \
    + INSTRUCTIONS_V2[len(INSTRUCTIONS):]


def extraction_prompt_v3(text: str) -> str:
    return text + "\n\n" + INSTRUCTIONS_V3
