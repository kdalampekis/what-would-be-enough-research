"""Stable schemas, config checks, run log, retry cap. No network."""

import hashlib
import json

from msep.controllers.llm_extractor import EXTRACTION_SCHEMA
from msep.models.config_check import check_model
from msep.models.runner import MAX_ERROR_ATTEMPTS, Job, raw_path, run_jobs
from msep.models.providers.base import Provider, ProviderResult
from msep.models.schemas import CAPABILITY_SCHEMA, DECISION_SCHEMA, JUDGMENT_SCHEMA, PLAN_SCHEMA, SCHEMA_VERSION

SNAPSHOT = {"msep-schemas-v1": {"plan": "e4d1ff144bcd8b73", "judgment": "18185dbb3dddcd7d",
                                "decision": "71abcc685dd83e0d", "extraction": "285bec19d0eb4eb1"},
            "msep-schemas-v2": {"plan": "e4d1ff144bcd8b73", "judgment": "18185dbb3dddcd7d",
                                "decision": "71abcc685dd83e0d", "extraction": "285bec19d0eb4eb1",
                                "capability": "f125437ef31d2b29"}}


def h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()[:16]


def test_schemas_match_their_version_snapshot():
    snap = SNAPSHOT[SCHEMA_VERSION]
    assert {"plan": h(PLAN_SCHEMA), "judgment": h(JUDGMENT_SCHEMA), "decision": h(DECISION_SCHEMA),
            "extraction": h(EXTRACTION_SCHEMA), "capability": h(CAPABILITY_SCHEMA)} == snap, \
        "schema changed: bump SCHEMA_VERSION and add a snapshot"


def test_strict_schema_subset():
    def walk(s):
        if s.get("type") == "object":
            assert s.get("additionalProperties") is False and set(s["required"]) == set(s["properties"])
            for v in s["properties"].values():
                walk(v)
        if s.get("type") == "array":
            walk(s["items"])
        assert "minimum" not in s and "maximum" not in s
    for s in (PLAN_SCHEMA, JUDGMENT_SCHEMA, DECISION_SCHEMA, EXTRACTION_SCHEMA, CAPABILITY_SCHEMA):
        walk(s)


def test_config_checks():
    base = {"provider": "anthropic", "model_id": "claude-sonnet-5-5", "settings": {"max_tokens": 1000, "effort": "medium"},
            "prices": {"input_per_mtok": 2.0, "output_per_mtok": 10.0}}
    e, w = check_model("c", base, require_keys=False)
    assert not e and any("thinking" in x for x in w)
    e, _ = check_model("c", {**base, "settings": {"max_tokens": 1000, "temperature": 0}}, require_keys=False)
    assert any("rejected" in x for x in e)
    e, _ = check_model("c", {**base, "prices": None}, require_keys=False)
    assert any("prices" in x for x in e)
    e, _ = check_model("c", base, require_keys=True)
    assert any("ANTHROPIC_API_KEY" in x for x in e) or not e


class Failing(Provider):
    name = "failing"

    def complete(self, prompt, schema, name):
        return ProviderResult(None, {"error": "x"}, {}, {}, "error", "500: x")


def test_retry_cap_and_run_log(tmp_path):
    jobs = [Job("plan", "i1", "f1", "detection_controlled", "PROMPT")]
    cfg = {"provider": "failing", "model_id": "x", "settings": {"max_tokens": 10}}
    for _ in range(MAX_ERROR_ATTEMPTS):
        run_jobs(jobs, "m", cfg, tmp_path, max_calls=1, provider=Failing("x", {}), log=lambda *_: None)
    c = run_jobs(jobs, "m", cfg, tmp_path, max_calls=1, provider=Failing("x", {}), log=lambda *_: None)
    assert c["retry_cap_reached"] == 1 and c["error"] == 0
    events = [json.loads(l) for l in (tmp_path / "run_log.jsonl").read_text().splitlines()]
    assert {e["event"] for e in events} >= {"batch_start", "job", "batch_end"}
    assert not raw_path(tmp_path, jobs[0], "m").exists()  # failed attempts are kept separately


def test_default_budget_is_zero_and_blocks_real_runs(tmp_path):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from run_pilot import main
    from test_pilot_pipeline import make_records
    data = tmp_path / "d.jsonl"
    data.write_text("\n".join(json.dumps(r) for r in make_records(1)) + "\n")
    rc = main(["--data", str(data), "--splits", "dev", "--max-families", "1", "--max-calls", "5",
               "--raw", str(tmp_path / "raw"), "--out", str(tmp_path / "out")])
    assert rc == 2 and not (tmp_path / "raw").exists()


def test_overrides_apply_to_dry_run(tmp_path, capsys):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from run_pilot import main
    from test_pilot_pipeline import make_records
    data = tmp_path / "d.jsonl"
    data.write_text("\n".join(json.dumps(r) for r in make_records(1)) + "\n")
    main(["--data", str(data), "--splits", "dev", "--max-families", "1", "--dry-run",
          "--override", "claude-sonnet-5-5.settings.max_tokens=4000", "--models", "claude-sonnet-5-5"])
    out = capsys.readouterr().out
    assert "output_tokens_assumed" in out and "4000" in out.split("output_tokens_assumed")[1][:20]


def test_rate_limited_calls_wait_and_retry_without_recording_an_attempt(tmp_path, monkeypatch):
    from msep.models import runner
    from msep.models.providers.base import ProviderResult
    from test_pilot_pipeline import make_records
    from msep.eval import pilot

    class Flaky:
        def __init__(self):
            self.calls = 0

        def complete(self, prompt, schema, name):
            self.calls += 1
            if self.calls <= 2:
                return ProviderResult(None, {"error": "x"}, {}, status="error",
                                      error="429: Error code: 429 - rate_limit_exceeded; retry after 60 seconds")
            return ProviderResult('{"state_sufficient": true, "resource_class": "ALREADY_SUFFICIENT", "plan": [], '
                                  '"stop_after_plan": true, "decision": "true", "confidence": 1, "short_justification": "x"}',
                                  {}, {}, status="ok")

    monkeypatch.setattr(runner, "RATE_LIMIT_WAIT_S", 0)
    monkeypatch.setattr(runner.random, "uniform", lambda a, b: 0)
    job = [j for j in pilot.build_jobs(make_records(1)) if j.pool == "plan"][0]
    prov = Flaky()
    counts = runner.run_jobs([job], "m", {"provider": "fake", "model_id": "m", "settings": {}, "prices": None},
                             tmp_path, max_calls=1, provider=prov, log=lambda *_: None)
    assert prov.calls == 3 and counts["ok"] == 1
    assert not list(tmp_path.rglob("*.attempt*.json"))  # rate limits are not failed attempts
