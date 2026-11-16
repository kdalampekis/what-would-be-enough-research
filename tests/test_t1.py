"""T1 single-edit counterfactual flips: generator invariants, metrics, runner path. No network."""

import difflib
import hashlib
import json
import sys
from pathlib import Path

import pytest

from msep.benchmark import t1_flips
from msep.benchmark.schemas import instance_from_record
from msep.eval.experiments import build_variant_jobs
from msep.models.runner import load_results, run_jobs
from msep.oracle import solver
from msep.oracle.brute_force import BruteForce

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import analyze_t1  # noqa: E402
from test_pilot_pipeline import make_records  # noqa: E402


@pytest.fixture(scope="module")
def pairs():
    out = []
    for r in make_records(4):
        p = t1_flips.make_pair(r)
        if p:
            out.append((r, p))
    assert out, "fixture produced no T1 pairs"
    return out


def test_pair_invariants(pairs):
    for src, (A, B) in pairs:
        assert A["prompt_text"] == src["prompt_text"]
        changed = [l for l in difflib.ndiff(A["prompt_text"].splitlines(), B["prompt_text"].splitlines())
                   if l[:1] in "+-"]
        assert len(changed) == 2  # exactly one line replaced
        menu = lambda r: sorted(a["name"] for a in r["state"]["info_actions"] + r["state"]["comp_actions"])  # noqa: E731
        assert menu(A) == menu(B)
        assert ({frozenset(p) for p in A["oracle"]["optimal_plans"]} != {frozenset(p) for p in B["oracle"]["optimal_plans"]}
                or A["oracle"]["resource_class"] != B["oracle"]["resource_class"])
        for m in (A, B):
            st = instance_from_record(m).state
            assert solver.analyze(st).key() == BruteForce(st).analyze().key()
        assert A["t1"]["pair_id"] == B["t1"]["pair_id"] and (A["t1"]["role"], B["t1"]["role"]) == ("A", "B")


def test_generation_is_deterministic(pairs):
    src, (A, B) = pairs[0]
    A2, B2 = t1_flips.make_pair(src)
    assert json.dumps(B, sort_keys=True) == json.dumps(B2, sort_keys=True)


def test_direct_means_drop_rule_works(pairs):
    for _, (_, B) in pairs:
        if B["t1"]["transition"] == "direct":
            assert B["t1"]["drop_rule_ok"]


def _run_mock(t1, agent, raw):
    by_id = {r["instance_id"]: r for r in t1}
    jobs = build_variant_jobs(t1, "t1")
    lookup = {hashlib.sha256(j.prompt.encode()).hexdigest(): (j, by_id[j.instance_id]) for j in jobs}
    run_jobs(jobs, agent, {"provider": "mock", "model_id": agent, "settings": {"agent": agent, "lookup": lookup,
                                                                              "max_tokens": 1}},
             raw, max_calls=len(jobs), concurrency=1, log=lambda *_: None)
    return analyze_t1.pair_rows(t1, load_results(raw, "plan_t1", agent))


def test_metrics_perfect_and_abstaining_agents(pairs, tmp_path):
    t1 = [m for _, p in pairs for m in p]
    perfect = analyze_t1._stats(_run_mock(t1, "oracle_perfect", tmp_path))
    assert perfect["a"] == perfect["b"] == perfect["joint"] == 1
    assert perfect["transition"] in (1, None)
    abstain = analyze_t1._stats(_run_mock(t1, "always_abstain", tmp_path))
    assert abstain["joint"] <= min(abstain["a"], abstain["b"])


def test_missing_responses_count_as_incorrect(pairs):
    t1 = [m for _, p in pairs for m in p]
    rows = analyze_t1.pair_rows(t1, [])
    assert all(r["missing"] and not r["a_ok"] and not r["b_ok"] for r in rows)


def test_run_pilot_t1_requires_pairs_file(tmp_path, capsys):
    from run_pilot import main
    data = tmp_path / "d.jsonl"
    data.write_text("\n".join(json.dumps(r) for r in make_records(1)) + "\n")
    rc = main(["--data", str(data), "--splits", "dev", "--max-families", "1", "--experiments", "t1", "--dry-run"])
    assert rc == 2 and "needs --t1" in capsys.readouterr().out
