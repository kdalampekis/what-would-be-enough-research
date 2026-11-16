# HELDOUT_PLAN.md — draft plan for the single held-out (test-split) evaluation

**Status: superseded on 2026-11-14 by `PREREG_FINAL.md` (kept as the draft that was approved at the gate).** No test-split item has
been sent to any model. After approval this becomes `PREREG_FINAL.md`, is frozen with
`experiments/freeze_protocol.py`, and the test run happens once, without tuning on its outcomes.

## Scope (test split only; 63 v3 families)

1. **v3 controlled evaluation**, E1–E9, End-to-End / Detection-Controlled / Diagnosis-Controlled, original
   eligibility (`run_pilot.py --splits test --allow-test --allow-full-split`).
2. **T1 counterfactual flips**, test pairs (402 pairs), End-to-End, with the PREREG_T1 outcomes and the
   T1B outcomes on into-ALREADY_SUFFICIENT pairs.
3. **EOP comparison** A/B/C/D on v3 test (End-to-End, Detection-Controlled) and T1 test, exactly as in
   PREREG_EOP.md (no change to prompts, extraction schema, planner or scoring).

## Models and settings

The four dev models, unchanged: `adaption-qwen3.5-397b`, `adaption-qwen3.8-27b`,
`adaption-gemma-4-26b-a4b-it-schema`, `adaption-deepseek-v4-flash` (configs/models.json; served models
recorded; any provider-side change is reported, not hidden).

## Confirmatory hypotheses (to be fixed at the gate; candidates)

- PROTOCOL.md §4 confirmatory tests (H2 diagnosis vs plan sufficiency, H3 relevance vs sufficiency, H4
  INFO/COMP vs BOTH), Holm within model as registered there.
- H-OI (T-OI-1, T-OI-2) on the test into-ALREADY_SUFFICIENT pairs, Holm across models — only if the dev
  T1B result motivates confirming it; otherwise reported descriptively.
- H6: C−A on optimality, Detection-Controlled, Holm across models (as PREREG_EOP).
- Everything else descriptive. Inconclusive and null results are reported as such.

## Size and time (estimate, mine)

Per model ≈ 1,840 v3 jobs + 804 T1 items + ≈ 2,600 EOP calls ≈ 5,250 calls; four models ≈ 21,000 calls.
At the observed shared provider rate (~31 calls/min) ≈ 11 hours. Cost at dev rates ≈ 60–90 credits.

## Open decisions for the gate

- Whether the dev results change which confirmatory tests are registered (allowed before the test run).
- Whether all four models run on test or a subset (time).
- Any objective bug fix found at the dev gate (logged in BENCHMARK_CHANGELOG.md / protocol notes).
