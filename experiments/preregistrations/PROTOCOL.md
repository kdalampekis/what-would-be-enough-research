# Evaluation protocol

**Status: v0.2, ready for the calibration pilot (2026-11-04). Not frozen.**

> **Amendment (2026-11-14).** The models actually used are Adaption-hosted open-weight models (credits, not
> dollars): `adaption-qwen3.5-397b` (served `qwen3.5-397b-a17b-nvfp4`), `adaption-qwen3.8-27b`,
> `adaption-gemma-4-26b-a4b-it-schema` (forced JSON-schema function tool; a separate documented condition)
> and `adaption-deepseek-v4-flash`; settings in `configs/models.json` (temperature 0.0, max_tokens 16000,
> streaming). The GPT/Claude/Gemini plans in §3 were not run. Dev evaluation so far: 10-family calibration
> (2026-11-13), all-72-family dev run, T1 (`PREREG_T1.md`), T1B (`PREREG_T1B.md`) and the EOP comparison
> (`PREREG_EOP.md`). The protocol is frozen before the single held-out test run (§12).
- The benchmark content is frozen: `data/FREEZE_v3.json`, benchmark v3.0.
- This protocol is frozen after the dev calibration pilot, before any test-split run (§12).
- No model has been evaluated under it.

## 1. Data (frozen)

| Item | Value |
|---|---|
| Benchmark | v3.0: `pool_v3`, 300 families, 2,282 instances. Generator and oracle source hashes, dataset hashes, seed scheme and every family's split are in `data/FREEZE_v3.json` (code commit 2b496e7). `python experiments/freeze_benchmark.py --verify` must print FREEZE OK before every run |
| Variants | `variants_v3`: E10 cost sweeps, E11 risk, E12 wording shift |
| Shallow subset | `pool_v2`: solved 100% by a text-only heuristic. Used only as the in-distribution side of the v2 → v3 structural comparison (E12) |
| Changes | Only objective bug fixes, each in `BENCHMARK_CHANGELOG.md` with a new freeze record. Never to change scores |

## 2. Splits

The split is a function of the family id. Siblings and variants never cross splits.

| Split | Families | Use |
|---|---|---|
| train | 165 | prompt development, learned-router training, probe training |
| dev | 72 | calibration pilot and pilot only |
| test | 63 | the single frozen final evaluation. The code refuses it without `--allow-test` |

## 3. Models and settings

**Pilot:** GPT-5.6 Sol and Claude Sonnet 5.5.
**Main evaluation (planned):** GPT-5.6 Sol, Claude Opus 5.5, Gemini 4 Argon, and one smaller model.

