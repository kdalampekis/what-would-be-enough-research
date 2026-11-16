"""Provider that answers with a SYNTHETIC mock agent (agents/mock.py). No network.

It looks up the job and record by the prompt hash, so it goes through exactly
the same runner path as a real provider (caching, raw logging, ledger)."""

from __future__ import annotations

import hashlib
import json

from msep.agents import heuristics
from msep.agents.mock import respond as mock_respond

from .base import Provider, ProviderResult


class MockProvider(Provider):
    name = "mock"

    def __init__(self, model_id: str, settings: dict):
        super().__init__(model_id, settings)
        self.agent = settings["agent"]
        self.lookup = settings["lookup"]  # prompt sha256 -> (job, record)

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:
        h = hashlib.sha256(prompt.encode()).hexdigest()
        job, rec = self.lookup[h]
        fn = heuristics.respond if self.agent in heuristics.HEURISTICS else mock_respond
        text = json.dumps(fn(self.agent, job, rec))
        synthetic = self.agent not in heuristics.HEURISTICS  # heuristics are real (non-LLM) baselines
        return ProviderResult(text, {"synthetic": synthetic, "agent": self.agent, "text": text},
                              {"prompt_sha256": h, "synthetic": True}, {"input_tokens": 0, "output_tokens": 0},
                              "ok", None, f"mock:{self.agent}")
