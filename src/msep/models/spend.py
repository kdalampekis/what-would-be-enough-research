"""Per-request cost accounting and a hard budget stop.

Cost of a request = usage reported by the provider x the model's configured prices.
Reasoning tokens are billed as output on both providers and are included in
output_tokens. Cache discounts are ignored (the estimate errs high).

The ledger (spend_ledger.jsonl) is append-only and shared across models and runs.
Before every call the runner reserves the worst case for that call
(estimated input + max output tokens); a call whose worst case would take the
cumulative total over the budget is not made.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path


class BudgetExceeded(RuntimeError):
    pass


def token_usage(provider: str, usage: dict) -> dict:
    """Normalise provider usage to input / output / reasoning / cached token counts."""
    usage = usage or {}
    if provider == "anthropic":
        return {"input_tokens": int(usage.get("input_tokens") or 0)
                + int(usage.get("cache_creation_input_tokens") or 0) + int(usage.get("cache_read_input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "reasoning_tokens": None,  # included in output_tokens; not reported separately
                "cached_input_tokens": int(usage.get("cache_read_input_tokens") or 0)}
    if provider in ("openai", "adaption"):
        out_d = usage.get("output_tokens_details") or {}
        in_d = usage.get("input_tokens_details") or {}
        return {"input_tokens": int(usage.get("input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "reasoning_tokens": out_d.get("reasoning_tokens"),
                "cached_input_tokens": in_d.get("cached_tokens")}
    # any other provider (the test double): plain input/output counts; never silently zero
    return {"input_tokens": int(usage.get("input_tokens") or 0), "output_tokens": int(usage.get("output_tokens") or 0),
            "reasoning_tokens": None, "cached_input_tokens": None}


def request_cost(prices: dict, tokens: dict) -> float:
    return (tokens["input_tokens"] / 1e6 * prices["input_per_mtok"]
            + tokens["output_tokens"] / 1e6 * prices["output_per_mtok"])


class Ledger:
    def __init__(self, path: Path, budget_usd: float):
        self.path = Path(path)
        self.budget = float(budget_usd)
        self.lock = threading.Lock()
        self.spent = 0.0
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                if line.strip():
                    self.spent += float(json.loads(line)["cost_usd"])
        self.reserved = 0.0

    def reserve(self, worst_case: float) -> None:
        with self.lock:
            if self.spent + self.reserved + worst_case > self.budget:
                raise BudgetExceeded(
                    f"budget ${self.budget:.2f}: spent ${self.spent:.2f}, reserved ${self.reserved:.2f}, "
                    f"next call up to ${worst_case:.4f}")
            self.reserved += worst_case

    def settle(self, worst_case: float, entry: dict) -> None:
        with self.lock:
            self.reserved -= worst_case
            self.spent += float(entry["cost_usd"])
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a") as fh:
                fh.write(json.dumps(entry) + "\n")
