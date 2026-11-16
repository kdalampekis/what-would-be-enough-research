"""Shallow heuristic baselines: visible-only, and they expose the v2 shortcut."""

import ast
from pathlib import Path

from msep.agents import heuristics
from msep.agents.heuristics import plan_for
from msep.eval.plan_metrics import score
from msep.models.schemas import ModelResponse

from test_pilot_pipeline import make_records


def optimal_rate(h, recs):
    ok = 0
    for r in recs:
        p = plan_for(h, r["prompt_text"])
        s = score(r, ModelResponse(p["state_sufficient"], p["resource_class"], p["plan"], [], True, p["decision"], None, ""))
        ok += s["class_correct"] and (s["plan_optimal"] or (r["oracle"]["resource_class"] == "NEITHER" and not p["plan"]))
    return ok / len(recs)


def test_h1p_solves_template_v2():
    assert optimal_rate("h1p", make_records(4)) == 1.0


def test_heuristics_read_only_the_text():
    tree = ast.parse(Path(heuristics.__file__).read_text())
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not mods & {"msep.oracle.minimal_plan", "msep.oracle.solver", "msep.benchmark.schemas",
                       "msep.benchmark.families", "msep.benchmark.template_v3"}
    src = Path(heuristics.__file__).read_text()
    assert 'rec["oracle"]' not in src and "latent_world" not in src
