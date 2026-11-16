"""Adaption provider, config rules, currency separation and .env loading. No network."""

import json
import os
from pathlib import Path

import pytest

adaption = pytest.importorskip("adaption")

from adaption.types.response import Response  # noqa: E402

from msep.envfile import load_env  # noqa: E402
from msep.models.config_check import check_all  # noqa: E402
from msep.models.providers.adaption_provider import AdaptionProvider  # noqa: E402
from msep.models.runner import load_models  # noqa: E402
from msep.models.spend import request_cost, token_usage  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODELS = load_models(ROOT / "configs" / "models.json")
ADAPTION_KEYS = [k for k, v in MODELS.items() if v["provider"] == "adaption"]


def _resp(status="completed", text='{"plan": []}', content_type="output_text", incomplete=None):
    content = [{"type": content_type, "text": text}] if content_type == "output_text" else \
        [{"type": "refusal", "refusal": "no"}]
    return Response.model_validate({
        "id": "resp_1", "object": "response", "status": status, "model": "glm-5.2",
        "output": [{"type": "reasoning", "summary": []}, {"type": "message", "role": "assistant", "content": content}],
        "output_text": text if content_type == "output_text" else "",
        "incomplete_details": incomplete,
        "usage": {"input_tokens": 1200, "output_tokens": 300, "total_tokens": 1500,
                  "output_tokens_details": {"reasoning_tokens": 200}, "input_tokens_details": {"cached_tokens": 0}}})


from adaption.types.response_stream_event import ResponseStreamEvent  # noqa: E402


class _Stream:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(self.events)


def _events(resp, terminal=True):
    evs = [ResponseStreamEvent(type="response.created"),
           ResponseStreamEvent(type="response.output_text.delta", delta=resp.output_text)]
    if terminal:
        kind = {"completed": "response.completed", "incomplete": "response.incomplete",
                "failed": "response.failed"}[resp.status]
        evs.append(ResponseStreamEvent(type=kind, response=resp))
    return evs


class _Client:
    def __init__(self, resp, terminal=True):
        self.resp, self.sent, self.terminal = resp, None, terminal
        self.responses = self

    def create(self, **kw):
        self.sent = kw
        if kw.get("stream"):
            return _Stream(_events(self.resp, self.terminal))
        return self.resp


def _provider(resp, stream=True, terminal=True):
    cfg = MODELS["adaption-glm-5.2"]
    return AdaptionProvider(cfg["model_id"], {**cfg["settings"], "stream": stream}, client=_Client(resp, terminal))


def test_seven_models_configured_with_credit_prices():
    assert len({MODELS[k]["model_id"] for k in ADAPTION_KEYS}) == 7
    for k in ADAPTION_KEYS:
        assert "/" not in k  # keys become directory names
        assert MODELS[k]["prices"]["currency"] == "credits"
        assert MODELS[k]["settings"]["temperature"] == 0.0


def test_config_streams_with_16k_cap_and_two_retries():
    base = {"max_tokens": 16000, "temperature": 0.0, "stream": True, "max_retries": 2}
    for k in ADAPTION_KEYS:
        if k.endswith("-32k"):  # diagnostic conditions: only the cap differs
            assert MODELS[k]["settings"] == {**base, "max_tokens": 32000}
        elif k.endswith("-schema"):  # diagnostic conditions: only the structured mode differs
            assert MODELS[k]["settings"] == {**base, "structured": "function_tool"}
            assert MODELS[k]["model_id"] == MODELS[k.removesuffix("-schema")]["model_id"]
        else:
            assert MODELS[k]["settings"] == base


@pytest.mark.parametrize("stream", [True, False])
def test_request_shape_and_ok_result(stream):
    p = _provider(_resp(), stream=stream)
    res = p.complete("prompt text", {"type": "object"}, "plan")
    sent = p.client.sent
    expected = {"model": "glm-5.2", "input": "prompt text", "max_output_tokens": 16000, "store": False,
                "temperature": 0.0}
    assert sent == ({**expected, "stream": True} if stream else expected)
    assert res.request == sent
    assert res.status == "ok" and res.text == '{"plan": []}' and res.served_model == "glm-5.2"
    assert res.raw["output"][0]["type"] == "reasoning"  # raw response preserved in full
    assert "api_key" not in json.dumps(res.request)


