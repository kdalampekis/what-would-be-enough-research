"""The realistic planner (B) uses only agent-visible information."""

import ast
from pathlib import Path

import pytest

from msep.controllers import realistic_planner as rp
from msep.controllers.environment import AgentEnvironment, environment_for
from msep.eval.plan_metrics import score
from msep.models.schemas import ModelResponse

from test_pilot_pipeline import make_records

RECS = make_records(5)
FORBIDDEN = {"msep.world.state.Instance", "msep.world.state.LatentWorld", "msep.oracle.minimal_plan",
             "msep.oracle.brute_force", "msep.oracle.solver", "msep.benchmark.families", "msep.benchmark.schemas",
             "msep.controllers.obligation_planner"}


def imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
            out.update(f"{node.module}.{a.name}" for a in node.names)
        elif isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
    return out


def test_planner_module_imports_no_oracle_or_hidden_state():
    src = Path(rp.__file__)
    assert not (imported_names(src) & FORBIDDEN)
    assert not (imported_names(src.parent / "environment.py") - {"msep.benchmark.schemas",
                                                                "msep.benchmark.schemas.instance_from_record"}
                & FORBIDDEN)


def test_environment_exposes_no_world():
    env = environment_for(RECS[3])
    assert not hasattr(env, "world") and not hasattr(env, "instance") and not hasattr(env, "__dict__")


class StrictEnv:
    """Only what an agent may use: the text, execute() and the spend."""

    def __init__(self, env):
        self._env = env

    @property
    def prompt_text(self):
        return self._env.prompt_text

    def execute(self, a):
        return self._env.execute(a)

    @property
    def spent(self):
        return self._env.spent


@pytest.mark.parametrize("i", range(len(RECS)))
def test_runs_on_visible_information_only(i):
    rec = RECS[i]
    o = rec["oracle"]
    trace = rp.EpistemicObligationPlanner().run(StrictEnv(environment_for(rec)))
    if o["resource_class"] == "NEITHER":
        assert trace.outcome == "deferred"
        return
    assert trace.outcome == "answered" and trace.decision == rec["true_target_value"]
    assert trace.total_cost <= (o["optimal_cost"] or 0)


def test_static_plan_is_scored_by_the_oracle_not_trusted():
    for rec in RECS[:22]:
        out = rp.EpistemicObligationPlanner().plan(rec["prompt_text"])
        if out["plan"] is None:
            continue
        resp = ModelResponse(out["state_sufficient"], rec["oracle"]["resource_class"], list(out["plan"]), [], True,
                             "defer", None, "")
        s = score(rec, resp)
        assert s["plan_sufficient"] and s["plan_optimal"]


def test_perturbed_extraction_can_produce_bad_plans_and_scoring_catches_them():
    bad = 0
    planner = rp.EpistemicObligationPlanner(extractor=rp.PerturbedExtractor(rp.ParserExtractor(), rate=0.3, seed=1))
    for rec in RECS:
        if rec["oracle"]["current_sufficient"]:
            continue
        try:
            out = planner.plan(rec["prompt_text"])
        except Exception:
            bad += 1
            continue
        if out["plan"] is None:
            bad += rec["oracle"]["resource_class"] != "NEITHER"
            continue
        resp = ModelResponse(False, rec["oracle"]["resource_class"], list(out["plan"]), [], True, "defer", None, "")
        bad += not score(rec, resp)["plan_optimal"]
    assert bad > 0  # synthetic extraction errors do show up in exact scoring


def test_planner_cannot_compute_certified_values_for_free():
    from msep.world.certified_tasks import OpaqueTaskError
    st = rp.ParserExtractor().extract(RECS[3]["prompt_text"])
    assert st.tasks and all(getattr(t, "opaque", False) for t in st.tasks.values())
    with pytest.raises(OpaqueTaskError):
        next(iter(st.tasks.values())).evaluate()


def test_planner_does_not_touch_environment_internals():
    src = Path(rp.__file__).read_text()
    for forbidden in ("_execute", "_cost_of", "__closure__", "__globals__", "gc.get_referents", "inspect."):
        assert forbidden not in src, forbidden


def _extraction_json(text):
    """What a perfect extractor would return (built from the text only)."""
    import re as _re
    from msep.benchmark.parsing import parse_state
    from msep.world.constraints import render
    st = parse_state(text, opaque_tasks=True)
    names = {i: v.name for i, v in enumerate(st.variables)}
    return {"variables": [{"handle": v.name, "kind": v.kind.value} for v in st.variables if v.name != "Q"],
            "rules": [render(r.formula, names) for r in st.rules],
            "known": [{"handle": names[i], "value": v} for i, v in st.known.items()],
            "actions": [{"name": a.name, "kind": a.resource.value, "cost": a.cost,
                         "reveals": [names[i] for i in a.reveals]} for a in st.actions]}


def test_llm_extractor_condition_runs_offline_with_a_fake_provider():
    import json as _json
    from msep.controllers.llm_extractor import EXTRACTION_SCHEMA, LLMStateExtractor
    from msep.models.providers.base import ProviderResult

    def fake_complete(prompt, schema, name):
        assert schema is EXTRACTION_SCHEMA and "Do not solve it" in prompt
        text = prompt.split("\n\nExtract the formal state")[0]
        return ProviderResult(_json.dumps(_extraction_json(text)), {"fake": True}, {}, {}, "ok")

    planner = rp.EpistemicObligationPlanner(extractor=LLMStateExtractor(fake_complete))
    for rec in RECS[:22]:
        trace = planner.run(StrictEnv(environment_for(rec)))
        if rec["oracle"]["resource_class"] == "NEITHER":
            assert trace.outcome == "deferred"
        else:
            assert trace.outcome == "answered" and trace.decision == rec["true_target_value"]


class RecordingEnv(StrictEnv):
    """Records every value the environment hands out."""

    def __init__(self, env):
        super().__init__(env)
        self.calls = []

    def execute(self, a):
        out = self._env.execute(a)
        self.calls.append((a, dict(out)))
        return out


def test_knowledge_comes_only_from_text_and_executed_actions():
    """No certificate or world value reaches the planner before it executes the permitted action."""
    import re as _re
    for rec in RECS:
        env = RecordingEnv(environment_for(rec))
        planner = rp.EpistemicObligationPlanner()
        initial = rp.ParserExtractor().extract(rec["prompt_text"])
        trace = planner.run(env)
        for action, observed in env.calls:
            # each step returns exactly the handles named in that action's display name
            assert set(observed) == set(_re.findall(r"[FK][0-9]+", action.split("_", 1)[1]))
        learned = {h for _, obs in env.calls for h in obs}
        assert [s["action"] for s in trace.steps] == [a for a, _ in env.calls]
        names = {i: v.name for i, v in enumerate(initial.variables)}
        known_initial = {names[i] for i in initial.known}
        # everything the planner knows at the end came from the text or from an executed action
        assert set(trace.final_known) == known_initial | learned
        assert trace.total_cost == sum(env._env.log[k].cost for k in range(len(env._env.log)))