| Setting | Rule |
|---|---|
| Budget | **Default $0.** No real call is possible until `--budget-usd` is given explicitly. The ledger is a hard stop across runs |
| Output tokens and reasoning | Per model in `configs/models.json`, or overridden per run with `--override MODEL.settings.FIELD=VALUE`. Overrides are recorded in the summary |
| Open decision | The cap of 1,000 tokens includes reasoning/thinking on both APIs (RISKS #1). Decide cap and effort from the smoke test before calibration |
| Sampling | None sent. Claude Sonnet 5.5 rejects temperature; GPT-5.6 Sol support is unverified |
| Structured output | The same JSON schemas for both providers (`SCHEMA_VERSION` msep-schemas-v2, snapshot-tested) |
| Refusal fallback | Off: a fallback would answer with a different model |
| Checks before any call | `experiments/check_config.py` (configuration, prices, keys), smoke gate (stops on truncation, refusal or parse error), freeze verification |

## 4. Experiments in the pilot

| Exp. | Question | Modes | Pool |
|---|---|---|---|
| E1 | Base competence: answer Q when the state is already sufficient | direct question; End-to-End on ALREADY_SUFFICIENT | `decision`, `plan` |
| E3 | Resource diagnosis | Detection-Controlled (primary), End-to-End | `plan` |
| E5 | Relevance vs sufficiency: judge matched candidate plans; construct plans when decoys are offered | judgment; Detection-Controlled, Diagnosis-Controlled | `judgment`, `plan` |
| E7 | BOTH vs single-resource | all three modes | `plan` |
| E14 (opt-in) | Computation-capability control (§9) | direct task, no planning | `capability` |

**Calibration size:** 10 dev families, 278 calls per model. Worst case at a 1,000-token cap: $3.78 for Claude Sonnet 5.5; GPT-5.6 Sol's cost depends on its price.

## 5. Modes

| Mode | Prompt adds | Eligible instances |
|---|---|---|
| End-to-End | nothing | all |
| Detection-Controlled (primary) | "The current state is not yet sufficient…" | all except ALREADY_SUFFICIENT |
| Diagnosis-Controlled | also the correct resource class | INFORMATION_ONLY, COMPUTATION_ONLY, BOTH |

Each result names its mode. End-to-End errors are never reported as planning failures.

- **Mode decomposition** (same instance across modes) attributes each failure to detection, diagnosis or planning.
- **Instruction compliance:** a response that contradicts the facts a controlled mode states is counted separately.

## 6. Reporting units (all reported; none hidden)

1. **Full v3: the primary distribution.**
2. **`heuristic_hard`: a pre-registered stress-test subset.** These are instances where the text-only h1pp baseline fails, determined from the prompt text alone.
   - It contains **no NEITHER items**, because h1pp solves every NEITHER instance.
   - Its class and motif mix differ from the full set (`results/audit_v3` §4d).
   - Compare within class only, never pooled against the full set. It is never the sole primary benchmark.
3. **Each resource class**, and each mode.
4. **Shallow heuristics h1, h1p, h1pp** on the same instances. Paired model vs h1pp: McNemar and paired difference on plan optimality.

## 7. Metrics

- **Diagnosis:** class accuracy, macro-F1, balanced accuracy, confusion matrix.
- **Plans:** plan sufficiency, inclusion-minimality, optimality, excess cost, regret.
  - Any sufficient plan at optimal cost counts as optimal.
  - Precision and recall are measured against the closest optimal plan (tested with ties).
- **E5:** accuracy on sufficient vs relevant-but-insufficient candidates; matched-pair accuracy.
- **E7:** plan sufficiency by class; BOTH plans that use only one resource.
- **Hierarchical:** A_D, A_G, A_P, A_S, A_E2E. **Calibration:** Brier, ECE.
- **Failure taxonomy (first failing stage):** detection, diagnosis, targeting, sufficiency, minimality, stopping.
- **Cost and tokens:** exact provider-reported input, output and reasoning tokens and cost per request; distributions per pool; total per model.
- **Unparseable, refused, truncated or failed responses count as incorrect** and are reported separately.

## 8. Hypotheses and statistics

**Confirmatory** (test split only, per model, Detection-Controlled, full v3): exact two-sided McNemar on matched pairs, Holm across the four, α = 0.05. Effect sizes: paired differences with 95% family-clustered bootstrap intervals; Cohen's h.

| ID | Claim | Pairs | Supported if |
|---|---|---|---|
| H2 | Diagnosis is easier than sufficient planning | class correct vs plan sufficient, per resolvable instance | Holm p < 0.05 and difference > 0 |
| H3 | Relevance is confused with sufficiency | correct judgment of the optimal plan vs of a relevant-but-insufficient plan | Holm p < 0.05 and difference > 0 |
| H4a | BOTH is harder than INFORMATION_ONLY | plan sufficient, INFORMATION_ONLY sibling vs BOTH sibling, per family | Holm p < 0.05 and difference > 0 |
| H4b | BOTH is harder than COMPUTATION_ONLY | as H4a with COMPUTATION_ONLY | as H4a |

- **Pre-registered secondary:** the same tests on `heuristic_hard` (E3/E7 classes present there), and model vs h1pp.
- **Exploratory:** everything in the pilot; H1, H5; E10–E12; E14.
- Families of the same sibling type that are missing in a family (v3 trap siblings are optional) are excluded from the paired tests that need them; the counts are reported.

## 9. Certified computation: assumption and control (E14)

- **Assumption.** COMPUTE means certified computation whose result is not yet in the decision state. A model that settles a computational fact internally has not run the certified procedure. Under the declared rule its decision is not justified, even if correct.
- **Risk.** The benchmark could then measure tool-policy compliance, not epistemic planning.
- **Control (E14).**
  1. Ask each certified task directly, with no planning context, to measure internal capability per task kind.
  2. For instances that need computation, compare how often the model's plan skips the needed computation when it is capable of the task vs when it is not.

  A higher skip rate when capable indicates policy substitution, not a failure to see the need.
- **Reporting.** Diagnosis and planning results on COMPUTATION_ONLY and BOTH are reported both overall and excluding instances where the model was internally capable on every needed task.
- **Optional exploratory condition (dev only).** A relaxed instruction that allows uncertified own computation, to see whether plans change. Not implemented as a default prompt; requires a protocol amendment.

## 10. Mitigation (planned, not run)

- **Candidate:** the realistic Epistemic Obligation Planner.
  - **S2:** an LLM extracts the formal state as JSON (`controllers/llm_extractor.py`); the planner plans on it.
  - **S4:** LLM-estimated action effects (not yet built).
- **Compared against:** native LLM, confidence threshold, ask-vs-think heuristic, learned router (train only), information-only and computation-only planners, h1–h1pp, and the oracle.
- **Additional reported metric:** extraction accuracy, the formal state compared with the true state.
- The rule-based parser condition is a tool-use upper bound. The oracle planner (A) is never a mitigation. **No mitigation claim before this evaluation.**

## 11. Budget and logging

- Every request and response is kept raw with its tokens and cost.
- `run_log.jsonl` holds per-job events. `spend_ledger.jsonl` is the cumulative spend; the budget is a hard stop.
- Each job is retried at most 3 times after errors.

## 12. Freezing this protocol

After the calibration pilot, on dev, only these may change:
- prompt wording, bumping `PROMPT_VERSION`;
- token, effort and budget settings;
- the decision on E14 and on any relaxed-instruction condition.

Then:
1. Set the status above to FROZEN with the date.
2. Record the commit, prompt version, schema version and freeze-record hash here.
3. Tag the commit.

The test run uses only that tag.
