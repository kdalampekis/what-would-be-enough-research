# PREREG_EOP.md — Epistemic Obligation Planner: registered dev comparison (H6, S1–S3)

**Registered:** 2026-11-14 (UTC), before any condition-B, C or D response exists. Frozen with the
driver and planner code in `data/FREEZE_EOP.json` (`experiments/freeze_protocol.py --name EOP --verify`).
**Scope:** dev split only (the held-out test split is reserved for the final frozen evaluation).
**Hypothesis (H6, from EXPERIMENT_PLAN.md):** an obligation-guided planner reduces insufficient actions,
premature stopping and excess resource cost relative to native planning and a structured prompt.

## Conditions (same items, same model, same settings within a model)

- **A — native:** the model's own answer to the benchmark prompt (`msep-prompts-v2-certified-compute`).
  Taken from the T1 pilot, T1B and v3 dev runs (identical configurations; no new calls).
- **B — structured obligation prompt (S1):** the same prompt plus step-by-step obligation-reasoning
  instructions (`src/msep/models/prompts_s1.py`, `msep-s1-obligations-v1`); same output JSON.
- **C — realistic EOP (S3):** the model extracts the agent-visible formal state as JSON from the prompt text
  (`controllers/llm_extractor.py`, `msep-extraction-v1`); the realistic planner
  (`controllers/realistic_planner.py`) checks whether Q is already decided, enumerates unresolved
  obligations and finds a minimum-cost plan that discharges all of them (weighted hitting set). One
  extraction per state; the plan does not depend on the mode.
- **D — verifier ablation (S2):** B's plan, verified on C's extracted state without search: if the
  extracted state already decides Q, the plan is emptied and Q is answered; otherwise every action of B's
  plan that discharges no unresolved obligation (or is not in the extracted menu) is removed; nothing is
  added. Separates verification/pruning from full plan optimisation.
- **Upper bounds (not mitigations):** U = the same planner on the exact rule-based parse of the text;
  the oracle (1.0 by definition).
- Strict scoring: if a call fails, an extraction is invalid or inconsistent, or B's answer does not parse,
  C/D count as failures (no fallback to another condition). Failure rates are reported.
- No condition sees hidden-world truth, oracle labels, true values or certified results before COMPUTE:
  planning uses only the prompt text via the extraction (tests: `tests/test_eop_driver.py`).

## Item sets (End-to-End unless stated)

1. **v3 dev, all 72 families** — End-to-End and Detection-Controlled (B is run in both; A from the v3 dev
   run; C/D plans are mode-independent and scored on each mode's eligible items). Primary set.
2. **T1 pilot items** (families 11–30, 266 items).
3. **T1B items** (families 31–72, 544 items) — includes the into-ALREADY_SUFFICIENT cases (the
   over-intervention regime). The primary sample is **not** conditioned on native failures.

## Models

`adaption-qwen3.5-397b`, `adaption-qwen3.8-27b`, `adaption-gemma-4-26b-a4b-it-schema` (forced-schema
condition), `adaption-deepseek-v4-flash`. Settings as frozen; served model recorded per response.

## Outcomes

Primary (resolvable states; all attempted, unparsed/failed = incorrect): plan optimality; plan
sufficiency; regret (parsed); unnecessary-action rate (sufficient plans that are not minimal).
Secondary: resource-class accuracy; correct stopping (empty plan and answer on ALREADY_SUFFICIENT; defer on
NEITHER); extraction validity; format/truncation failures; tokens, latency and cost per item including all
calls of a condition (D = B call + extraction call) and planner runtime. Parsed-only reported separately.

## Comparisons

Paired by item, 95% family-clustered bootstrap intervals: C−A, C−B, B−A, D−A, C−D (and D−B), on optimality
and sufficiency, per model and item set and mode. **Confirmatory (dev):** C−A on optimality, v3 dev
Detection-Controlled, per model; one-sided bootstrap p (share of resamples ≤ 0), Holm across the 4 models.
Everything else is descriptive. A null result is reported as such.

## Discipline

No change to prompts, extraction schema, planner or scoring after seeing B/C/D results on these sets. If
the planner fails, an error analysis (extraction, obligation representation, verification, planning) is
reported instead of tuning.

---

## Amendment 1 (2026-11-14, before any C/D outcome was scored)

**What happened.** During the run, a pipeline check (extraction validity and planner errors only, no
outcome metrics) showed that most extractions from providers without schema enforcement were invalid:
deepseek-v4-flash 525/538, qwen3.5-397b 171/545 (v3 dev), against gemma +schema 3/545. Inspection: the
models extracted the correct content (variables and kinds, rules, known values) in other JSON layouts,
e.g. `"variables": {"F1": "world"}` or `{"name": ...}` instead of `{"handle": ...}`. The v1 extraction
prompt describes its fields in prose and never shows the exact layout the parser requires, whereas the
plan prompt used by conditions A and B has always contained the full JSON template. Under strict scoring,
condition C therefore mostly measured whether a model guesses our layout. Decided by the PI on 2026-11-14.

**Change.** A new condition **C′** (and **D′** = B verified on C′'s extraction) uses extraction prompt v2
(`msep-extraction-v2`, `controllers/llm_extractor.py`: the v1 text plus the exact JSON template). Nothing
else changes: same planner, verifier, scoring, items, modes, models and settings. Run for the models
without schema enforcement (qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash); gemma +schema's extractions
already receive the layout through the forced function-tool schema, so its C is unaffected (not re-run).

**Reporting.** The registered conditions C and D are reported exactly as registered (with their
extraction failures). C′/D′ are reported separately and labelled as Amendment 1. Paired comparisons
include C′−A, C′−B, C′−C, D′−A, C′−D′. The confirmatory test stays C−A (registered); C′−A on the same
basis is reported as an amended secondary analysis, not as the registered confirmatory result.
Frozen: `data/FREEZE_EOP_A1.json`. The original `data/FREEZE_EOP.json` no longer verifies because
`llm_extractor.py`, `run_eop.py` and this file changed (additions only; the v1 prompt is byte-identical,
tested in `tests/test_eop_driver.py`).

## Amendment 2 (2026-11-14, analysis only, no new calls)

**What happened.** Under the structured prompt (condition B), gemma +schema wrote its reasoning and then
the JSON answer as message text and made no function call in all 1,018 v3 dev responses, although the
call was forced (`tool_choice`); under the native prompt (A) it made the call in 1,417 of 1,418. The
forced-schema connector by design never takes an answer from prose, so registered B (and D, which needs
B's plan) score 100% "no text" for gemma. The registration assumed a forced-schema model "can only reason
internally"; the provider did not enforce that.

**Change (analysis only).** A sensitivity condition **Bt** parses the JSON from the model's own message
text with the standard plan parser (the parser used for every non-forced model) only where no function
call was made; **Dt** = Bt verified on C's extraction. Registered B and D are reported unchanged. Bt/Dt
are labelled as Amendment 2 and are used only where registered B is uninformative (gemma +schema).
