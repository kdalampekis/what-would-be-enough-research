"""Model configuration checks before any real run. No network, no API call.

Errors block a run; warnings are printed. Provider rules come from documentation
read in this project (Claude API reference, cached 2026-10-06). OpenAI rules are
UNVERIFIED (the OpenAI documentation was unreachable from the build environment).
"""

from __future__ import annotations

import os

ANTHROPIC_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-1", "claude-opus-5",
                    "claude-sonnet-5"}
ANTHROPIC_EFFORT = {"low", "medium", "high", "xhigh", "max"}
OPENAI_EFFORT = {"minimal", "low", "medium", "high"}  # unverified
SAMPLING = {"temperature", "top_p", "top_k"}


def check_model(key: str, cfg: dict, require_keys: bool = True) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    prov = cfg.get("provider")
    st = cfg.get("settings", {})
    if prov not in ("anthropic", "openai", "adaption", "mock", "fake"):
        errors.append(f"{key}: unknown provider {prov!r}")
    if not cfg.get("model_id"):
        errors.append(f"{key}: model_id missing")
    if not isinstance(st.get("max_tokens"), int) or st["max_tokens"] < 1:
        errors.append(f"{key}: settings.max_tokens must be a positive integer")
    prices = cfg.get("prices")
    if prov in ("anthropic", "openai", "adaption"):
        if not prices or not all(isinstance(prices.get(k), (int, float)) for k in ("input_per_mtok", "output_per_mtok")):
            errors.append(f"{key}: prices missing; the budget guard cannot run")
    if prov == "anthropic":
        if cfg.get("model_id") not in ANTHROPIC_MODELS:
            warnings.append(f"{key}: model_id {cfg.get('model_id')!r} not in the known Claude model list")
        bad = SAMPLING & set(st)
        if bad:
            errors.append(f"{key}: {sorted(bad)} are rejected by current Claude models (400)")
        if st.get("effort") and st["effort"] not in ANTHROPIC_EFFORT:
            errors.append(f"{key}: effort {st['effort']!r} not in {sorted(ANTHROPIC_EFFORT)}")
        if st.get("max_tokens", 0) > 128000:
            errors.append(f"{key}: max_tokens above 128000")
        if st.get("max_tokens", 0) < 2000:
            warnings.append(f"{key}: max_tokens {st.get('max_tokens')} includes thinking tokens (thinking cannot be "
                            "disabled on this model family); expect truncations at effort medium or above")
        if require_keys and not os.environ.get("ANTHROPIC_API_KEY"):
            errors.append(f"{key}: ANTHROPIC_API_KEY not set")
    if prov == "openai":
        if not str(cfg.get("verified", "")).lower().startswith("yes"):
            warnings.append(f"{key}: model ID and parameters UNVERIFIED; run --smoke first")
        if st.get("reasoning_effort") and st["reasoning_effort"] not in OPENAI_EFFORT:
            warnings.append(f"{key}: reasoning_effort {st['reasoning_effort']!r} not in the expected set (unverified)")
        if st.get("max_tokens", 0) < 2000 and st.get("reasoning_effort"):
            warnings.append(f"{key}: max_output_tokens {st.get('max_tokens')} includes reasoning tokens; "
                            "expect incomplete responses at medium effort")
        if require_keys and not os.environ.get("OPENAI_API_KEY"):
            errors.append(f"{key}: OPENAI_API_KEY not set")
    if prov == "adaption":
        if not str(cfg.get("verified", "")).lower().startswith("yes"):
            warnings.append(f"{key}: written from SDK source, no live call yet; run --smoke first")
        if (prices or {}).get("currency") != "credits":
            errors.append(f"{key}: prices.currency must be 'credits' for Adaption models")
        if st.get("max_tokens", 0) > cfg.get("context_tokens", 10**9):
            errors.append(f"{key}: max_tokens above the context length")
        if require_keys and not os.environ.get("ADAPTION_API_KEY"):
            errors.append(f"{key}: ADAPTION_API_KEY not set")
    return errors, warnings


def currency(cfg: dict) -> str:
    return (cfg.get("prices") or {}).get("currency", "usd")


def check_all(models: dict, keys: list[str], require_keys: bool = True) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for k in keys:
        if k not in models:
            errors.append(f"{k}: not in the model config")
            continue
        e, w = check_model(k, models[k], require_keys)
        errors += e
        warnings += w
    cur = {currency(models[k]) for k in keys if k in models}
    if len(cur) > 1:
        errors.append(f"models priced in different currencies {sorted(cur)}: run them separately "
                      "(one budget and ledger per currency)")
    return errors, warnings
