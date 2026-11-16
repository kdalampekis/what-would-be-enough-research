# PREREG_FINAL.md — the single held-out (test-split) evaluation

**Registered:** 2026-11-14 (UTC), before any test-split item was sent to any model. Frozen with the drivers,
analysis code, prompts, planner, data and model settings in `data/FREEZE_FINAL.json`
(`experiments/freeze_protocol.py --name FINAL --verify`). Decided by the PI at dev decision gate 2
(`results/aggregate/GATE2_DEV_REPORT.md`). Replaces the draft `HELDOUT_PLAN.md`.

The earlier registrations are unchanged and stay in force for what they registered: `PROTOCOL.md`,
`PREREG_T1.md`, `PREREG_T1B.md`, `PREREG_EOP.md` (with Amendments 1 and 2).

## 1. What this run is, and what it is not

- It is the one run on the test split: 63 v3 families (468 states) and their 402 T1 pairs (804 items).
- For the EOP mitigation it is a **prospective test of the amended method**. The mitigation as originally
  registered (condition C, extraction prompt v1) was supported on dev for gemma +schema only; for the other
  three models it failed because the v1 prompt never showed the JSON layout (PREREG_EOP Amendment 1). That
  registered dev result stands and is reported as such. The amended condition C′ was chosen after seeing
  dev data. Test results for C′ are evidence for the amended method; they do not turn the original
  registered experiment into a success.
- No prompt, extractor, planner, scoring rule or model setting changes after the first test response.

## 2. Models and settings (unchanged from dev)

`adaption-qwen3.5-397b`, `adaption-qwen3.8-27b`, `adaption-gemma-4-26b-a4b-it-schema` (forced function-tool
schema), `adaption-deepseek-v4-flash`; temperature 0.0, max_tokens 16000, streaming (`configs/models.json`,
hashed in the freeze). The served model is recorded per response; a provider-side change is reported.

## 3. Conditions (identical items within a model)

- **A — native.** v3 test, experiments E1–E9 in End-to-End, Detection-Controlled and Diagnosis-Controlled
  modes with the original eligibility rules (`run_pilot.py`); T1 test pairs End-to-End.
- **B — structured obligation prompt (S1,** `msep-s1-obligations-v1`**).** v3 test End-to-End and
  Detection-Controlled; T1 test End-to-End.
- **EOP — realistic Epistemic Obligation Planner, frozen configuration per model.** One extraction call
  per state, then the realistic planner (unchanged).
  - qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash: extraction prompt v2 (`msep-extraction-v2`) = condition
    **C′** of Amendment 1.
  - gemma +schema: the registered extraction prompt v1 under its forced schema = registered condition
    **C**. Reason: this is the configuration validated on dev (the schema supplies the layout); the v2
    prompt was never run with this model.
  - Registered C (v1 prompt) is **not** run on test for the three models without schema enforcement: it is
    a known instrument defect, and its dev results are the registered outcome.