def test_stream_without_final_event_is_an_error_keeping_the_text():
    r = _provider(_resp(), terminal=False).complete("x", {}, "plan")
    assert r.status == "error" and "without a final response" in r.error
    assert r.raw["streamed_text"] == '{"plan": []}'


@pytest.mark.parametrize("stream", [True, False])
def test_incomplete_is_truncated_and_refusal_detected(stream):
    r = _provider(_resp(status="incomplete", text='{"pl', incomplete={"reason": "max_output_tokens"}), stream).complete("x", {}, "plan")
    assert r.status == "truncated" and "max_output_tokens" in r.error
    r = _provider(_resp(content_type="refusal"), stream).complete("x", {}, "plan")
    assert r.status == "refusal" and r.text is None
    r = _provider(_resp(status="failed", text=""), stream).complete("x", {}, "plan")
    assert r.status == "error"


def test_usage_normalised_and_costed_in_credits():
    raw_usage = _resp().model_dump(mode="json")["usage"]
    t = token_usage("adaption", raw_usage)
    assert t["input_tokens"] == 1200 and t["output_tokens"] == 300 and t["reasoning_tokens"] == 200
    cost = request_cost(MODELS["adaption-glm-5.2"]["prices"], t)
    assert cost == pytest.approx(1200 / 1e6 * 1.40 + 300 / 1e6 * 4.40)


def test_config_check_requires_key_and_blocks_mixed_currencies(monkeypatch):
    monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
    errs, warns = check_all(MODELS, ["adaption-glm-5.2"])
    assert any("ADAPTION_API_KEY" in e for e in errs)
    monkeypatch.setenv("ADAPTION_API_KEY", "[redacted]")
    errs, warns = check_all(MODELS, ["adaption-glm-5.2", "adaption-qwen3.5-397b"])
    assert errs == [] and any("smoke" in w for w in warns)
    errs, _ = check_all(MODELS, ["adaption-glm-5.2", "claude-sonnet-5-5"], require_keys=False)
    assert any("different currencies" in e for e in errs)


def test_env_file_loading(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text('# comment\nexport MSEP_T1="abc"\nMSEP_T2=x=y\n\nMSEP_T3=keep\n')
    monkeypatch.delenv("MSEP_T1", raising=False)
    monkeypatch.delenv("MSEP_T2", raising=False)
    monkeypatch.setenv("MSEP_T3", "already")
    assert sorted(load_env(f)) == ["MSEP_T1", "MSEP_T2"]
    assert os.environ["MSEP_T1"] == "abc" and os.environ["MSEP_T2"] == "x=y" and os.environ["MSEP_T3"] == "already"
    assert load_env(tmp_path / "missing") == []


def test_latest_record_reads_newest_failed_attempt(tmp_path):
    from msep.models.runner import latest_record, raw_path
    from types import SimpleNamespace
    job = SimpleNamespace(pool="plan", job_id=lambda mk: f"j1-{mk}")
    p = raw_path(tmp_path, job, "m")
    p.parent.mkdir(parents=True)
    assert latest_record(tmp_path, job, "m") is None
    for k in (1, 2, 10):
        p.with_suffix(f".attempt{k}.json").write_text(json.dumps({"status": "error", "n": k}))
    assert latest_record(tmp_path, job, "m")["n"] == 10
    p.write_text(json.dumps({"status": "ok", "n": 0}))
    assert latest_record(tmp_path, job, "m")["n"] == 0


def test_usage_summary_reports_currency_and_served_model():
    from msep.eval.pilot import usage_summary
    rs = [{"status": "ok", "pool": "plan", "tokens": {"input_tokens": 10, "output_tokens": 5}, "cost_usd": 0.5,
           "prices": {"currency": "credits"}, "served_model": "qwen3.5-397b-a17b-nvfp4"}]
    u = usage_summary(rs)["all"]
    assert u["currency"] == "credits" and u["served_models"] == {"qwen3.5-397b-a17b-nvfp4": 1}
    assert usage_summary([{**rs[0], "prices": {"input_per_mtok": 1}}])["all"]["currency"] == "usd"


def test_cached_results_with_other_settings_block_the_run(tmp_path):
    from types import SimpleNamespace
    from msep.models.runner import raw_path, run_jobs
    job = SimpleNamespace(pool="plan", job_id=lambda mk: f"j1-{mk}", prompt="p")
    cfg = {"provider": "fake", "model_id": "m", "settings": {"max_tokens": 32000}}
    p = raw_path(tmp_path, job, "glm")
    p.parent.mkdir(parents=True)
    # an old-style record (no "settings") made at a 16k cap, status truncated (counts as done)
    p.write_text(json.dumps({"status": "truncated", "request": {"max_output_tokens": 16000}}))
    with pytest.raises(RuntimeError, match="different settings"):
        run_jobs([job], "glm", cfg, tmp_path, max_calls=1)
    p.write_text(json.dumps({"status": "ok", "settings": {"max_tokens": 16000, "stream": True}}))
    with pytest.raises(RuntimeError, match="own model key"):
        run_jobs([job], "glm", cfg, tmp_path, max_calls=1)
    p.write_text(json.dumps({"status": "ok", "settings": {"max_tokens": 32000}}))
    assert run_jobs([job], "glm", cfg, tmp_path, max_calls=0, provider=object())["skipped_done"] == 1


def _fn_resp(arguments='{"plan": []}', with_call=True, text=""):
    out = [{"type": "reasoning", "summary": []}]
    if with_call:
        out.append({"type": "function_call", "name": "msep_plan", "arguments": arguments, "call_id": "c1"})
    if text:
        out.append({"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": text}]})
    return Response.model_validate({
        "id": "resp_2", "object": "response", "status": "completed", "model": "gemma-4-26b-a4b-it",
        "output": out, "output_text": text, "incomplete_details": None,
        "usage": {"input_tokens": 1000, "output_tokens": 100, "total_tokens": 1100}})


