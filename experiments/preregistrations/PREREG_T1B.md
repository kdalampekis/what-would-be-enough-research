# PREREG_T1B.md — Over-intervention after an intervention makes the state sufficient (prospective follow-up)

**Registered:** 2026-11-14 (UTC), before any T1 model response on the families below exists, and before
any v3 dev result on these families has been inspected (the v3 dev controlled evaluation was running at
registration; no output of it was read for families 31–72, except that a smoke test of the analysis script
touched the single native ALREADY_SUFFICIENT response that existed at that moment for one of the 42
families — its value was not used to change anything here).
**Status:** a prospectively registered follow-up **motivated by an exploratory finding** of the T1 dev
pilot (`results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md`: qwen3.5-397b over-intervened on 10/55
pairs that became ALREADY_SUFFICIENT; gemma +schema on 30/55). The T1 pilot's own pre-registration
(`PREREG_T1.md`) and its inconclusive result are unchanged. The 20 pilot families are **not** used here.
Links to the original hypotheses: H1 (detection), H5 (minimality and stopping are distinct).

## Hypothesis

**H-OI.** When a single intervention makes a previously insufficient state already sufficient, models
continue to propose information or computation actions that are no longer needed.

## Items (frozen T1 data, `data/FREEZE_T1.json`; no new generation)

- Dev families ranked 31–72 by sorted id (42 families; ranks 1–10 were the v3 calibration families, ranks
  11–30 the T1 pilot): 272 T1 pairs (544 items).
- **Primary population:** the 122 pairs whose B member is ALREADY_SUFFICIENT (A was INFORMATION_ONLY 49,
  COMPUTATION_ONLY 48, NEITHER 17, BOTH 8; edits E_OBS 63, E_CERT 59), in 42 families.
- **Native-sufficiency contrast:** the 42 v3 ALREADY_SUFFICIENT siblings of the same families, from the
  v3 dev controlled evaluation (End-to-End), same models and settings.
- All 272 pairs are run, so pair and transition metrics (as in PREREG_T1.md) are also reported.

## Models, mode, settings

`adaption-qwen3.5-397b`, `adaption-qwen3.8-27b`, `adaption-gemma-4-26b-a4b-it-schema` (forced-schema
condition), `adaption-deepseek-v4-flash`; settings as in `configs/models.json` at registration (temperature
0.0, max_tokens 16000, streaming, max_retries 2; served models recorded). End-to-End only: the
Detection- and Diagnosis-Controlled prompts are ineligible for ALREADY_SUFFICIENT states by definition.
Prompt `msep-prompts-v2-certified-compute`. Failed calls (transport/5xx) are retried at most twice more
with identical settings.

## Outcomes (on the into-ALREADY_SUFFICIENT B members unless stated; all attempted, unparsed = failure)

- **O1 over-intervention** (primary): the plan is non-empty.
- O2 answer-now correct: `state_sufficient` true, plan empty, and the decision equals the true value.
- O3 recognised-but-acted: `state_sufficient` true and plan non-empty.
- O4 unnecessary computation: plan contains a COMPUTE action; O5 unnecessary information: plan contains an
  ASK action; O6 redundant action count: mean plan length.
- O7 optimal after the intervention (= empty plan; same as not O1 for parsed answers).
- O8 A→B transition correct (as in PREREG_T1.md), on these pairs.
- Contrast **C-native**: O1 on the 42 native ALREADY_SUFFICIENT items.

## Confirmatory tests (per model; Holm correction across the 4 models within each test)

- **T-OI-1 (prevalence):** O1 > 0.05. Supported if the one-sided 95% family-clustered bootstrap lower bound
  of O1 exceeds 0.05 (Holm on the bootstrap one-sided p = share of resamples with O1 ≤ 0.05).
- **T-OI-2 (specific to intervention-induced sufficiency):** O1 on into-AS B items > O1 on native AS items
  of the same families. Difference with family-clustered bootstrap (resampling families, both item sets
  together); one-sided p = share of resamples with difference ≤ 0; Holm across models.
- Bootstrap: 10,000 resamples, seed 0.

Everything else (O2–O8, by edit kind, by A class) is descriptive. Non-significant results are not
evidence of absence.

## Budget and stopping

Covered by the authorised evaluation ceiling (ledger cap 519.4324 credits at registration). Run once; no
change to items, prompts, settings or analysis after seeing results. Analysis: `experiments/analyze_t1b.py`
(written and frozen with this document before any response exists).
