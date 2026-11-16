# PREREG_T1.md — T1 single-edit counterfactual flips: pre-registration (dev pilot)

**Registered:** 2026-11-13, before any model has seen a T1 item. Frozen together with the data, generator,
oracle and analysis code in `data/FREEZE_T1.json` (`experiments/freeze_t1.py --verify`).
**Scope:** dev split only. The held-out test split is not used. v3 is unchanged and remains the primary
benchmark.

**Disclosure.** T1 belongs to Challenge Tier v4. It was designed after the v3 calibration showed three
models at ceiling and after the literature review (`LITERATURE_FAILURE_MAP.md`); its closest prior work is
Ask, Relax, or Act? (matched pairs, IFC). It is not designed around any tested model's failures, and no
item was selected using model outputs.

## 1. Items

- Source: frozen v3 pool (`pool_v3`, sha256 `660012bd…`). Generator `src/msep/benchmark/t1_flips.py`
  (`t1-v1`), script `experiments/generate_t1.py`.
- Pair (A, B): A is a v3 record, re-rendered (byte-identical to its v3 prompt). B fixes exactly one more
  non-target variable at its true value: E_OBS (a world variable observed) or E_CERT (a computed
  variable's certified result). Rules, world, action menu, costs and rendering are identical; the prompts
  differ in exactly one line ("Known so far"), by 3–13 characters.
- Both members labelled from scratch by the exact oracle; a pair is kept only if the optimal-plan set or
  the class changes. One edit per base record, drawn with a seed from the base id, uniformly over the
  non-empty (edit kind, transition type) groups.
- Validation (all must pass; 0 failures at registration): A prompt equals v3; one-line diff; identical
  menus; SAT oracle = brute-force oracle on every member (3,938 items).
- Full set: 1,969 pairs, 300 families (train 1,098 / dev 469 / test 402).
- Transition types: **direct** (optimal B plans = optimal A plans minus the actions that reveal the edited
  variable) and **indirect** (anything else).

## 2. Shortcut and control checks (done before registration, heuristics only)

On the pilot families, text-only heuristics reach 0.81–0.84 transition accuracy on direct pairs and
0.00–0.28 on indirect pairs. Direct pairs are therefore largely solvable by "drop what became known".
**The indirect stratum is the primary test; direct pairs are a shortcut control.** The heuristics also
show positive excess over the family permutation (+0.10 to +0.19), because A and B share a base state.
Excess is therefore read against the h1++ value, not against 0.
Controls reported per stratum: prompt length and length change, action count (identical within pairs),
class transitions, number of minimal plans, optimal cost.

## 3. Pilot sample, models and settings

- Families: dev families ranked 11–30 by sorted id (the first 10 are the calibration families):
  G32e3bf02b7, G32efc4979e, G3303dbbaab, G3354ecb6e8, G38d540cc73, G3d8bb206ae, G3de7198540, G4332c7e7eb,
  G452b5f9d2c, G4795b65645, G486768e0c2, G49ae433e4c, G4a6f2ad510, G4d5fc55c67, G4ea12023e5, G5078de6b92,
  G5173e1a3d6, G5420f54cc4, G563c07d0ba, G6508d36578. → 133 pairs (85 direct, 48 indirect), 266 items.
- Mode: End-to-End only (flips change what is known, including into ALREADY_SUFFICIENT).
- Models and fixed settings (`configs/models.json`, Adaption SDK 0.19.0, streaming, max_retries 2,
  temperature 0.0, max_tokens 16000):
  `adaption-qwen3.5-397b`, `adaption-qwen3.8-27b`, `adaption-gemma-4-26b-a4b-it-schema` (forced
  JSON-schema function tool; a separately documented condition, not comparable to plain gemma).
- Prompt: `msep-prompts-v2-certified-compute` (unchanged).
- Budget: 12 credits on top of the ledger total at registration (10.6908): `--budget 22.6908`. The runner
  reserves the worst case before each call and stops before any call that could cross the cap. A budget
  stop is reported, not extended.
- Run order: smoke gate, then qwen3.8-27b, gemma +schema, qwen3.5-397b.

## 4. Outcomes (analysis: `experiments/analyze_t1.py`)

All-attempted basis is primary (an unparsed or truncated answer is incorrect); parsed-only is a
sensitivity analysis; parse and truncation counts are reported separately.

- Item correct: NEITHER → decision "defer"; otherwise the plan is optimal (on ALREADY_SUFFICIENT, the
  empty plan).
- **P1 Joint accuracy**: both members correct.
- **P2 Transition accuracy**: on pairs without a NEITHER member, the model's plan change equals the change
  between some optimal A plan and some optimal B plan (both answers must parse).
- **P3 Excess inconsistency** (primary baseline): joint − joint under a family-matched permutation
  (re-pair each A with B members of other pairs in the same family and transition stratum). Secondary:
  joint − Σ p(A stratum)·p(B stratum), strata = (class, transition, edit).
- Also: item accuracy A and B; P(B correct | A correct) vs P(B correct | A wrong).
- Strata: direct / indirect (primary), edit kind, into ALREADY_SUFFICIENT, from NEITHER, drop rule
  succeeds / fails.
- Uncertainty: 95% family-clustered bootstrap (2,000 resamples, seed 0). No significance tests; this is a
  dev pilot.

## 5. Decision rules (fixed now)

- **Ceiling on T1** for a model: indirect-stratum joint accuracy has a lower 95% bound ≥ 0.90.
- **Additional capability gap** for a model: indirect-stratum joint accuracy has an upper 95% bound
  < 0.90, *and* the model's v3 calibration optimal rate was ≥ 0.95 (qwen3.5-397b, qwen3.8-27b).
- **Edit-tracking failure beyond difficulty**: indirect-stratum excess vs family permutation has an upper
  95% bound below h1++'s point estimate on the same pairs.
- With 48 indirect pairs in 19 families, intervals will be wide; outcomes inside neither rule are reported
  as inconclusive. A ceiling result is a valid result and will be reported as such.

## 6. Stopping

The pilot is run once with these settings. The generator, items, prompts and analysis are not changed after
seeing results. Any bug fix is logged with its effect, and the frozen record is renewed.
