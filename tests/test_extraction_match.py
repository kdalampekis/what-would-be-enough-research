import json
from dataclasses import replace
from pathlib import Path

from msep.benchmark.parsing import parse_state
from msep.eval.extraction_match import compare
from msep.world.constraints import Not
from msep.world.state import Rule

ROOT = Path(__file__).resolve().parents[1]


def _states(n=12):
    out = []
    with open(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r["split"] == "train":
                out.append(parse_state(r["prompt_text"], opaque_tasks=True))
            if len(out) == n:
                break
    return out


def test_identity_and_rule_order():
    for s in _states():
        assert compare(s, s)["exact"]
        assert compare(replace(s, rules=tuple(reversed(s.rules))), s)["exact"]


def test_detects_changes():
    for s in _states():
        neg = replace(s, rules=(Rule("R1", Not(s.rules[0].formula)), *s.rules[1:]))
        assert compare(neg, s)["rules"] is False
        assert not compare(replace(s, rules=s.rules[1:]), s)["exact"] or len(s.rules) == 1
        if s.evidence:
            assert compare(replace(s, evidence=s.evidence[1:]), s)["known"] is False
        a = s.actions[0]
        bumped = replace(a, cost=a.cost + 1)
        info = tuple(bumped if x.name == a.name else x for x in s.info_actions)
        comp = tuple(bumped if x.name == a.name else x for x in s.comp_actions)
        assert compare(replace(s, info_actions=info, comp_actions=comp), s)["actions"] is False
