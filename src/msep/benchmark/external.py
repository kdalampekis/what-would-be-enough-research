"""E13 infrastructure: convert externally sourced propositional problems into formal states.

No dataset is bundled or downloaded. ProofWriter- or FOLIO-derived problems
must be obtained under their own licences and first converted (by a separate,
documented script) into this intermediate format, one JSON object per line:

    {
      "id": "pw-000123",
      "source": "ProofWriter depth-3 (converted)",
      "atoms": ["bob_is_big", "bob_is_red", ...],      # ground propositions
      "facts": {"bob_is_big": true, ...},               # values stated in the theory
      "rules": [{"if": ["bob_is_big", "!bob_is_red"], "then": "bob_is_kind"}, ...],
      "query": "bob_is_kind",
      "withhold": ["bob_is_big"],                       # stated facts turned into unknowns
      "ask_cost": 1
    }

Conversion: atoms become world variables; rules become implications; the
"withhold" facts are removed from the evidence and each gets an ASK action.
The latent world must satisfy all rules and the original facts; atoms not fixed
by them get the value derived by forward chaining (else false), and the
converter rejects a problem whose completed world violates a rule.
Only information actions are produced: certified-computation actions over
external theories are not defined yet (see ASSUMPTIONS.md F7).
"""

from __future__ import annotations

import json
from pathlib import Path

from msep.actions.information import InformationAction
from msep.world.constraints import And, Implies, evaluate, lit
from msep.world.state import FormalState, Instance, LatentWorld, Rule, Variable, VarKind


class ConversionError(ValueError):
    pass


def _lit(name: str, idx: dict):
    neg = name.startswith("!")
    a = name[1:] if neg else name
    if a not in idx:
        raise ConversionError(f"unknown atom {a}")
    return lit(idx[a], not neg)


def convert(problem: dict) -> Instance:
    atoms = list(problem["atoms"])
    if problem["query"] not in atoms:
        raise ConversionError("query is not an atom")
    # target first, so the target index is 0
    atoms.remove(problem["query"])
    atoms = [problem["query"], *atoms]
    idx = {a: i for i, a in enumerate(atoms)}
    rules = []
    for k, r in enumerate(problem["rules"]):
        body = [_lit(x, idx) for x in r["if"]]
        rules.append(Rule(f"R{k + 1}", Implies(body[0] if len(body) == 1 else And(tuple(body)), _lit(r["then"], idx))))
    facts = {a: bool(v) for a, v in problem["facts"].items()}
    # complete the latent world: stated facts, then forward chaining, else false
    world = {idx[a]: v for a, v in facts.items()}
    changed = True
    while changed:
        changed = False
        for r in problem["rules"]:
            if all(world.get(idx[x.lstrip("!")]) is (not x.startswith("!")) for x in r["if"]):
                h = r["then"].lstrip("!")
                val = not r["then"].startswith("!")
                if idx[h] not in world:
                    world[idx[h]] = val
                    changed = True
    for i in range(len(atoms)):
        world.setdefault(i, False)
    if not all(evaluate(r.formula, world) for r in rules):
        raise ConversionError("completed world violates a rule")
    withhold = set(problem.get("withhold", []))
    evidence = tuple(sorted((idx[a], v) for a, v in facts.items() if a not in withhold and a != problem["query"]))
    cost = int(problem.get("ask_cost", 1))
    info = tuple(InformationAction(f"ASK_{a}", (idx[a],), cost) for a in sorted(withhold))
    state = FormalState(variables=tuple(Variable(a, VarKind.WORLD) for a in atoms), rules=tuple(rules), target=0,
                        evidence=evidence, info_actions=info)
    return Instance(state, LatentWorld(tuple(sorted(world.items()))))


def load(path: Path) -> list[tuple[dict, Instance | None, str | None]]:
    out = []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        try:
            out.append((p, convert(p), None))
        except ConversionError as e:
            out.append((p, None, str(e)))
    return out
