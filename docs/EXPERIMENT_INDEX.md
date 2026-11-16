> **Superseded.** This index was written on 2026-11-14, before the held-out results and the follow-up studies. The current record is [`experiments/experiment_registry.md`](../experiments/experiment_registry.md).

# Experiment index

Evidence map for "What Would Be Enough? Evaluating Minimal Sufficient Epistemic Plans in LLM Agents".
Written 2026-11-14 against commit `9bf8315`. Dev-split results only. The held-out run and the robustness run were in progress; their result files were not opened and none of their numbers is here.

## Contents

1. [How to read this index](#1-how-to-read-this-index)
2. [Status at a glance](#2-status-at-a-glance)
3. [Hypotheses](#3-hypotheses)
4. [Experiments](#4-experiments)
   - [4.1 E0 oracle validation](#41-e0-oracle-validation)
   - [4.2 Shortcut audit v2 → v3 and heuristic baselines](#42-shortcut-audit-v2--v3-and-heuristic-baselines)
   - [4.3 Calibration on 10 dev families](#43-calibration-on-10-dev-families)
   - [4.4 v3 dev, E1–E9 in three modes](#44-v3-dev-e1e9-in-three-modes)
   - [4.5 T1 pilot](#45-t1-pilot)
   - [4.6 T1B](#46-t1b)
   - [4.7 EOP on dev: registered conditions A, B, C](#47-eop-on-dev-registered-conditions-a-b-c)
   - [4.8 EOP on dev: amended condition C′](#48-eop-on-dev-amended-condition-c)
   - [4.9 EOP on dev: Bt and Dt](#49-eop-on-dev-bt-and-dt)
   - [4.10 EOP on dev: verifier ablation D, D′](#410-eop-on-dev-verifier-ablation-d-d)
   - [4.11 Parser baseline P](#411-parser-baseline-p)
   - [4.12 Held-out evaluation (design only)](#412-held-out-evaluation-design-only)
   - [4.13 Linguistic robustness (design and model-free facts only)](#413-linguistic-robustness-design-and-model-free-facts-only)
   - [4.14 Not run](#414-not-run)
5. [Known defects in analysis outputs](#5-known-defects-in-analysis-outputs)
6. [Protocol amendments and deviations](#6-protocol-amendments-and-deviations)
7. [Built before the sprint vs during the sprint](#7-built-before-the-sprint-vs-during-the-sprint)

## 1. How to read this index

Each experiment is traced along one chain: hypothesis → protocol (registration and section) → frozen data (freeze record) → model configuration → raw responses → analysis script → result file and key → figure or table → the claim, with its evidence tier.

**Evidence tiers.** Every finding carries one.

| Tier | Meaning | Where it applies |
|---|---|---|
| 1 | Registered confirmatory: protocol, analysis and decision rule fixed and frozen before any response | EOP test C − A on dev; T1 pilot decision rules; held-out families F0, F1, F2 (pending) |
| 2 | Prospectively registered follow-up: motivated by an earlier exploratory finding, then registered before any response on new items | T1B (H-OI); linguistic robustness (pending) |
| 3 | Development-informed amended condition: added after seeing dev data | C′, D′ (Amendment 1); Bt, Dt (Amendment 2, analysis only) |
| 4 | Exploratory: descriptive, no registered test on this split | Calibration; H1–H5 on dev; secondary paired differences; cost figures |
| 5 | Model-free reference | Oracle (E0), shortcut audit, heuristics h1/h1p/h1pp, fixed policies, parser P, robustness dataset validation |

The paper draft (§11.1) numbers its own five tiers for the mitigation only. They are not these tiers: its tier 1 is the registered C result, 2 is C′/D′, 3 is Bt/Dt, 4 is the held-out confirmation, 5 is exploratory.

**Conventions.**

- Model order in every list of numbers: qwen3.5-397b / qwen3.8-27b / deepseek-v4-flash / gemma +schema. A list of three covers the first three.
- Modes: E2E (End-to-End), DC (Detection-Controlled, primary), DxC (Diagnosis-Controlled).
- Rates are on the "all attempted" basis unless stated: an unparsed, truncated or failed answer counts as wrong. Intervals are 95% family-clustered bootstrap.
- `<key>` is a model key from [configs/models.json](../configs/models.json): the model name with a provider prefix, and the suffix `-schema` for the forced-schema condition.
- Checked for this index on 2026-11-14: every number was read from the named result file, and all freeze records were re-verified (§6). Raw responses were not opened. A statement that rests on a document only names the document.

**Result files (shorthand used below).**

| Tag | File | Written by |
|---|---|---|
| ORACLE | [results/oracle_validation.json](../results/oracle_validation.json), [.md](../results/oracle_validation.md) | `experiments/e0_oracle_validation.py` |
| AUDIT2, AUDIT3 | [results/audit_v2/](../results/audit_v2/), [results/audit_v3/](../results/audit_v3/) `benchmark_audit.{json,md}` | `experiments/benchmark_audit.py` |
| BASE3 | [results/baselines_v3/report.md](../results/baselines_v3/report.md) | `experiments/run_offline.py --baselines-only` |
| CAL | [results/aggregate/diagnostics_2026-11-13/diagnostics.json](../results/aggregate/diagnostics_2026-11-13/diagnostics.json), [FINDINGS.md](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md); [calibration_dev/](../results/aggregate/calibration_dev/) | `experiments/analyze_calibration.py`; `run_pilot.py` |
| V3 | [results/aggregate/v3dev/pilot_dev/summary.json](../results/aggregate/v3dev/pilot_dev/summary.json), [report.md](../results/aggregate/v3dev/pilot_dev/report.md) | `experiments/run_pilot.py --analyze-only` |
| T1 | [results/aggregate/t1_pilot_dev/t1_summary.json](../results/aggregate/t1_pilot_dev/t1_summary.json), [T1_PILOT_FINDINGS.md](../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md) | `experiments/analyze_t1.py` |
| T1B | [results/aggregate/t1b_dev/t1b_summary.json](../results/aggregate/t1b_dev/t1b_summary.json) | `experiments/analyze_t1b.py` |
| EOP | [results/aggregate/eop_dev/eop_summary.json](../results/aggregate/eop_dev/eop_summary.json) | `experiments/run_eop.py --analyze-only` |
| RBV | [data/robust_v1_validation.json](../data/robust_v1_validation.json) | `experiments/generate_robust.py` |
| GATE | [results/aggregate/GATE2_DEV_REPORT.md](../results/aggregate/GATE2_DEV_REPORT.md) | written by hand from V3, T1B, EOP |

**Models and settings** ([configs/models.json](../configs/models.json); pinned in every protocol freeze record).

| Model | Settings | Note |
|---|---|---|
| qwen3.5-397b | temperature 0.0, max_tokens 16000, streaming, max_retries 2 | served build `qwen3.5-397b-a17b-nvfp4` (V3 `by_model.<key>.usage.all.served_models`) |
| qwen3.8-27b | same | |
| deepseek-v4-flash | same | |
| gemma-4-26b-a4b-it +schema | same, plus `structured: function_tool` | forced function-tool schema; a separate condition, not comparable to plain gemma |

One sample per item. Calibration also ran plain gemma-4-26b-a4b-it and glm-5.3-flash. The proprietary models named in PROTOCOL.md §3 were not run.

**Data and freeze records.**

| Dataset | Content | Freeze record | Regenerate |
|---|---|---|---|
| `pool_v3` (benchmark v3.0) | 300 families, 2,282 states; train 165 / dev 72 / test 63 families. Dev: 545 states, 401 resolvable | [data/FREEZE_v3.json](../data/FREEZE_v3.json) (2026-11-04) | `python experiments/generate_benchmark.py --template v3 --families 300 --out data/generated/pool_v3` |
| `variants_v3`, `pool_v2` | E10–E12 variants; shallow v2 subset | FREEZE_v3.json | `experiments/generate_variants.py`; `generate_benchmark.py --template v2` |
| `t1_v1` | 1,969 pairs (3,938 items): train 1,098 / dev 469 / test 402 | [data/FREEZE_T1.json](../data/FREEZE_T1.json) (2026-11-13) | `python experiments/generate_t1.py --pool data/generated/pool_v3/instances.jsonl --out data/generated/t1_v1` |
| `robust_v1` | 18 dev families, 137 states, 4 wordings, 548 items | [data/FREEZE_ROBUST.json](../data/FREEZE_ROBUST.json) (2026-11-14) | `python experiments/generate_robust.py` |

Generated data is not in git; the freeze records pin its SHA-256. Verify with `experiments/freeze_benchmark.py --verify`, `experiments/freeze_t1.py --verify` and `experiments/freeze_protocol.py --name NAME --verify`.

**Raw responses** (archives in [results/raw/](../results/raw/)).

| Archive | Run |
|---|---|
| `pilot_calibration_2026-11-13.tar.gz`, `pilot_phase2_2026-11-13.tar.gz`, `pilot_diagnostics_2026-11-13.tar.gz` | Calibration and its diagnostics |
| `t1_pilot_raw_2026-11-13.tar.gz` | T1 pilot |
| `dev_gate2_v3_2026-11-14.tar.gz` | v3 dev E1–E9 |
| `dev_gate2_t1_2026-11-14.tar.gz` | T1B and T1 pilot items, native |
| `dev_gate2_eop_s1_2026-11-14.tar.gz`, `dev_gate2_eop_extract_2026-11-14.tar.gz` | EOP structured-prompt and extraction calls |
| `dev_gate2_logs_ledger_2026-11-14.tar.gz` | Run logs and spend ledger |
| working pool `results/raw/pilot/` (git-ignored) | Held-out and robustness responses; archived at the end of each run |

The archive-to-run mapping comes from archive names and commit messages; the archives were not unpacked.

## 2. Status at a glance

Status is one of: done (dev) · done (pre-sprint, no model) · running (held-out, protocol frozen 2026-11-14) · running (robustness, protocol frozen 2026-11-14) · partly done · not run.

| Item | What | Status | Evidence or note |
|---|---|---|---|
| E0 | Oracle validation | done (pre-sprint, no model) | ORACLE; §4.1 |
| E1 | Base decision competence | done (dev) | V3 `E1`; §4.4 |
| E2 | Insufficiency detection | done (dev) | V3 `E2` |
| E3 | Resource-class diagnosis | done (dev) | V3 `E3` |
| E4 | Exact targeting | done (dev) | V3 `E4` |
| E5 | Relevance vs sufficiency | done (dev) | V3 `E5`; two decoy metrics invalid (§5) |
| E6 | Minimality | done (dev) | V3 `E6` |
| E7 | BOTH | done (dev) | V3 `E7` |
| E8 | NEITHER / defer | done (dev) | V3 `E8` |
| E9 | Stopping | done (dev) | V3 `E9` |
| E10 | Cost sensitivity | not run | No model run. Variants frozen; runner prepared; heuristic-only rows in BASE3 |
| E11 | Risk sensitivity | not run | No model run. Variants frozen; heuristic-only rows in BASE3 |
| E12 | Structural shift | not run | No model run. The robustness study is not E12 |
| E13 | External validity | not run | Converter only; no external dataset processed |
| E14 | Computation-capability control | not run | Opt-in runner exists |
| T1 pilot | Single-edit flips, 20 dev families | done (dev) | T1; inconclusive under the registered rules; §4.5 |
| T1B | Over-intervention follow-up, 42 dev families | done (dev) | T1B; §4.6 |
| T3 | Necessity vs relevance | not run | Design only ([CHALLENGE_V4_DESIGN.md](../research/working_documents/CHALLENGE_V4_DESIGN.md)) |
| EOP A | Native answer | done (dev) | EOP `conditions.A`; no new calls |
| EOP B | Structured obligation prompt | done (dev) | EOP `conditions.B`; no parsed answer for gemma +schema |
| EOP C | Extraction v1 + planner (registered) | done (dev) | EOP `conditions.C`; §4.7 |
| EOP C′ | Extraction v2 + planner (Amendment 1) | done (dev) | EOP `conditions.C2`; three models by design, not gemma +schema; §4.8 |
| EOP D | B verified on C's extraction | done (dev) | EOP `conditions.D`; computed, no calls |
| EOP D′ | B verified on C′'s extraction | done (dev) | EOP `conditions.D2`; three models |
| EOP Bt | B parsed from message text (Amendment 2) | done (dev) | EOP `conditions.Bt`; gemma +schema only, analysis only |
| EOP Dt | Bt verified on C's extraction | done (dev) | EOP `conditions.Dt`; gemma +schema only |
| EOP P | Parser + planner, no model | done (dev) | EOP `upper_bound_parser_EOP`; §4.11 |
| S1 | Structured prompt | done (dev) | = condition B |
| S2 | Obligation verifier | done (dev) | = condition D / D′ in PREREG_EOP. Labels differ across documents (§5) |
| S3 | Epistemic Obligation Planner | done (dev) | = condition C / C′ |
| S4 | Hybrid planner | not run | Not built |
| S5 | Shift robustness vs learned router | not run | Not built; no learned router |
| Held-out evaluation | v3 test, T1 test, EOP on test | running (held-out, protocol frozen 2026-11-14) | §4.12. Chain logs show pass 1 started 2026-11-14 20:05 UTC and no "chain done" line |
| Linguistic robustness | Four rewordings of 137 dev states | running (robustness, protocol frozen 2026-11-14) | §4.13. Dataset validation and audit are done and model-free |

## 3. Hypotheses

H1–H6 are worded in [EXPERIMENT_PLAN.md](../research/working_documents/EXPERIMENT_PLAN.md) §2 (committed 2026-11-03). H-OI is in [PREREG_T1B.md](../PREREG_T1B.md). Held-out tests are in [PREREG_FINAL.md](../PREREG_FINAL.md) §5.

| ID | Claim as registered | Test registered in | Tested by | Dev result (source) | Tier on dev | Held-out test |
|---|---|---|---|---|---|---|
| H1 | "Models will perform better in Detection-Controlled mode than End-to-End mode, but substantial planning error will remain." | Exploratory by [PROTOCOL.md](../PROTOCOL.md) §8 | E2, mode decomposition | Plan optimal E2E → DC: 0.963→0.955 / 0.963→0.975 / 0.950→0.963 / 0.406→0.446. Share failing in all three modes: 0.00 / 0.00 / 0.00 / 0.09. V3 `by_model.<key>.plan_sufficiency_by_mode.*.optimal_all_answers`, `mode_decomposition` | 4 | None (descriptive on test) |
| H2 | "Models may correctly identify [the class] while still selecting an insufficient or wasteful plan." | PROTOCOL.md §8 (test split only) | E3 vs plan sufficiency | Class correct − plan sufficient, DC, n = 401: −0.035 / −0.005 / +0.002 / −0.090. The registered direction is positive. V3 `E3.detection_controlled.h2_paired_class_minus_sufficient` | 4 | F0: pending (held-out run in progress) |
| H3 | "Models will often choose interventions that are semantically relevant but do not actually make the decision sufficient." | PROTOCOL.md §8 (test split only) | E5 judgments | Sufficient − insufficient candidates judged correctly: −0.015 / +0.005 / +0.013 / −0.318. V3 `E5.a_judgment.paired_diff_sufficient_minus_insufficient` | 4 | F0: pending (held-out run in progress) |
| H4 | "Models will perform disproportionately worse on instances requiring mixed information + computation than on single-resource instances." | PROTOCOL.md §8 as H4a, H4b (test split only) | E7 | Plan sufficient, IO − BOTH: 0.000 / +0.028 / +0.014 / +0.028. CO − BOTH: 0.000 / +0.014 / 0.000 / +0.097. V3 `E7.detection_controlled.paired_*_minus_BOTH_plan_sufficient` | 4 | F0: pending (held-out run in progress) |
| H5 | "Even when models find a sufficient plan, they may over-consume resources or continue acting after sufficiency is achieved." | Exploratory by PROTOCOL.md §8 | E6, E8, E9, T1B | Optimal given sufficient (DC): 0.955 / 0.985 / 0.982 / 0.514. Correct defer on NEITHER (DC): 0.806 / 0.875 / 0.931 / 0.000. V3 `E6.detection_controlled.optimal_given_sufficient`, `E8.detection_controlled.correct_defer` | 4 | None (descriptive on test) |
| H6 | "An obligation-guided planner will reduce insufficient actions, premature stopping, and excess resource cost relative to confidence-based and generic routing baselines." [PREREG_EOP.md](../PREREG_EOP.md) restates it "relative to native planning and a structured prompt". | PREREG_EOP.md "Comparisons" | EOP comparison | Registered C − A, plan optimal, DC: −0.264 / −0.329 / −0.935 / +0.546. Holm p: 1 / 1 / 1 / 0.0. Supported for gemma +schema only. EOP `v3dev.models.<key>.detection_controlled.paired["C-A\|plan_optimal"]`, `v3dev.confirmatory_C_minus_A_optimal_DC` | 1 (C); 3 (C′) | F1 (EOP − A, amended method): pending (held-out run in progress) |
| H-OI | "When a single intervention makes a previously insufficient state already sufficient, models continue to propose information or computation actions that are no longer needed." | PREREG_T1B.md | T1B | O1 on 122 newly sufficient states: 0.172 / 0.000 / 0.016 / 0.680. T-OI-1 supported for qwen3.5-397b (Holm p 0.0012) and gemma +schema (Holm p 0.0). T-OI-2 supported for no model. T1B `models.<key>.{O1_into_AS,T_OI_1,T_OI_2}` | 2 | F2 (T-OI-1 only): pending (held-out run in progress) |

Notes.

- H6 was tested against native planning and a structured prompt only. The confidence-based and routing baselines named in EXPERIMENT_PLAN.md were not built (paper draft §3.3).
- A Holm p of 0.0 in a file means no bootstrap resample fell at or below the threshold.
- F1 tests the amended method. By [PREREG_FINAL.md](../PREREG_FINAL.md) §1 it cannot turn the registered dev result of C into a success.

## 4. Experiments

Every block has the same eleven fields. "§1" refers to the shared tables above. Archive names are files in [results/raw/](../results/raw/).

### 4.1 E0 oracle validation

- **Question.** Do the independent exact paths (brute force, SAT/MaxSAT, obligation planner, weighted model counting) agree?
- **Protocol.** [EXPERIMENT_PLAN.md](../research/working_documents/EXPERIMENT_PLAN.md) §5 E0, 2026-11-03. No freeze record.
- **Data.** 10,000 small and 2,000 medium random instances; 200 families (2,200 instances); 100 template-v3 families (765 instances).
- **Models and settings.** None.
- **Run.** `python experiments/e0_oracle_validation.py --small 10000 --medium 2000 --families 200 --families-v3 100`
- **Raw responses.** None.
- **Analysis script.** Same script.
- **Result files.** ORACLE → `total_checks`, `total_failed`, `checks`.
- **Figure/table.** Check table in [results/oracle_validation.md](../results/oracle_validation.md).
- **Finding.** 228,199 checks, 0 failed. T1 items, validated separately: 1,969 pairs, 0 failed checks (`data/generated/t1_v1/validation.json`; not in git, hash pinned in FREEZE_T1.json).
- **Tier and caveats.** Tier 5. Exactness is shown on the validated instance sizes only.

### 4.2 Shortcut audit v2 → v3 and heuristic baselines

- **Question.** Can the benchmark be solved from surface features or by reading one rule?
- **Protocol.** Not registered. History: [BENCHMARK_CHANGELOG.md](../research/working_documents/BENCHMARK_CHANGELOG.md); reporting units: [PROTOCOL.md](../PROTOCOL.md) §6. Run 2026-11-04. Freeze: FREEZE_v3.json.
- **Data.** `pool_v2` (3,300 instances), `pool_v3` (2,282). Probe trained on train, read on dev; test not used.
- **Models and settings.** None. Heuristics h1, h1p, h1pp read the prompt text only.
- **Run.** `experiments/benchmark_audit.py`; `experiments/run_offline.py --baselines-only` (full commands in [README.md](../README.md)).
- **Raw responses.** None.
- **Analysis script.** Same scripts.
- **Result files.** AUDIT2, AUDIT3 → `heuristic_baselines_dev`, `label_reverification_brute_force`, `shortcut_probe`. BASE3. V3 → `by_model.heuristic-h1pp`.
- **Figure/table.** [results/baselines_v3/figures/](../results/baselines_v3/figures/); paper draft Tables 2, 3.
- **Finding.** h1pp on dev, audit basis (all instances): class accuracy 1.00 and plan optimal 0.909 on v2 (n = 671); 0.747 and 0.506 on v3 (n = 545). Labels re-verified by brute force: 3,300 and 2,282, 0 mismatches. On v3 dev resolvable states (DC, n = 401): plan sufficient 0.845, plan optimal 0.586.
- **Tier and caveats.** Tier 5. h1pp still gets about half of v3 plans optimal and defers on every NEITHER state, so NEITHER results are not evidence of reasoning. `heuristic_hard` is selected on a baseline's failure: compare within class only.

### 4.3 Calibration on 10 dev families

- **Question.** Do runner, prompts and scoring work? Is there a ceiling or floor?
- **Protocol.** [PROTOCOL.md](../PROTOCOL.md) §4 and §12 (v0.2, 2026-11-04). Diagnostic; no registered test. Data freeze: FREEZE_v3.json.
- **Data.** First 10 dev families: 74 states, 54 resolvable; 278 calls per model.
- **Models and settings.** qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash, gemma-4-26b-a4b-it (plain and +schema), glm-5.3-flash (16k cap; 32k re-runs of truncated jobs). Settings as §1.
- **Run.** `experiments/run_pilot.py … --splits dev --max-families 10`, 2026-11-13. Exact invocations: `step*`, `calibration_*`, `diag*` logs (not opened).
- **Raw responses.** The three `pilot_*_2026-11-13.tar.gz` archives.
- **Analysis script.** `experiments/analyze_calibration.py`.
- **Result files.** CAL → `conditions.<name>.modes.<mode>.{suff_all,opt_all,class_acc_all}`, `versus_h1pp`.
- **Figure/table.** [results/aggregate/calibration_dev/figures/](../results/aggregate/calibration_dev/figures/); paper draft Table 4.
- **Finding.** Plan optimal, DC: 0.963 / 0.963 / 0.981 for the three stronger models; gemma +schema 0.333; plain gemma 0.259; glm-5.3-flash 0.556. Three models are at a ceiling.
- **Tier and caveats.** Tier 4. Ten families. The +schema condition changes behaviour as well as format (FINDINGS.md §1). The ceiling motivated T1.

### 4.4 v3 dev, E1–E9 in three modes

- **Question.** Where along detection → diagnosis → planning → stopping do models fail?
- **Protocol.** [PROTOCOL.md](../PROTOCOL.md) §4–§8 (v0.2, 2026-11-04; models amendment 2026-11-14). By §8 all dev values are exploratory. Freeze: FREEZE_v3.json.
- **Data.** All 72 dev families: 545 states, 401 resolvable. 2,105 requests per model (1,419 plan, 614 judgment, 72 decision).
- **Models and settings.** The four dev models (§1).
- **Run.** [experiments/chain_dev_eval.sh](../experiments/chain_dev_eval.sh) step 1; fill pass in [experiments/gate_finalize.sh](../experiments/gate_finalize.sh).
- **Raw responses.** `dev_gate2_v3_2026-11-14.tar.gz`.
- **Analysis script.** `experiments/run_pilot.py --analyze-only`; metrics in `src/msep/eval/pilot.py`.
- **Result files.** V3 → `by_model.<key>.{E1…E9, plan_sufficiency_by_mode, mode_decomposition, breakdown, error_taxonomy, versus_h1pp, usage}`. Per-model outputs: [results/aggregate/v3dev_by_model/](../results/aggregate/v3dev_by_model/).
- **Figure/table.** [results/aggregate/v3dev/pilot_dev/figures/](../results/aggregate/v3dev/pilot_dev/figures/); paper draft Tables 5, 5b, 6a–6c, 7, 8, 17, 18.
- **Finding.** Plan optimal, DC: 0.955 / 0.975 / 0.963 / 0.446; h1pp 0.586. On the 166 resolvable `heuristic_hard` states: 0.928 / 0.946 / 0.940 / 0.229. Lowest result of the stronger models: correct deferral on NEITHER (DC) 0.806 / 0.875 / 0.931.
- **Tier and caveats.** Tier 4. Three models are near ceiling, so H2–H4 have little room on dev. The summary's `experiments` field lists e1, e3, e5, e7; E2, E4, E6, E8, E9 are analyses of the same job pools. One gemma +schema response is missing (§5).

### 4.5 T1 pilot

- **Question.** When one more fact becomes known, does the model's plan change as the optimal plan does?
- **Protocol.** [PREREG_T1.md](../PREREG_T1.md) §3–§5, committed 2026-11-13 21:22 UTC, before any T1 response. Freeze: [data/FREEZE_T1.json](../data/FREEZE_T1.json).
- **Data.** `t1_v1`, dev families ranked 11–30: 133 pairs (85 direct, 48 indirect), 266 items, E2E.
- **Models and settings.** qwen3.5-397b, qwen3.8-27b, gemma +schema. deepseek-v4-flash answered these items later, as EOP condition A only.
- **Run.** `experiments/run_pilot.py --experiments t1 --t1 data/generated/t1_v1/pairs.jsonl --splits dev --skip-families 10 --max-families 20`. Logs `t1_pilot_*_2026-11-13.log` (not opened).
- **Raw responses.** `t1_pilot_raw_2026-11-13.tar.gz`.
- **Analysis script.** `experiments/analyze_t1.py`.
- **Result files.** T1 → `models.<key>.{all,direct,indirect,into_ALREADY_SUFFICIENT}.{a,b,joint,transition,excess_vs_family_perm}`.
- **Figure/table.** [t1_report.md](../results/aggregate/t1_pilot_dev/t1_report.md); paper draft Table 9.
- **Finding.** Joint accuracy on the 48 indirect pairs: 0.792 [0.667, 0.902] (qwen3.5-397b), 0.938 [0.870, 1.000] (qwen3.8-27b), 0.146 [0.048, 0.278] (gemma +schema). Inconclusive for both qwen models under the registered rules. Exploratory: qwen3.5-397b over-intervened on 10 of 55 newly sufficient states, gemma +schema on 30 of 55 (counts from T1_PILOT_FINDINGS.md).
- **Tier and caveats.** Tier 1 in form: decision rules fixed before the run; a dev pilot with no significance test. The over-intervention pattern is tier 4 and led to T1B. One registered rule is uninformative near ceiling (§5).

### 4.6 T1B

- **Question.** H-OI: do models keep proposing actions after one edit has made the state sufficient?
- **Protocol.** [PREREG_T1B.md](../PREREG_T1B.md), committed 2026-11-13 23:53 UTC, before any response on its families. Freeze: [data/FREEZE_T1B.json](../data/FREEZE_T1B.json).
- **Data.** `t1_v1`, dev families ranked 31–72: 272 pairs, 544 items. Primary: the 122 pairs whose edited state is ALREADY_SUFFICIENT. Contrast: the 42 native ALREADY_SUFFICIENT states of the same families.
- **Models and settings.** The four dev models; E2E.
- **Run.** chain_dev_eval.sh step 2; fill pass in gate_finalize.sh.
- **Raw responses.** `dev_gate2_t1_2026-11-14.tar.gz`; native contrast in `dev_gate2_v3_2026-11-14.tar.gz`.
- **Analysis script.** `experiments/analyze_t1b.py` (frozen with the registration).
- **Result files.** T1B → `models.<key>.{O1_into_AS, O1_native_AS, diff_into_minus_native, T_OI_1, T_OI_2, descriptive_into_AS, pairs_all}`.
- **Figure/table.** Paper draft Tables 10, 11, 11b; right panel of [figures/stopping_dev.png](../figures/stopping_dev.png).
- **Finding.** O1 (non-empty plan on a newly sufficient state): 0.172 [0.099, 0.256] / 0.000 / 0.016 [0.000, 0.041] / 0.680 [0.561, 0.780]. T-OI-1 (O1 > 0.05) is supported for qwen3.5-397b and gemma +schema. T-OI-2 (higher than on natively sufficient states, where O1 is 0.119 and 0.643 for those two models) is supported for no model.
- **Tier and caveats.** Tier 2. Over-intervention is shown for two models; it is not shown to be specific to the edit. The families are also v3 dev families. One native response was touched by a smoke test before registration (disclosed there).

### 4.7 EOP on dev: registered conditions A, B, C

- **Question.** H6: does planning exactly on an LLM-extracted state (C) beat native planning (A) and a structured prompt (B)?
- **Protocol.** [PREREG_EOP.md](../PREREG_EOP.md) "Conditions", "Comparisons", committed 2026-11-13 23:58 UTC, before any B, C or D response. Freeze: [data/FREEZE_EOP.json](../data/FREEZE_EOP.json) (no longer verifies; §6).
- **Data.** v3 dev (72 families; E2E and DC; primary), T1 pilot items (266), T1B items (544).
- **Models and settings.** The four dev models. Prompts: native `msep-prompts-v2-certified-compute`; B `msep-s1-obligations-v1`; C `msep-extraction-v1`.
- **Run.** chain_dev_eval.sh step 4 (`run_eop.py --conditions s3,s1`); fill pass in gate_finalize.sh.
- **Raw responses.** `dev_gate2_eop_s1_2026-11-14.tar.gz`, `dev_gate2_eop_extract_2026-11-14.tar.gz`; A from the v3 and T1 archives.
- **Analysis script.** `experiments/run_eop.py --analyze-only`.
- **Result files.** EOP → `<set>.models.<key>.<mode>.conditions.{A,B,C}`, `.paired["C-A|plan_optimal"]`, `v3dev.confirmatory_C_minus_A_optimal_DC`, `.usage.C_extraction.parse_errors`.
- **Figure/table.** Paper draft Table 12. The dev figures do not show registered C for three models (see 4.8).
- **Finding.** Registered test C − A (plan optimal, v3 dev, DC, n = 401): −0.264 [−0.328, −0.200] / −0.329 [−0.379, −0.285] / −0.935 [−0.957, −0.911] / +0.546 [0.485, 0.606]. Supported for gemma +schema only. Invalid v1 extractions: 171 / 191 / 533 / 3 of 545. B − A: −0.279 / +0.005 / −0.010; gemma +schema has no parsed B answer (1,018 of 1,018).
- **Tier and caveats.** Tier 1 for C − A; the other comparisons are registered as descriptive. The v1 prompt never showed the JSON layout, so for three models C mostly measured layout guessing. qwen3.5-397b lost 252 of 1,018 B answers to parsing, a format artefact (GATE §1).

### 4.8 EOP on dev: amended condition C′

- **Question.** With the JSON layout shown in the extraction prompt, does extraction + planner give optimal plans?
- **Protocol.** PREREG_EOP.md Amendment 1, committed 2026-11-14 11:36 UTC, before any C′ response. Freeze: [data/FREEZE_EOP_A1.json](../data/FREEZE_EOP_A1.json) (no longer verifies; §6).
- **Data.** As 4.7.
- **Models and settings.** qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash; prompt `msep-extraction-v2`. Not run for gemma +schema (its forced schema supplies the layout).
- **Run.** `run_eop.py --conditions s3v2` (in gate_finalize.sh). Logs `eop_c2_<key>.log`.
- **Raw responses.** `dev_gate2_eop_extract_2026-11-14.tar.gz`.
- **Analysis script.** As 4.7.
- **Result files.** EOP → `conditions.C2`, `paired["C2-A|plan_optimal"]`, `usage.C2_extraction.parse_errors`. The file names C′ `C2` and D′ `D2`.
- **Figure/table.** [figures/conditions_dev.png](../figures/conditions_dev.png), [figures/stopping_dev.png](../figures/stopping_dev.png); paper draft Tables 13–15.
- **Finding.** Plan optimal 1.000 on all 401 resolvable v3 dev states in both modes; 0 of 545 extractions invalid. C′ − A (DC): +0.045 [0.025, 0.069] / +0.025 [0.010, 0.040] / +0.037 [0.020, 0.058]. Correct stopping (E2E), A → C′: 0.958→1.000 / 0.931→1.000 / 0.972→1.000. On the T1 pilot items deepseek-v4-flash has 1 invalid extraction of 266 (plan optimal 0.995).
- **Tier and caveats.** Tier 3. Prompt v2 was written after the v1 failures were seen on these items: the dev score is optimistic and is not the registered result. No p value for C′ − A in the dev file. In both dev figures "EOP" is C′ for three models and registered C for gemma +schema.

### 4.9 EOP on dev: Bt and Dt

- **Question.** What does the structured prompt score for gemma +schema if its answer is read from message text?
- **Protocol.** PREREG_EOP.md Amendment 2, committed 2026-11-14 13:32 UTC. Analysis only. Freeze: [data/FREEZE_EOP_A2.json](../data/FREEZE_EOP_A2.json) (no longer verifies; §6).
- **Data.** As 4.7.
- **Models and settings.** gemma +schema only.
- **Run.** No new calls.
- **Raw responses.** The existing B responses.
- **Analysis script.** As 4.7.
- **Result files.** EOP → `conditions.{Bt,Dt}`, `paired["Bt-A|plan_optimal"]`.
- **Figure/table.** Paper draft Tables 13, 14. In `figures/conditions_dev.png` the gemma B and V markers are Bt and Dt.
- **Finding.** Bt plan optimal: 0.394 (DC), 0.481 (E2E), with 278 of 473 and 260 of 545 answers still unparsed. Bt − A: −0.052 [−0.131, 0.030] (DC), +0.075 [−0.005, 0.149] (E2E).
- **Tier and caveats.** Tier 3, added after the data were seen. Registered B and D stand (no parsed answer). The registration assumed the provider would enforce the forced call; it did not.

### 4.10 EOP on dev: verifier ablation D, D′

- **Question.** Is pruning B's plan against the extracted state, with no search, enough?
- **Protocol.** PREREG_EOP.md "Conditions" D; D′ in Amendment 1; Dt in Amendment 2. Freeze records as 4.7–4.9.
- **Data.** As 4.7.
- **Models and settings.** D: four models. D′: three models. Dt: gemma +schema.
- **Run.** No calls of its own (B call + extraction call).
- **Raw responses.** As 4.7 and 4.8.
- **Analysis script.** As 4.7.
- **Result files.** EOP → `conditions.{D,D2,Dt}`, `paired["C2-D2|plan_optimal"]`, `["D2-B|plan_optimal"]`, `["C-Dt|plan_optimal"]`.
- **Figure/table.** Marker "V" in `figures/conditions_dev.png`; paper draft Table 14.
- **Finding.** Plan optimal, DC. Registered D: 0.504 / 0.641 / 0.025. D′: 0.736 / 0.993 / 0.970. C′ − D′: +0.264 [0.222, 0.307] / +0.007 [0.000, 0.020] / +0.030 [0.015, 0.046]. gemma +schema: Dt 0.406; C − Dt +0.586 [0.527, 0.644].
- **Tier and caveats.** D is registered and descriptive; D′ and Dt are tier 3. D and D′ inherit B's unparsed answers: for qwen3.5-397b, 122 of 473 DC items have none, so most of its C′ − D′ gap is format, not search.

### 4.11 Parser baseline P

- **Question.** What does the same planner score on a rule-based parse of the prompt, with no model?
- **Protocol.** Upper bound U in PREREG_EOP.md "Conditions"; baseline P in [PREREG_FINAL.md](../PREREG_FINAL.md) §3 and [PREREG_ROBUST.md](../PREREG_ROBUST.md) §2.
- **Data.** The dev item sets of 4.7; the 548 robustness items for the last sentence of the finding.
- **Models and settings.** None. Parser `parse_state` in `src/msep/benchmark/parsing.py`; planner `src/msep/controllers/realistic_planner.py`.
- **Run.** Inside `run_eop.py --analyze-only`; `generate_robust.py` for the variants.
- **Raw responses.** None.
- **Analysis script.** As 4.7.
- **Result files.** EOP → `<set>.upper_bound_parser_EOP.<mode>.{optimal_all,stop_ok_AS_NEITHER,unparsed_items,n_resolvable}`. RBV → `by_kind.<kind>.benchmark_parser_exact`.
- **Figure/table.** Marker "P" in `figures/conditions_dev.png`; paper draft Tables 12, 13.
- **Finding.** Plan optimal 1.000, correct stopping 1.000, 0 unparsed on v3 dev (401 resolvable, both modes), T1B (383) and T1 pilot (192). On the reworded items the parser recovers the state from 137 of 137 reorder variants and 0 of 137 lexical, syntax and prose variants.
- **Tier and caveats.** Tier 5. The parser inverts the benchmark's own renderer and was written by the benchmark authors. Its score says nothing about other wordings.

### 4.12 Held-out evaluation (design only)

- **Question.** Do the registered tests hold on the untouched test split: F0 (H2, H3, H4a, H4b), F1 (EOP − A, amended method), F2 (T-OI-1)?
- **Protocol.** [PREREG_FINAL.md](../PREREG_FINAL.md) §3–§6, committed 2026-11-14 20:04 UTC; first chain step logged 20:05 UTC. Freeze: [data/FREEZE_FINAL.json](../data/FREEZE_FINAL.json) (verifies).
- **Data.** Test split: 63 families, 468 states; 402 T1 pairs (804 items). 5,567 calls per model.
- **Models and settings.** The four dev models, unchanged. EOP is C′ for three models and registered C for gemma +schema. Registered C is not run on test for the other three.
- **Run.** [experiments/chain_final.sh](../experiments/chain_final.sh) per model, then [experiments/final_finalize.sh](../experiments/final_finalize.sh).
- **Raw responses.** Working pool, archived at the end of the run. Logs `final_chain_<key>.log`.
- **Analysis script.** `run_pilot.py --analyze-only`, `run_eop.py --allow-test --analyze-only`, `experiments/analyze_final.py`.
- **Result files.** Expected under `results/aggregate/final_test/` (per final_finalize.sh). Not opened.
- **Figure/table.** Shells 12-T, 12-T2, 16-T, 10-T in paper draft §11.5.
- **Finding.** Pending.
- **Tier and caveats.** Tier 1 once complete. F1 is evidence for the amended method only. Holm correction is within each family of tests, not across them.

### 4.13 Linguistic robustness (design and model-free facts only)

- **Question.** Does extraction, and EOP with it, survive rewording? Does an LLM extractor then give anything the parser does not?
- **Protocol.** [PREREG_ROBUST.md](../PREREG_ROBUST.md) §1–§4, committed 2026-11-14 20:20 UTC; first chain step logged 20:20 UTC. Freeze: [data/FREEZE_ROBUST.json](../data/FREEZE_ROBUST.json) (verifies). One registered test: EOP − A on plan optimality, pooled over wordings.
- **Data.** `robust_v1`: 18 dev families (positions 0, 4, 8, …), 137 states, four wordings (lexical, syntax, reorder, prose), 548 items. 2,192 calls per model.
- **Models and settings.** The four dev models; E2E. Conditions A, B, EOP (frozen configuration), EOP-N (normalising extraction prompt v3), P.
- **Run.** [experiments/chain_robust.sh](../experiments/chain_robust.sh), then `experiments/run_robust.py --analyze-only`.
- **Raw responses.** Working pool, archived at the end of the run. Logs `robust_chain_<key>.log`.
- **Analysis script.** `experiments/run_robust.py`.
- **Result files.** Model-free: RBV → `by_kind.<kind>.{inverse_exact,benchmark_parser_exact}`, `n_failures`. Audit: [ROBUST_AUDIT.md](../ROBUST_AUDIT.md), [results/aggregate/robust_dev/audit/](../results/aggregate/robust_dev/audit/). Model outcomes: not opened.
- **Figure/table.** Shells R1–R4 in paper draft §11.6.
- **Finding.** Model results pending. Model-free: all 548 variants pass validation (137 of 137 per wording recovered by the inverse parser; 0 failures). The benchmark's own parser reads 137 of 137 reorder variants and 0 of 137 of each other wording. Audit: one language-model reader recovered the true state from 24 of 24 sampled train-split variants (ROBUST_AUDIT.md; not recomputed here).
- **Tier and caveats.** Tier 2 when complete; the validation is tier 5. The variants are still template-made. The audit reader was a language model, not a person, and read the texts before the last wording fix. Nothing found here changes the test run (PREREG_FINAL.md §7).

### 4.14 Not run

| Item | What exists | Source |
|---|---|---|
| E10 cost sensitivity | Frozen variants (`variants_v3/cost.jsonl`), runner flag `--experiments e10`, tests. No model run | [ROADMAP_MATRIX.md](../research/working_documents/ROADMAP_MATRIX.md); CAL FINDINGS.md §5 |
| E11 risk sensitivity | Frozen variants (`risk.jsonl`); analysis not wired into the driver. No model run | ROADMAP_MATRIX.md |
| E12 structural shift | Variants (`shift.jsonl`; theme shift only on v3). No model run | ROADMAP_MATRIX.md |
| E13 external validity | Converter only | ROADMAP_MATRIX.md; [CLAIMS.md](../research/working_documents/CLAIMS.md) |
| E14 computation capability | Opt-in runner and analysis. No model run | PROTOCOL.md §9 |
| T3 necessity vs relevance | Design text only | CHALLENGE_V4_DESIGN.md §3 |
| S4 hybrid planner | Not built | ROADMAP_MATRIX.md |
| S5 shift robustness vs router | Not built | ROADMAP_MATRIX.md |
| 64 dev T1 pairs of the 10 calibration families | Generated, in no item set (469 − 133 − 272) | Derived from PREREG_T1.md §1, T1, T1B |

## 5. Known defects in analysis outputs

| Defect | Effect | Recorded in |
|---|---|---|
| E5 fields `decoy_selected` and `decoy_only_plan` are invalid on v3. The code looks for v2 action names; both are 0.00 for every agent, including the always-ask policy | Do not read them from V3 or its report | GATE "Corrections"; paper draft §12.1 (H3). Checked in V3 `by_model.policy-always_ask.E5.b_construction` |
| The v3 dev report prints the dev H2–H4 p values under "Confirmatory tests" (and cites PROTOCOL.md §4; the tests are in §8). The JSON key is also `confirmatory` | On dev they are descriptive. They are confirmatory on the test split only | GATE "Corrections"; paper draft §8.7 |
| One gemma +schema DxC response is missing and is dropped from the denominator (400, not 401; 2,104 of 2,105 requests) | Small deviation from the all-attempted rule | Paper draft §8.7, §13 |
| One gemma +schema native response is missing on the T1B items (543 of 544). The EOP analysis counts it as a failure (13 unparsed of 544) | Handled differently from the row above | Seen in EOP `t1b.models.<key>.usage.A`; not found in the documents read |
| PROTOCOL.md header still reads "Not frozen" and §3 lists models that were not run. Its §12 steps (status line, recorded commit, tag) were not done; the repository has no git tag | Deviation in form. The file is pinned unchanged in FREEZE_FINAL.json | GATE "Corrections"; paper draft §8.4 |
| Structured prompt, qwen3.5-397b: 252 of 1,018 answers unparsed, first reported as 225 | Corrected in place | GATE "Corrections" |
| "Every parsed C and C′ plan is optimal" was too strong: parsed registered C is 0.977 for qwen3.8-27b | Corrected in place | GATE "Corrections" |
| The exact-match check of extracted states (545 of 545 for C′; 523 of 545 for gemma +schema C) is not stored in EOP | Rests on GATE only | GATE §1 and "Corrections"; paper draft §11.3 |
| No p value for C′ − A in the dev file | C′ − A on dev has intervals only | Paper draft §11.3; the held-out driver adds it (PREREG_FINAL.md §8) |
| T1 "edit-tracking failure" rule is formally met near ceiling by construction | Reported, not changed; not evidence of a failure | T1_PILOT_FINDINGS.md; paper draft §9.3 |
| Planned analyses absent from the result files: Cohen's h; H2–H4 on `heuristic_hard`; paired DC − E2E difference; redundant vs minimal-but-dearer split on the 72-family run | Not reported | Paper draft §13 |
| Labels differ: the code and PROTOCOL.md §10 call the extractor condition S2; PREREG_EOP.md calls it S3 and uses S2 for the verifier. Result keys: `C2`, `D2` for C′, D′; `upper_bound_parser_EOP` for P | Naming only | Paper draft §10.2 |
| Amendment 1 quotes interim invalid-extraction counts (deepseek-v4-flash 525 of 538); the final file has 533 of 545 | Use EOP | PREREG_EOP.md Amendment 1 vs EOP `usage.C_extraction.parse_errors` |
| Stale documents: ROADMAP_MATRIX.md (status of 2026-11-14 00:05 UTC, shows dev runs as "running"); CLAIMS.md (2026-11-04, "No language model has been evaluated"); HELDOUT_PLAN.md (superseded draft) | Use this index and GATE for status | The documents themselves |

## 6. Protocol amendments and deviations

Times are UTC, from git commit timestamps and the `===` marker lines of the chain logs.

| When (UTC) | Change | Recorded in |
|---|---|---|
| 2026-11-13 21:22 | T1 registered and frozen. No amendment since | PREREG_T1.md; FREEZE_T1.json |
| 2026-11-13 23:53, 23:58 | T1B and EOP registered and frozen. Both documents date themselves 2026-11-14 (UTC); the commits are minutes before midnight. First T1B step logged 2026-11-14 02:43, first EOP step 04:03 | PREREG_T1B.md; PREREG_EOP.md; `chain_<key>.log` |
| 2026-11-14 00:08 | PROTOCOL.md amended to name the models actually used | PROTOCOL.md header |
| 2026-11-14 11:36 | **PREREG_EOP Amendment 1.** New conditions C′ and D′ with extraction prompt v2 (the v1 text plus the exact JSON template). Reason: a pipeline check of extraction validity showed most v1 extractions invalid for the three models without schema enforcement. Decided before any C or D outcome was scored, but after seeing dev data. C and D are reported as registered. The freeze record was written twice within two minutes (`4947810`, then `6ff8d16` after the C′ pools were renamed) | PREREG_EOP.md; FREEZE_EOP_A1.json |
| 2026-11-14 13:32 | **PREREG_EOP Amendment 2.** Analysis-only conditions Bt and Dt for gemma +schema, which answered the structured prompt as message text with no function call in all 1,018 v3 dev responses. No new calls | PREREG_EOP.md; FREEZE_EOP_A2.json |
| 2026-11-14 20:04 | **PREREG_FINAL §8**, before any test response. `experiments/run_eop.py`: item sets `v3test` and `t1test` behind `--allow-test`; one-sided p also for C′ − A; a block for F1; no change to prompts, planning, verification or scoring. New files: `experiments/analyze_final.py`, `src/msep/eval/extraction_match.py`, `experiments/chain_final.sh`, `experiments/final_finalize.sh` | PREREG_FINAL.md §8; FREEZE_FINAL.json |
| 2026-11-14 20:04 | Registration differs from the draft [HELDOUT_PLAN.md](../research/working_documents/HELDOUT_PLAN.md): EOP on test is C′ for three models and C for gemma +schema, not registered C for all; P is a baseline; T-OI-2 is descriptive; the EOP test is F1 | PREREG_FINAL.md §1, §3, §5 |
| 2026-11-14 20:20 | PREREG_ROBUST registered and frozen. One wording fix (parentheses around a negated compound statement) was made before the freeze, after the audit; all variants were regenerated and re-validated | PREREG_ROBUST.md; ROBUST_AUDIT.md |
| 2026-11-14 20:05–20:41 | Held-out chains, scheduling only: all four started 20:05; qwen3.5-397b restarted at concurrency 24 at 20:17; gemma +schema paused at 20:17 ("takes most of the shared request quota"), resumed at concurrency 3 at 20:37, restarted at concurrency 10 at 20:41 | `final_chain_<key>.log` |
| 2026-11-14 20:20–20:41 | Robustness chains, scheduling only: three started 20:20; gemma +schema started 20:37, restarted at concurrency 6 at 20:41 | `robust_chain_<key>.log` |

No dropped step was recorded in the chain logs as of the last marker line read.

**Freeze records** (re-checked 2026-11-14 with the three `--verify` commands of §1).

| Record | Result | Files that differ | Why |
|---|---|---|---|
| FREEZE_EOP | fails | `PREREG_EOP.md`, `experiments/run_eop.py`, `src/msep/controllers/llm_extractor.py` | Amendment 1 added prompt v2 and C′. The documents state the v1 prompt is byte-identical and tested in `tests/test_eop_driver.py`. Later changes as below |
| FREEZE_EOP_A1 | fails | `PREREG_EOP.md`, `experiments/run_eop.py` | Amendment 2 added its text and the Bt/Dt analysis |
| FREEZE_EOP_A2 | fails | `experiments/run_eop.py` | PREREG_FINAL §8 added the test item sets and the F1 block |
| FREEZE_v3, FREEZE_T1, FREEZE_T1B, FREEZE_FINAL, FREEZE_ROBUST | OK | none | FREEZE_FINAL pins the current versions of the files above |

## 7. Built before the sprint vs during the sprint

The sprint ran 2026-11-13 to 2026-11-15. Dates here are git author dates in the author's local time zone (UTC−8 for the sprint commits), so they can differ by a day from the UTC times of §6. At commit `9bf8315` there are 16 commits dated 2026-11-03 or 2026-11-04 and 44 from 2026-11-13 on. CLAIMS.md of 2026-11-04 states that no language model had been evaluated, and no commit lies between 2026-11-04 and 2026-11-13.

| Period | Commits | What they contain |
|---|---|---|
| 2026-11-03 | 7 (`8ca8190` … `106a8c0`) | Specification documents, including H1–H6 and the E0–E13 plan; formal environment, exact oracles, first families, tests; E0 results and mutation tests; certified-computation semantics; model runner and E1/E3/E5/E7 driver (not run); budget guard |
| 2026-11-04 | 9 (`4e90cd2` … `0b7f846`) | Benchmark audit; template v2, then template v3 after the adversarial audit; variants for E10–E12; E13 converter; text parser; realistic planner; LLM extractor with prompt v1; mock agents and analyses E2–E12; heuristic baselines; PROTOCOL.md v0.2; CLAIMS.md; paper skeleton; benchmark v3.0 freeze |
| 2026-11-13 | 22 (`b09f07c` … `b6a2961`) | Provider integration; calibration and diagnostics (first model calls); literature failure map and challenge-tier design; T1 generator, registration, freeze and pilot; EOP driver and structured prompt; T1B and EOP registrations and freezes; roadmap matrix; dev chain script; draft held-out plan |
| 2026-11-14 | 22 so far (`e1fb301` … `9bf8315`) | EOP Amendments 1 and 2; gate script; dev gate 2 results and raw archives; held-out registration and freeze; robustness generator, registration and freeze; paper and report drafts; figures; licensing |

What this means for the evidence.

- The benchmark, the oracle, the parser, the planner and extraction prompt v1 predate the sprint. FREEZE_v3.json (2026-11-04) still verifies, so benchmark content did not change during the sprint.
- By the commit history and CLAIMS.md, every model call was made during the sprint. So were the T1 items, the structured prompt, extraction prompts v2 and v3, the reworded items and every registration other than PROTOCOL.md and the hypotheses in EXPERIMENT_PLAN.md.
