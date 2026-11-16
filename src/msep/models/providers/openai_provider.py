"""OpenAI models via the official openai Python SDK (Responses API, strict JSON schema).

UNVERIFIED: the model ID and parameter support for GPT-5.6 Sol could not be
checked against OpenAI's documentation from this environment (host blocked).
Run `python experiments/run_pilot.py --smoke` before any pilot: it makes one call
per model and stops on any error. No sampling parameters are sent unless the
model config sets them.
"""

from __future__ import annotations

import os

import openai

from .base import Provider, ProviderResult


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, model_id: str, settings: dict):
        super().__init__(model_id, settings)
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set (add it as an environment secret)")
        self.client = openai.OpenAI(api_key=key, max_retries=settings.get("max_retries", 5),
                                    timeout=settings.get("timeout_s", 600.0))

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:
        request = {"model": self.model_id, "input": prompt,
                   "max_output_tokens": self.settings.get("max_tokens", 16000),
                   "text": {"format": {"type": "json_schema", "name": schema_name, "schema": schema, "strict": True}}}
        if self.settings.get("reasoning_effort"):
            request["reasoning"] = {"effort": self.settings["reasoning_effort"]}
        if "temperature" in self.settings:
            request["temperature"] = self.settings["temperature"]
        try:
            resp = self.client.responses.create(**request)
        except openai.BadRequestError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"400: {e}")
        except openai.APIStatusError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"{e.status_code}: {e}")
        except openai.APIConnectionError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"connection: {e}")
        raw = resp.model_dump(mode="json")
        usage = raw.get("usage") or {}
        if resp.status == "incomplete":
            return ProviderResult(resp.output_text or None, raw, request, usage, "truncated",
                                  str(raw.get("incomplete_details")), resp.model)
        refusal = any(c.get("type") == "refusal" for item in raw.get("output", []) for c in (item.get("content") or []))
        if refusal:
            return ProviderResult(None, raw, request, usage, "refusal", "refusal content item", resp.model)
        return ProviderResult(resp.output_text, raw, request, usage, "ok", None, resp.model)
