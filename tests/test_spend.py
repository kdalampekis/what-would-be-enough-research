"""Budget guard and per-request cost accounting (test double only; no API calls)."""

import hashlib
import json
import sys
from pathlib import Path

from msep.eval import pilot
from msep.models.runner import load_results, run_jobs, worst_case_cost
from msep.models.spend import Ledger, request_cost, token_usage

from test_pilot_pipeline import make_records, oracle_answer

PRICES = {"input_per_mtok": 2.0, "output_per_mtok": 10.0}


def fake_cfg(jobs, by_id, out_tokens=900):
    answers = {hashlib.sha256(j.prompt.encode()).hexdigest(): oracle_answer(by_id[j.instance_id], j) for j in jobs}
    return {"provider": "fake", "model_id": "fake", "prices": PRICES,
            "settings": {"answers": answers, "output_tokens": out_tokens, "max_tokens": 1000}}


def test_token_usage_normalisation():
    a = token_usage("anthropic", {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 10,
                                  "cache_creation_input_tokens": 0})
    assert a["input_tokens"] == 110 and a["output_tokens"] == 50
    o = token_usage("openai", {"input_tokens": 100, "output_tokens": 300,
                               "output_tokens_details": {"reasoning_tokens": 250}, "input_tokens_details": {"cached_tokens": 0}})
    assert o["output_tokens"] == 300 and o["reasoning_tokens"] == 250
    assert abs(request_cost(PRICES, o) - (100 * 2 + 300 * 10) / 1e6) < 1e-12


def test_budget_hard_stop_never_exceeded(tmp_path):
    recs = make_records(2)
    by_id = {r["instance_id"]: r for r in recs}
    jobs = pilot.build_jobs(recs)
    cfg = fake_cfg(jobs, by_id)
    budget = 10 * worst_case_cost(jobs[0].prompt, cfg)  # room for only ~10 calls
    ledger = Ledger(tmp_path / "ledger.jsonl", budget)
    counts = run_jobs(jobs, "fake", cfg, tmp_path, max_calls=len(jobs), concurrency=4, ledger=ledger, log=lambda *_: None)
    assert counts["budget_stopped"] > 0 and counts["ok"] < len(jobs)
    spent = sum(json.loads(l)["cost_usd"] for l in (tmp_path / "ledger.jsonl").read_text().splitlines())
    assert spent <= budget
    # a new ledger on the same file continues from the recorded spend
    assert abs(Ledger(tmp_path / "ledger.jsonl", budget).spent - spent) < 1e-9
    rec = load_results(tmp_path, "plan", "fake")[0]
    assert rec["tokens"]["output_tokens"] == 900 and rec["cost_usd"] > 0 and rec["prices"] == PRICES


def test_driver_refuses_full_split_and_unpriced_models(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from run_pilot import main
    recs = make_records(1)
    data = tmp_path / "d.jsonl"
    data.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    cfg = tmp_path / "m.json"
    cfg.write_text(json.dumps({"nopx": {"provider": "fake", "model_id": "x", "prices": None,
                                        "settings": {"answers": {}, "max_tokens": 1000}}}))
    base = ["--data", str(data), "--splits", "dev", "--models", "nopx", "--models-config", str(cfg),
            "--raw", str(tmp_path / "raw"), "--out", str(tmp_path / "out"), "--max-calls", "5"]
    assert main(base) == 2                              # no --max-families
    assert main(base + ["--max-families", "1"]) == 2    # no prices
    assert main(base[:-2] + ["--splits", "test", "--max-families", "1"]) == 2  # test split refused