- **D′ / D — verifier ablation** (B's plan pruned on the EOP extraction, no search): computed, no calls.
- **Bt / Dt** (Amendment 2, analysis only): where a forced-schema answer made no function call, the JSON
  in the message text is parsed. Used for gemma +schema, reported next to registered B / D.
- **P — deterministic parser + planner (baseline, no model).** The rule-based parser
  (`benchmark/parsing.py: parse_state`) followed by the same planner. Audit (2026-11-14): the parser's
  only input is the prompt text; it uses a fixed grammar and no generator metadata, oracle label or hidden
  value. It is therefore reported as a baseline, not only as an upper bound. It was written by the
  benchmark authors as the inverse of the benchmark's own renderer, so its score on canonical text says
  nothing about other wordings (see PREREG_ROBUST.md).
- **Oracle** (exact, 1.0 by definition) and the non-LLM policies and heuristics as in dev.

No condition sees hidden-world truth, oracle labels or unexecuted computation results.

## 4. Outcomes and scoring

As in PROTOCOL.md §7 and PREREG_EOP.md: plan optimality, plan sufficiency, regret (parsed),
unnecessary-action rate, resource-class accuracy, correct stopping (empty plan and correct answer on
ALREADY_SUFFICIENT; defer on NEITHER), E1–E9 metrics, T1 pair outcomes, T1B outcomes O1–O8, extraction
validity, tokens, latency and cost per condition. Extraction correctness: the extracted state against the
exact parse of the same text (`eval/extraction_match.py`: same variables and kinds, known values, actions
with costs and reveals, logically equivalent rule set).

**Primary basis: all attempted.** A failed call, truncated or unparsed answer, invalid extraction or
planner error counts as incorrect. Parsed-only figures are reported separately. Failure counts by type
are reported for every condition.

Intervals: 95% family-clustered bootstrap. Paired differences by item, resampling families.

## 5. Confirmatory tests (test split)

Three families. Holm correction within each family, α = 0.05; no correction across families (stated here
so it can be judged).

- **F0 — PROTOCOL.md §8, unchanged:** H2, H3, H4a, H4b; exact two-sided McNemar, Detection-Controlled,
  Holm across the four tests, per model.
- **F1 — EOP improves planning (amended H6):** EOP − A on plan optimality, v3 test, Detection-Controlled,
  resolvable states, all attempted, per model. One-sided family-clustered bootstrap p (share of 10,000
  resamples with difference ≤ 0, seed 0), Holm across the four models. Supported for a model if Holm
  p < 0.05.
- **F2 — over-intervention on newly sufficient states (H-OI, T-OI-1 of PREREG_T1B):** O1 > 0.05 on the test
  pairs whose edited state is ALREADY_SUFFICIENT, End-to-End, native; same bootstrap test as PREREG_T1B,
  Holm across the four models. T-OI-2 (edit-specific excess) was not supported on dev and is reported
  descriptively.

**Registered secondary (intervals, no test):** EOP − B and EOP − D′ on optimality and sufficiency (both
modes); B − A; correct stopping EOP − A (v3 End-to-End; T1 test items); T1 pair joint accuracy A / B / EOP;
P against EOP; extraction correctness; cost per item.

Everything else is descriptive, including H1 and H5 and the mode decomposition. Null and inconclusive
results are reported as such.

## 6. Execution

`experiments/chain_final.sh MODEL CONCURRENCY CAP` per model, in priority order (v3 native; EOP on v3; T1
native; EOP extraction on T1; structured prompt on T1), then one fill pass. Jobs are cached by job id: a
completed response is never requested again; a job that ends in a transport or provider error is retried
up to 3 attempts in total; rate-limit waits are not attempts. Then `experiments/final_finalize.sh` (no
calls). Size: 5,567 calls per model, 22,268 in total. Spend cap: cumulative ledger 519.4324 credits.

If time runs out before every step finishes, steps are dropped from the end of the priority order for all
models alike, and the report says which steps did not run. No step is dropped because of its results.

## 7. Related, separate study

Linguistic robustness (`PREREG_ROBUST.md`) is frozen separately and uses dev families. Its results are
never used to change the EOP configuration or to re-run anything on the test split.

## 8. Changes to frozen files made for this run (before any test response)

- `experiments/run_eop.py`: added the item sets `v3test` and `t1test` behind `--allow-test`; the one-sided
  p is now also computed for C′ − A; a `confirmatory_final_EOP_minus_A_optimal_DC` block for F1. No change
  to prompts, planning, verification or scoring. `data/FREEZE_EOP_A2.json` therefore no longer verifies.
- New: `experiments/analyze_final.py` (PREREG_T1B outcomes and bootstrap imported unchanged, test-split
  selection; extraction correctness), `src/msep/eval/extraction_match.py`, `experiments/chain_final.sh`,
  `experiments/final_finalize.sh`.
