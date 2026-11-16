"""Provider interface. Every call returns the full raw response for preservation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProviderResult:
    text: str | None              # the model's final text (JSON expected)
    raw: dict                     # full provider response, as returned
    request: dict                 # exactly what was sent (minus credentials)
    usage: dict = field(default_factory=dict)
    status: str = "ok"            # ok | refusal | truncated | error
    error: str | None = None
    served_model: str | None = None


class Provider:
    name = "base"

    def __init__(self, model_id: str, settings: dict):
        self.model_id = model_id
        self.settings = settings

    def complete(self, prompt: str, schema: dict, schema_name: str) -> ProviderResult:  # pragma: no cover
        raise NotImplementedError