def _structured(resp, stream):
    cfg = MODELS["adaption-gemma-4-26b-a4b-it-schema"]
    return AdaptionProvider(cfg["model_id"], {**cfg["settings"], "stream": stream}, client=_Client(resp))


@pytest.mark.parametrize("stream", [True, False])
def test_structured_mode_forces_schema_tool_and_parses_arguments(stream):
    schema = {"type": "object", "properties": {"plan": {"type": "array"}}}
    p = _structured(_fn_resp(), stream)
    res = p.complete("prompt text", schema, "msep_plan")
    sent = p.client.sent
    assert sent["tools"] == [{"type": "function", "name": "msep_plan", "parameters": schema, "strict": True,
                              "description": "Submit your answer as the arguments of this call."}]
    assert sent["tool_choice"] == {"type": "function", "name": "msep_plan"}
    assert res.status == "ok" and res.text == '{"plan": []}'  # the call's arguments, not the message text


def test_structured_mode_without_the_call_yields_no_text():
    p = _structured(_fn_resp(with_call=False, text='{"plan": []}'), stream=False)
    res = p.complete("prompt text", {"type": "object"}, "msep_plan")
    assert res.status == "ok" and res.text is None  # scored as unparsed ("no text"), never taken from prose


def test_default_mode_sends_no_tools():
    p = _provider(_resp(), stream=False)
    p.complete("prompt text", {"type": "object"}, "plan")
    assert "tools" not in p.client.sent and "tool_choice" not in p.client.sent


def test_unknown_structured_mode_is_rejected():
    cfg = MODELS["adaption-gemma-4-26b-a4b-it"]
    p = AdaptionProvider(cfg["model_id"], {**cfg["settings"], "structured": "json_mode"}, client=_Client(_resp()))
    with pytest.raises(ValueError):
        p.complete("prompt text", {"type": "object"}, "plan")


class _BrokenStream(_Stream):
    def __iter__(self):
        yield ResponseStreamEvent(type="response.created")
        import httpx
        raise httpx.RemoteProtocolError("peer closed connection without sending complete message body")


def test_dropped_stream_is_a_failed_call_not_a_crash():
    import httpx  # noqa: F401
    p = _provider(_resp(), stream=True)
    p.client.create = lambda **kw: _BrokenStream([])
    res = p.complete("prompt text", {"type": "object"}, "plan")
    assert res.status == "error" and res.error.startswith("transport:")
