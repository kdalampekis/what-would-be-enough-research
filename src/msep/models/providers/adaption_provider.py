"""Open-weight models hosted by Adaption, via the official `adaption` Python SDK (Responses API).

Written against `adaption` 0.19.0 from PyPI (read from the package source: the
documentation site was unreachable from the build environment). No live call has
been made yet; run `python experiments/run_pilot.py ... --smoke` first.

- Credentials: ADAPTION_API_KEY. Base URL: the SDK default unless ADAPTION_BASE_URL is set.
- Structured output: `responses.create` 0.19.0 has NO JSON-schema parameter. The
  prompt already ends with "Answer with one JSON object and nothing else" and the
  parser extracts the first JSON object from the text, so the prompt is identical
  to the other providers; only schema enforcement differs. Parse failures are
  counted and reported, never repaired.
- Streaming (settings.stream, on by default in the config): a non-streamed glm-5.2 call hit a
  504 gateway timeout on 2026-11-13; streaming keeps the connection busy while the model reasons.
  Background mode is not an option: SDK 0.19.0 accepts only background=false.
- Retries: SDK retries 5xx and connection errors (max_retries, 2 here); the runner adds its own
  per-job cap (MAX_ERROR_ATTEMPTS).
- Sampling: temperature from the config (0.0 for determinism where the backend honours it).
- Reasoning: the SDK exposes no reasoning/effort control. Reasoning items, if any, are kept
  in the raw response; only the `output_text` parts are parsed.
- Prices are in Adaption credits, not dollars (the config sets "currency": "credits").
- Constrained output (settings.structured = "function_tool", off by default; added 2026-11-13):
  the SDK has no response_format/text.format parameter, but it forwards any other
  OpenAI-compatible Responses tool to the model provider and a named tool_choice demands
  that call. So the job's JSON schema is sent as the parameters of one function tool
  (strict), the call is forced, and the function call's `arguments` string is parsed
  instead of the message text. Whether the backend actually constrains decoding to the
  schema is not documented; measure it, do not assume it.
"""

from __future__ import annotations

import os

import adaption
import httpx

from .base import Provider, ProviderResult


class AdaptionProvider(Provider):
    name = "adaption"

    def __init__(self, model_id: str, settings: dict, client=None):
        super().__init__(model_id, settings)
        if client is not None:  # tests inject a double
            self.client = client
            return
        key = os.environ.get("ADAPTION_API_KEY")
        if not key:
            raise RuntimeError("ADAPTION_API_KEY is not set (put it in .env or the environment)")
        self.client = adaption.Adaption(api_key=key, max_retries=settings.get("max_retries", 5),
                                        timeout=settings.get("timeout_s", 600.0))

    def _stream(self, request: dict):
        """Consume the event stream; return (final Response or None, streamed text, last event type, error)."""
        final, deltas, last_type, err = None, [], None, None
        with self.client.responses.create(**request, stream=True) as stream:
            for ev in stream:
                last_type = ev.type
                if ev.type == "response.output_text.delta" and ev.delta:
                    deltas.append(ev.delta)
                if ev.response is not None and ev.type in ("response.completed", "response.incomplete",
                                                            "response.failed", "response.cancelled"):
                    final = ev.response
                if ev.type == "error":
                    err = ev.model_dump(mode="json")
        return final, "".join(deltas), last_type, err

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:
        request = {"model": self.model_id, "input": prompt,
                   "max_output_tokens": self.settings.get("max_tokens", 8000), "store": False}
        if "temperature" in self.settings:
            request["temperature"] = self.settings["temperature"]
        structured = self.settings.get("structured")
        if structured not in (None, "function_tool"):
            raise ValueError(f"unknown structured mode {structured!r}")
        if structured == "function_tool":
            request["tools"] = [{"type": "function", "name": schema_name, "parameters": schema, "strict": True,
                                 "description": "Submit your answer as the arguments of this call."}]
            request["tool_choice"] = {"type": "function", "name": schema_name}
        streaming = bool(self.settings.get("stream"))
        sent = {**request, "stream": True} if streaming else request
        try:
            if streaming:
                resp, text, last_type, err = self._stream(request)
                if resp is None:  # stream ended without a terminal response event
                    raw = {"streamed_text": text, "last_event": last_type, "error_event": err}
                    return ProviderResult(None, raw, sent, status="error",
                                          error=f"stream ended without a final response (last event {last_type}): {err}")
            else:
                resp = self.client.responses.create(**request)
        except adaption.BadRequestError as e:
            return ProviderResult(None, {"error": str(e)}, sent, status="error", error=f"400: {e}")
        except adaption.APIStatusError as e:
            return ProviderResult(None, {"error": str(e)}, sent, status="error", error=f"{e.status_code}: {e}")
        except adaption.APIConnectionError as e:
            return ProviderResult(None, {"error": str(e)}, sent, status="error", error=f"connection: {e}")
        except httpx.HTTPError as e:  # e.g. the server drops a stream mid-body (seen 2026-11-13): not wrapped by the SDK
            return ProviderResult(None, {"error": repr(e)}, sent, status="error", error=f"transport: {e!r}")
        request = sent
        raw = resp.model_dump(mode="json")
        usage = raw.get("usage") or {}
        if resp.status in ("failed", "cancelled"):
            return ProviderResult(None, raw, request, usage, "error", str(raw.get("error")), resp.model)
        text = resp.output_text
        if structured == "function_tool":  # the answer is the forced call's arguments; no call -> no text
            calls = [i for i in raw.get("output") or [] if i.get("type") == "function_call" and i.get("name") == schema_name]
            text = calls[-1].get("arguments") if calls else None
        if resp.status == "incomplete":
            return ProviderResult(text or None, raw, request, usage, "truncated",
                                  str(raw.get("incomplete_details")), resp.model)
        refusal = any(c.get("type") == "refusal" for item in raw.get("output", []) for c in (item.get("content") or []))
        if refusal and not text:
            return ProviderResult(None, raw, request, usage, "refusal", "refusal content item", resp.model)
        return ProviderResult(text, raw, request, usage, "ok", None, resp.model)
