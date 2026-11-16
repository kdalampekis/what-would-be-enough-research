"""Model runner: executes jobs, preserves every raw response, resumes safely.

A job is one prompt for one model. Its id is a hash of (model key, pool, instance,
mode, candidate, prompt text), so a changed prompt is a new job and old raw
files are never overwritten.

Raw records: results/raw/<pool>/<model_key>/<job_id>.json, each holding the
request (no credentials), the full raw provider response, status, usage,
timing and the parsed output. Failed attempts are kept as <job_id>.attempt<k>.json.
"""

from __future__ import annotations

import hashlib
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .prompts import PROMPT_VERSION
from .providers.base import Provider
from .schemas import (CAPABILITY_SCHEMA, DECISION_SCHEMA, JUDGMENT_SCHEMA, PLAN_SCHEMA, ParseError, parse_capability,
                      parse_decision, parse_judgment, parse_response)
from .spend import BudgetExceeded, Ledger, request_cost, token_usage

def _extraction_schema():
    from msep.controllers.llm_extractor import EXTRACTION_SCHEMA
    return EXTRACTION_SCHEMA


SCHEMAS = {"plan": (PLAN_SCHEMA, "msep_plan"), "judgment": (JUDGMENT_SCHEMA, "msep_judgment"),
           "decision": (DECISION_SCHEMA, "msep_decision"), "capability": (CAPABILITY_SCHEMA, "msep_capability"),
           "extract": (None, "msep_state_extraction")}  # schema filled lazily (avoids an import cycle)


@dataclass
class Job:
    pool: str            # plan | judgment | decision
    instance_id: str
    family_id: str
    mode: str            # end_to_end | detection_controlled | diagnosis_controlled | judgment | base_decision
    prompt: str
    candidate: tuple[str, ...] = ()   # formal action names (judgment jobs)
    meta: dict | None = None

    def job_id(self, model_key: str) -> str:
        key = json.dumps([model_key, self.pool, self.instance_id, self.mode, list(self.candidate),
                          hashlib.sha256(self.prompt.encode()).hexdigest()])
        return hashlib.sha256(key.encode()).hexdigest()[:24]


def load_models(path: Path) -> dict:
    return {k: v for k, v in json.loads(Path(path).read_text()).items() if not k.startswith("_")}


def make_provider(cfg: dict) -> Provider:
    if cfg["provider"] == "anthropic":
        from .providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(cfg["model_id"], cfg["settings"])
    if cfg["provider"] == "openai":
        from .providers.openai_provider import OpenAIProvider
        return OpenAIProvider(cfg["model_id"], cfg["settings"])
    if cfg["provider"] == "adaption":
        from .providers.adaption_provider import AdaptionProvider
        return AdaptionProvider(cfg["model_id"], cfg["settings"])
    if cfg["provider"] == "mock":
        from .providers.mock import MockProvider
        return MockProvider(cfg["model_id"], cfg["settings"])
    if cfg["provider"] == "fake":
        from .providers.fake import FakeProvider
        return FakeProvider(cfg["model_id"], cfg["settings"])
    raise ValueError(cfg["provider"])


def schema_kind(pool: str) -> str:
    """Pools are named <kind> or <kind>_<variant set>, e.g. plan, plan_cost, judgment."""
    return pool.split("_")[0]


def _parse(pool: str, text: str | None):
    pool = schema_kind(pool)
    if text is None:
        return None, "no text"
    if pool == "extract":  # mitigation C: an LLM's state extraction, validated by building the formal state
        import re
        from msep.controllers.llm_extractor import state_from_extraction
        try:
            m = re.search(r"\{.*\}", text, re.S)
            if not m:
                return None, "no JSON object found"
            d = json.loads(m.group(0))
            state_from_extraction(d)
            return d, None
        except Exception as e:  # any malformed extraction is an extraction failure, recorded as such
            return None, f"extraction invalid: {type(e).__name__}: {str(e)[:200]}"
    try:
        if pool == "plan":
            return asdict(parse_response(text)), None
        if pool == "judgment":
            return parse_judgment(text), None
        if pool == "capability":
            return parse_capability(text), None
        return parse_decision(text), None
    except ParseError as e:
        return None, str(e)


def raw_path(root: Path, job: Job, model_key: str) -> Path:
    return root / job.pool / model_key / f"{job.job_id(model_key)}.json"


def worst_case_cost(prompt: str, cfg: dict) -> float:
    """Upper estimate for one call: input ~ chars / 3 tokens (errs high), output = the configured cap."""
    p = cfg["prices"]
    return (len(prompt) / 3) / 1e6 * p["input_per_mtok"] + cfg["settings"]["max_tokens"] / 1e6 * p["output_per_mtok"]


