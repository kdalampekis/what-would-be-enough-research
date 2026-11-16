"""Test double used ONLY by the test suite to exercise the runner and analysis code.

It answers from the oracle (optionally with deterministic errors). Its outputs are
never written under results/ and must never be reported as model results.
"""

from __future__ import annotations

import hashlib
import json

from .base import Provider, ProviderResult


class FakeProvider(Provider):
    name = "fake"

    def __init__(self, model_id: str, settings: dict):
        super().__init__(model_id, settings)
        self.answers = settings["answers"]  # prompt sha256 -> dict answer
        self.error_rate = settings.get("error_rate", 0.0)

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:
        h = hashlib.sha256(prompt.encode()).hexdigest()
        ans = dict(self.answers[h])
        flip = int(h[:8], 16) / 0xFFFFFFFF < self.error_rate
        if flip:
            for k in ("state_sufficient", "plan_sufficient"):
                if k in ans:
                    ans[k] = not ans[k]
            if "plan" in ans:
                ans["plan"] = ans["plan"][:1]
        text = json.dumps(ans)
        usage = {"input_tokens": len(prompt) // 4, "output_tokens": self.settings.get("output_tokens", 200)}
        return ProviderResult(text, {"fake": True, "text": text}, {"prompt_sha256": h}, usage, "ok", None, self.model_id)
