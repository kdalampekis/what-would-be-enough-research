"""Claude via the official Anthropic Python SDK (Messages API, structured outputs).

- Credentials: ANTHROPIC_API_KEY only (the experiment key). The base URL is the
  public API unless MSEP_ANTHROPIC_BASE_URL is set, so a session-level
  ANTHROPIC_BASE_URL is never picked up by accident.
- Structured output: output_config.format json_schema.
- Sampling: Claude Sonnet 5.5 rejects non-default temperature, so no sampling
  parameter is sent; runs are recorded as non-deterministic.
- Refusal fallbacks are deliberately NOT enabled: a fallback would answer with a
  different model and contaminate the evaluation. Refusals are recorded as such.
"""

from __future__ import annotations

import os

import anthropic

from .base import Provider, ProviderResult


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, model_id: str, settings: dict):
        super().__init__(model_id, settings)
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set (add it as an environment secret)")
        self.client = anthropic.Anthropic(
            api_key=key,
            base_url=os.environ.get("MSEP_ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            max_retries=settings.get("max_retries", 5),
            timeout=settings.get("timeout_s", 600.0),
        )

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:
        output_config: dict = {"format": {"type": "json_schema", "schema": schema}}
        if self.settings.get("effort"):
            output_config["effort"] = self.settings["effort"]
        request = {"model": self.model_id, "max_tokens": self.settings.get("max_tokens", 16000),
                   "messages": [{"role": "user", "content": prompt}], "output_config": output_config}
        try:
            resp = self.client.messages.create(**request)
        except anthropic.BadRequestError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"400: {e}")
        except anthropic.APIStatusError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"{e.status_code}: {e}")
        except anthropic.APIConnectionError as e:
            return ProviderResult(None, {"error": str(e)}, request, status="error", error=f"connection: {e}")
        raw = resp.model_dump(mode="json")
        usage = raw.get("usage") or {}
        if resp.stop_reason == "refusal":
            return ProviderResult(None, raw, request, usage, "refusal", str(raw.get("stop_details")), resp.model)
        text = next((b.text for b in resp.content if b.type == "text"), None)
        status = "truncated" if resp.stop_reason == "max_tokens" else "ok"
        return ProviderResult(text, raw, request, usage, status, None, resp.model)