def run_jobs(jobs: list[Job], model_key: str, cfg: dict, root: Path, *, max_calls: int,
             concurrency: int = 4, provider: Provider | None = None, log=print, ledger: Ledger | None = None) -> dict:
    """Run jobs not yet completed. Never exceeds max_calls provider calls.

    With a ledger, every call first reserves its worst-case cost; once the budget
    would be exceeded, no further calls are started for any model."""
    mismatched = [j for j in jobs if _settings_mismatch(raw_path(root, j, model_key), cfg)]
    if mismatched:
        raise RuntimeError(
            f"{len(mismatched)} saved results for {model_key} were made with different settings "
            f"(e.g. {_settings_mismatch(raw_path(root, mismatched[0], model_key), cfg)}); results are cached by "
            "model key, so give the new settings their own model key in configs/models.json instead of --override")
    todo = [j for j in jobs if not _done(raw_path(root, j, model_key))]
    # strict retry cap: a job that has already failed MAX_ERROR_ATTEMPTS times is not retried
    exhausted = [j for j in todo if _attempts(raw_path(root, j, model_key)) >= MAX_ERROR_ATTEMPTS]
    todo = [j for j in todo if j not in exhausted]
    if len(todo) > max_calls:
        raise RuntimeError(f"{len(todo)} calls needed for {model_key}, above --max-calls {max_calls}")
    if ledger is not None and not cfg.get("prices"):
        raise RuntimeError(f"{model_key} has no prices configured; cannot enforce the budget")
    provider = provider or make_provider(cfg)
    counts = {"skipped_done": len(jobs) - len(todo), "ok": 0, "refusal": 0, "truncated": 0, "error": 0,
              "parse_error": 0, "budget_stopped": 0}
    stop = threading.Event()
    counts["retry_cap_reached"] = len(exhausted)
    log_lock = threading.Lock()
    run_log = Path(root) / "run_log.jsonl"
    run_log.parent.mkdir(parents=True, exist_ok=True)

    def log_event(event: dict) -> None:
        with log_lock, open(run_log, "a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "model_key": model_key, **event}) + "\n")

    log_event({"event": "batch_start", "jobs": len(jobs), "to_run": len(todo), "retry_cap_reached": len(exhausted)})

    def one(job: Job):
        if stop.is_set():
            return "budget_stopped", None
        worst = 0.0
        if ledger is not None:
            worst = worst_case_cost(job.prompt, cfg)
            try:
                ledger.reserve(worst)
            except BudgetExceeded as e:
                stop.set()
                log(f"  STOP: {e}")
                return "budget_stopped", None
        path = raw_path(root, job, model_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        schema, name = SCHEMAS[schema_kind(job.pool)]
        if schema is None:
            schema = _extraction_schema()
        for rl_try in range(RATE_LIMIT_RETRIES + 1):
            t0 = time.time()  # latency of the attempt that is recorded, not of rate-limit waits
            res = provider.complete(job.prompt, schema, name)
            if not (res.status == "error" and _rate_limited(res.error)) or rl_try == RATE_LIMIT_RETRIES:
                break
            wait = RATE_LIMIT_WAIT_S + random.uniform(0, 15)
            log_event({"event": "rate_limited", "job_id": job.job_id(model_key), "try": rl_try + 1, "wait_s": round(wait)})
            time.sleep(wait)  # the server asks to retry after 60 s; not counted as a failed attempt
        tokens = token_usage(cfg["provider"], res.usage)
        cost = request_cost(cfg["prices"], tokens) if cfg.get("prices") else None
        if ledger is not None:
            ledger.settle(worst, {"model_key": model_key, "job_id": job.job_id(model_key), "pool": job.pool,
                                  "status": res.status, **tokens, "cost_usd": cost or 0.0,
                                  "timestamp": datetime.now(timezone.utc).isoformat()})
        parsed, perr = _parse(job.pool, res.text) if res.status in ("ok", "truncated") else (None, None)
        rec = {
            "job_id": job.job_id(model_key), "model_key": model_key, "model_id": cfg["model_id"],
            "provider": cfg["provider"], "served_model": res.served_model, "prompt_version": PROMPT_VERSION,
            "pool": job.pool, "instance_id": job.instance_id, "family_id": job.family_id, "mode": job.mode,
            "candidate": list(job.candidate), "meta": job.meta or {},
            "prompt_sha256": hashlib.sha256(job.prompt.encode()).hexdigest(),
            "settings": {k: v for k, v in (cfg.get("settings") or {}).items() if k != "lookup"},
            "request": res.request, "status": res.status, "error": res.error, "usage": res.usage,
            "tokens": tokens, "cost_usd": cost, "prices": cfg.get("prices"),
            "raw_response": res.raw, "text": res.text, "parsed": parsed, "parse_error": perr,
            "seconds": round(time.time() - t0, 2), "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        target = path
        if res.status == "error":  # keep the failed attempt, leave the job open for a retry
            k = 1
            while path.with_suffix(f".attempt{k}.json").exists():
                k += 1
            target = path.with_suffix(f".attempt{k}.json")
        target.write_text(json.dumps(rec, indent=1))
        log_event({"event": "job", "job_id": rec["job_id"], "pool": job.pool, "mode": job.mode,
                   "instance_id": job.instance_id, "status": res.status, "parse_error": perr,
                   "tokens": tokens, "cost_usd": cost, "seconds": rec["seconds"]})
        return res.status, perr

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(one, j) for j in todo]
        for i, f in enumerate(as_completed(futs), 1):
            status, perr = f.result()
            counts[status] += 1
            if status == "budget_stopped":
                continue
            if perr:
                counts["parse_error"] += 1
            if i % 50 == 0:
                log(f"  {model_key}: {i}/{len(todo)}")
    log_event({"event": "batch_end", **counts})
    return counts


MAX_ERROR_ATTEMPTS = 3
RATE_LIMIT_RETRIES = 10   # 429 "rate limit reached; retry after 60 seconds": wait and retry the same job
RATE_LIMIT_WAIT_S = 60


def _rate_limited(error: str | None) -> bool:
    e = str(error or "")
    return e.startswith("429") or "rate_limit" in e or "rate limit" in e.lower()


def _attempts(path: Path) -> int:
    return len(list(path.parent.glob(path.stem + ".attempt*.json"))) if path.parent.exists() else 0


_OUTPUT_CAP_FIELDS = ("max_output_tokens", "max_tokens")


def _settings_mismatch(path: Path, cfg: dict) -> str | None:
    """Describe how a saved, completed result's settings differ from the current config, or None."""
    if not path.exists():
        return None
    rec = json.loads(path.read_text())
    cur = cfg.get("settings") or {}
    if "settings" in rec and rec["settings"] is not None:
        keys = {"max_tokens", "temperature", "effort", "reasoning_effort", "stream", "structured"}
        diff = {k: (rec["settings"].get(k), cur.get(k)) for k in keys if rec["settings"].get(k) != cur.get(k)}
        return f"saved vs now {diff}" if diff else None
    req = rec.get("request") or {}  # records written before settings were saved
    saved_cap = next((req[f] for f in _OUTPUT_CAP_FIELDS if f in req), None)
    if saved_cap is not None and cur.get("max_tokens") is not None and saved_cap != cur["max_tokens"]:
        return f"output cap saved {saved_cap} vs now {cur['max_tokens']}"
    return None


def latest_record(root: Path, job: Job, model_key: str) -> dict | None:
    """The saved result for a job: the final file if present, else the most recent failed attempt."""
    path = raw_path(root, job, model_key)
    if path.exists():
        return json.loads(path.read_text())
    attempts = sorted(path.parent.glob(path.stem + ".attempt*.json"),
                      key=lambda p: int(p.suffixes[-2].removeprefix(".attempt"))) if path.parent.exists() else []
    return json.loads(attempts[-1].read_text()) if attempts else None


def _done(path: Path) -> bool:
    if not path.exists():
        return False
    return json.loads(path.read_text()).get("status") != "error"


def load_results(root: Path, pool: str, model_key: str) -> list[dict]:
    d = root / pool / model_key
    if not d.exists():
        return []
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json")) if ".attempt" not in p.name]


def estimate(jobs: list[Job], prices: dict, out_tokens: int) -> dict:
    """Rough budget: input tokens ~ chars / 4; output (incl. reasoning) assumed `out_tokens` per call."""
    chars = sum(len(j.prompt) for j in jobs)
    in_tok = chars / 4
    out_tok = out_tokens * len(jobs)
    cost = None
    if prices:
        cost = in_tok / 1e6 * prices["input_per_mtok"] + out_tok / 1e6 * prices["output_per_mtok"]
    cur = (prices or {}).get("currency", "usd")
    return {"calls": len(jobs), "input_tokens_est": int(in_tok), "output_tokens_assumed": out_tok,
            f"{cur}_est": None if cost is None else round(cost, 2)}
