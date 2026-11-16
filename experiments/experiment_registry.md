# Experiment registry

This registry answers one question: for every experiment of the project, which hypothesis did it address, how was it run, what did it find, how strong is that evidence, and what was decided next? It updates [`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md), which was written on 2026-11-14 before the held-out, rewording and follow-up results existed. Every number is read from the file named beside it. The final claims are those of [`paper/report.md`](../paper/report.md). Hypotheses and their outcomes are tracked in [`research/hypothesis_tracker.md`](../research/hypothesis_tracker.md); the reasons for each decision are in [`research/research_decisions.md`](../research/research_decisions.md); the plan these experiments came from is in [`research/original_roadmap.md`](../research/original_roadmap.md).

**Conventions.** Model order in lists: qwen3.5-397b / qwen3.8-27b / deepseek-v4-flash / gemma-4-26b +schema (forced function-tool schema). Modes: E2E (End-to-End), DC (Detection-Controlled), DxC (Diagnosis-Controlled). Rates are "all attempted": a failed, truncated or unreadable answer counts as wrong. Intervals are 95% family-clustered bootstrap. "Holm p < 0.001" stands for a stored value of 0.0. Times are UTC, converted from git author dates (the author worked in UTC−8; `git log --date=iso`). Settings for every model run: temperature 0.0, max_tokens 16000, one sample per item ([`configs/models.json`](../configs/models.json)).

**Evidence tiers** (kept separate everywhere): registered held-out; registered development; prospective test of an amended method; rewording study; follow-up registered after the held-out results were viewed; exploratory; no-model baseline.

## Summary

| ID | Experiment | Split | Status | One-line result | Evidence tier |
|---|---|---|---|---|---|
| X1 | E0 oracle validation | random + 300 families | completed | 228,199 checks, 0 failed | no-model baseline |
| X2 | Shortcut audit and heuristics | train/dev | completed (v2 superseded by v3) | v2 solvable from surface text; v3 h1pp plan optimal 0.586 on dev | no-model baseline |
| X3 | Calibration | dev, 10 families | exploratory | three models at ceiling (0.96–0.98) | exploratory |
| X4 | v3 dev E1–E9 | dev, 72 families | exploratory | plan optimal (DC) 0.955 / 0.975 / 0.963 / 0.446 | exploratory |
| X5 | T1 pilot | dev, 20 families | inconclusive | no model met the ceiling or gap rule | registered development |
| X6 | T1B | dev, 42 families | prospectively registered; completed | T-OI-1 supported for qwen3.5 and gemma; T-OI-2 null | registered development |
| X7 | EOP dev A/B/C | dev | prospectively registered; null result for three models | C − A supported for gemma only | registered development |
| X8 | Amended C′ | dev | exploratory | optimal 1.000 on 401 states | exploratory (development-informed) |
| X9 | Bt / Dt | dev | exploratory | gemma Bt 0.394 (DC) | exploratory |
| X10 | Verifier D / D′ | dev | completed (D registered descriptive) | D′ below C′ for all three models | registered development (D); exploratory (D′) |
| X11 | Parser P | dev, test, reworded | completed | 1.00 on benchmark text; 0.00 on three of four rewordings | no-model baseline |
| X12 | Held-out evaluation | test, 63 families | prospectively registered; completed | H2–H4 not supported; EOP − A supported for all four; T-OI-1 for qwen3.5 and gemma | registered held-out; prospective test of an amended method (EOP) |
| X13 | Rewording study | dev, 18 families | prospectively registered; completed | EOP − A supported for qwen3.8 and gemma only; EOP breaks for deepseek and gemma on syntax | rewording study |
| X14 | Study 1 clarity | train, 60 families | prospectively registered (after viewing); completed | acting on sufficient states 0.14 → 0.03 (qwen3.5), 0.73 → 0.59 (gemma) | follow-up after viewing |
| X15 | Study 2 cost (E10) | train, 60 families | prospectively registered (after viewing); null result for qwen models | gemma 0.31 above, 0.16 below the price boundary | follow-up after viewing |
| X16 | Study 3 repair | train, 12 families | exploratory; completed | gemma exact state 0.21 → 0.78, accepted-but-wrong 0.07 → 0.16 | follow-up after viewing (exploratory) |
| X17 | E11–E14, T3, S4, S5 and others | — | planned but not executed | — | — |

## Records

### X1. E0 oracle validation

- **Hypothesis / question.** Precondition, not a hypothesis: do the independent exact paths (brute force, SAT/MaxSAT, obligation planner, weighted model counting) agree?
- **Benchmark and population.** 10,000 small and 2,000 medium random instances; 200 families (2,200 instances); 100 template-v3 families (765 instances) ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.1). No split; no model.
- **Metric / test.** Agreement checks; no statistical test.
- **Registration.** [`EXPERIMENT_PLAN.md`](../research/working_documents/EXPERIMENT_PLAN.md) §5, 2026-11-03. No freeze record.
- **Result.** 228,199 checks, 0 failed ([`results/oracle_validation.md`](../results/oracle_validation.md)). T1 items: 1,969 pairs, 0 failed checks (INDEX §4.1).
- **Interpretation and limitations.** Exactness is shown on the validated instance sizes only.
- **Sources.** [`e0_oracle_validation.py`](e0_oracle_validation.py); [`methodology/oracle_validation.md`](../methodology/oracle_validation.md).
- **Next decision.** The oracle scores every later experiment.

### X2. Shortcut audit v2 → v3 and heuristic baselines

- **Question.** Can the benchmark be solved from surface features or by reading one rule?
- **Benchmark and population.** `pool_v2` (3,300 instances) and `pool_v3` (2,282). Probe trained on train, read on dev; test not used.
- **Conditions and metrics.** Heuristics h1, h1p, h1pp (prompt text only); class accuracy, plan optimality.
- **Registration.** Not registered. Run 2026-11-04; v3 frozen in [`data/FREEZE_v3.json`](../data/FREEZE_v3.json).
- **Result.** h1pp on dev: class accuracy 1.00 and plan optimal 0.909 on v2 (n = 671); 0.747 and 0.506 on v3 (n = 545). On v3 dev resolvable states (DC, n = 401): plan sufficient 0.845, plan optimal 0.586. Labels re-verified by brute force, 0 mismatches (INDEX §4.2). On the held-out split h1pp plan sufficiency is 0.88 in every mode ([`pilot_test/report.md`](../results/aggregate/final_test/v3/pilot_test/report.md)).
- **Interpretation and limitations.** v2 was superseded. h1pp still defers on every NEITHER state, so deferral on NEITHER is not evidence of reasoning.
- **Sources.** [`benchmark_audit.py`](benchmark_audit.py); [`run_offline.py`](run_offline.py); [`results/audit_v3/`](../results/audit_v3/); [`BENCHMARK_CHANGELOG.md`](../research/working_documents/BENCHMARK_CHANGELOG.md).
- **Next decision.** Template v3 frozen 2026-11-04; heuristics kept as baselines in every report.

### X3. Calibration on 10 dev families

- **Question.** Do runner, prompts and scoring work? Is there a ceiling or floor?
- **Population.** First 10 dev families: 74 states, 54 resolvable; 278 calls per model.
- **Conditions.** qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash, gemma (plain and +schema), glm-5.3-flash. Native answer, three modes.
- **Registration.** [`PROTOCOL.md`](../experiments/preregistrations/PROTOCOL.md) §4, §12 (v0.2, commit `0b7f846`, 2026-11-04 20:55 UTC). Diagnostic; no test.
- **Result.** Plan optimal (DC): 0.963 / 0.963 / 0.981; gemma +schema 0.333; plain gemma 0.259; glm-5.3-flash 0.556 (INDEX §4.3).
- **Interpretation and limitations.** Three models at ceiling on ten families. The +schema condition changes behaviour as well as format.
- **Sources.** [`analyze_calibration.py`](analyze_calibration.py); [`results/aggregate/diagnostics_2026-11-13/FINDINGS.md`](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md); archives `pilot_calibration_2026-11-13.tar.gz`, `pilot_phase2_2026-11-13.tar.gz`, `pilot_diagnostics_2026-11-13.tar.gz`.
- **Next decision.** The ceiling motivated the counterfactual pairs (T1). Four models kept for all later runs.

### X4. v3 dev, E1–E9 in three modes

- **Hypotheses.** H1–H5 ([`EXPERIMENT_PLAN.md`](../research/working_documents/EXPERIMENT_PLAN.md) §2). By PROTOCOL.md §8 all dev values are exploratory.
- **Population.** All 72 dev families: 545 states, 401 resolvable; 2,105 requests per model.
- **Conditions and metrics.** Native answer; E1 base competence to E9 stopping; plan sufficiency and optimality, class accuracy, deferral.
- **Registration.** PROTOCOL.md §4–§8 (2026-11-04); models amendment 2026-11-14 00:08 UTC (commit `1c0883e`).
- **Result.** Plan optimal (DC): 0.955 / 0.975 / 0.963 / 0.446; h1pp 0.586. Correct deferral on NEITHER (DC): 0.806 / 0.875 / 0.931 / 0.000 (INDEX §4.4, §3).
- **Interpretation and limitations.** Three models near ceiling, so H2–H4 have little room on dev. Two E5 decoy fields are invalid (see Known defects). One gemma response missing.
- **Sources.** [`chain_dev_eval.sh`](chain_dev_eval.sh); [`gate_finalize.sh`](gate_finalize.sh); [`results/aggregate/v3dev/pilot_dev/report.md`](../results/aggregate/v3dev/pilot_dev/report.md); [`GATE2_DEV_REPORT.md`](../results/aggregate/GATE2_DEV_REPORT.md); archive `dev_gate2_v3_2026-11-14.tar.gz`.
- **Next decision.** Planning hypotheses carried to the held-out split unchanged (F0).

### X5. T1 pilot (counterfactual single-edit pairs)

- **Question.** When one more fact becomes known, does the plan change as the optimal plan does?
- **Population.** `t1_v1`, dev families ranked 11–30: 133 pairs (85 direct, 48 indirect), 266 items, E2E. qwen3.5-397b, qwen3.8-27b, gemma +schema.
- **Metric and rules.** Joint pair accuracy on indirect pairs; three decision rules, no significance test.
- **Registration.** [`PREREG_T1.md`](../experiments/preregistrations/PREREG_T1.md) §3–§5, commit `7ade0ff`/`314469d`, 2026-11-13 21:22 UTC, before any T1 response.
- **Result.** Joint accuracy, indirect pairs: 0.792 [0.667, 0.902] / 0.938 [0.870, 1.000] / gemma 0.146 [0.048, 0.278]. Ceiling rule met by no model; gap rule not met (qwen3.5 upper bound 0.902). Exploratory: qwen3.5 over-intervened on 10 of 55 newly sufficient states, gemma on 30 of 55 ([`T1_PILOT_FINDINGS.md`](../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md)).
- **Interpretation and limitations.** Inconclusive for both qwen models. The edit-tracking rule is met by construction near ceiling and is uninformative.
- **Sources.** [`generate_t1.py`](generate_t1.py); [`analyze_t1.py`](analyze_t1.py); archive `t1_pilot_raw_2026-11-13.tar.gz`.
- **Next decision.** The exploratory over-intervention pattern was registered as T1B on fresh families.

### X6. T1B over-intervention follow-up

- **Hypothesis.** H-OI: after one edit makes a state sufficient, models keep proposing actions.
- **Population.** Dev families ranked 31–72: 272 pairs, 544 items; primary set 122 newly sufficient states; contrast 42 natively sufficient states. Four models, E2E.
- **Tests.** T-OI-1: O1 > 0.05, one-sided bootstrap, Holm across models. T-OI-2: higher than on natively sufficient states.
- **Registration.** [`PREREG_T1B.md`](../experiments/preregistrations/PREREG_T1B.md), commit `51223e4`/`ecb0678`, 2026-11-13 23:53 UTC.
- **Result.** O1: 0.172 [0.099, 0.256] / 0.000 / 0.016 [0.000, 0.041] / 0.680 [0.561, 0.780]. T-OI-1 supported for qwen3.5 (Holm p 0.0012) and gemma; T-OI-2 supported for no model ([`t1b_summary.json`](../results/aggregate/t1b_dev/t1b_summary.json); INDEX §4.6).
- **Interpretation and limitations.** Over-intervention shown for two models, not shown to be specific to the edit. One native response touched by a smoke test before registration (disclosed in PREREG_T1B.md).
- **Sources.** [`analyze_t1b.py`](analyze_t1b.py); archive `dev_gate2_t1_2026-11-14.tar.gz`.
- **Next decision.** T-OI-1 carried to the held-out split as F2; T-OI-2 made descriptive there.

### X7. EOP on dev: registered conditions A, B, C

- **Hypothesis.** H6 as restated in [`PREREG_EOP.md`](../experiments/preregistrations/PREREG_EOP.md): planning on an LLM-extracted state (C) beats native planning (A) and a structured obligation prompt (B).
- **Population.** v3 dev (72 families, E2E and DC; primary), T1 pilot items (266), T1B items (544). Four models.
- **Test.** C − A on plan optimality, v3 dev, DC, n = 401; one-sided bootstrap, Holm across models.
- **Registration.** PREREG_EOP.md, commit `2b5f5af`/`0dfee91`, 2026-11-13 23:58 UTC, before any B, C or D response.
- **Result.** C − A: −0.264 [−0.328, −0.200] / −0.329 [−0.379, −0.285] / −0.935 [−0.957, −0.911] / +0.546 [0.485, 0.606]; supported for gemma only (INDEX §4.7). Registered EOP optimal 0.69 / 0.65 / 0.03 / 0.99 with 150 / 163 / 461 / 3 of 473 items lacking a usable extraction ([`RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md); [`paper/report.md`](../paper/report.md) Table B1). gemma has no parsed B answer (1,018 of 1,018).
- **Interpretation.** The v1 prompt never showed the required JSON layout; for three models C mostly measured layout guessing. The registered outcome stands.
- **Sources.** [`run_eop.py`](run_eop.py); [`eop_summary.json`](../results/aggregate/eop_dev/eop_summary.json); archives `dev_gate2_eop_s1_2026-11-14.tar.gz`, `dev_gate2_eop_extract_2026-11-14.tar.gz`.
- **Next decision.** Amendment 1 (C′) and Amendment 2 (Bt/Dt).

### X8. Amended condition C′

- **Question.** With the JSON layout shown (prompt v2), does extraction + planner give optimal plans?
- **Population.** As X7; qwen3.5-397b, qwen3.8-27b, deepseek-v4-flash (not gemma: its schema supplies the layout).
- **Registration.** PREREG_EOP.md Amendment 1, commit `e1fb301`, 2026-11-14 11:36 UTC, after dev data had been seen and before any C′ response. Frozen twice (`4947810`, `6ff8d16`).
- **Result.** Plan optimal 1.000 on 401 resolvable states in both modes; 0 of 545 extractions invalid. C′ − A (DC): +0.045 [0.025, 0.069] / +0.025 [0.010, 0.040] / +0.037 [0.020, 0.058] (INDEX §4.8).
- **Interpretation and limitations.** Development-informed and optimistic: prompt v2 was written after the v1 failures were seen on these items. No p-value in the dev file.
- **Sources.** As X7; logs `eop_c2_*.log`.
- **Next decision.** C′ became the frozen EOP for three models on the held-out split (PREREG_FINAL.md §3).

### X9. Bt and Dt (analysis only)

- **Question.** What does B score for gemma if its answer is read from message text?
- **Registration.** PREREG_EOP.md Amendment 2, commit `cbe64c0`, 2026-11-14 13:32 UTC. No new calls.
- **Result.** Bt plan optimal 0.394 (DC), 0.481 (E2E), with 278 of 473 and 260 of 545 answers still unparsed. Bt − A: −0.052 [−0.131, 0.030] (DC) (INDEX §4.9).
- **Interpretation.** Registered B and D stand. The registration assumed the provider would enforce the forced call; it did not.
- **Next decision.** Bt/Dt reported beside B/D on held-out.

### X10. Verifier ablation D, D′

- **Question.** Is pruning B's plan against the extracted state, with no search, enough?
- **Registration.** D in PREREG_EOP.md "Conditions" (descriptive); D′ in Amendment 1; Dt in Amendment 2. No calls of their own.
- **Result (dev, DC).** D: 0.504 / 0.641 / 0.025. D′: 0.736 / 0.993 / 0.970. gemma Dt 0.406 (INDEX §4.10). Held-out DC "verifier only": 0.69 / 0.98 / 0.95 / 0.41 ([`RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md)).
- **Limitations.** D and D′ inherit B's unparsed answers; for qwen3.5 most of the C′ − D′ gap is format, not search.

### X11. Parser baseline P

- **Question.** What does the same planner score on a rule-based parse of the prompt, with no model?
- **Registration.** Upper bound in PREREG_EOP.md; baseline in [`PREREG_FINAL.md`](../experiments/preregistrations/PREREG_FINAL.md) §3 and [`PREREG_ROBUST.md`](../experiments/preregistrations/PREREG_ROBUST.md) §2.
- **Result.** Plan optimal 1.00 on dev and held-out (both modes) ([`RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md)). On reworded items: 1.00 on reorder, 0.00 on lexical, syntax and prose ([`robust_report.md`](../results/aggregate/robust_dev/robust_report.md)).
- **Interpretation and limitations.** The parser inverts the benchmark's own renderer and was written by the benchmark authors. On canonical text EOP adds nothing over it; its value is only shown under rewording.

### X12. Held-out evaluation

- **Hypotheses and tests.** F0: H2, H3, H4a, H4b (exact two-sided McNemar, DC, Holm across four tests per model). F1: EOP − A on plan optimality (amended H6; one-sided bootstrap, Holm across models). F2: T-OI-1. No correction across families ([`PREREG_FINAL.md`](../experiments/preregistrations/PREREG_FINAL.md) §5).
- **Population.** Test split: 63 families, 468 states (342 resolvable in DC); 402 T1 pairs (804 items), 169 newly sufficient states. 5,567 calls per model (PREREG_FINAL.md §6).
- **Conditions.** A, B, EOP (C′ for three models; registered C for gemma), D′/D, Bt/Dt, P, heuristics and fixed policies.
- **Registration.** PREREG_FINAL.md, commit `a13f9b7`/`d00ada4`, 2026-11-14 20:04 UTC; freeze [`data/FREEZE_FINAL.json`](../data/FREEZE_FINAL.json).
- **Result.**
  - F0-H2, class correct vs plan sufficient: 0.95 vs 1.00 / 0.99 vs 0.99 / 0.98 vs 0.99 / 0.77 vs 0.88; Holm p 0.000122 / 1 / 1 / 0.00023. Not supported; significant in the reverse direction for qwen3.5 and gemma ([`pilot_test/report.md`](../results/aggregate/final_test/v3/pilot_test/report.md) "Diagnosis vs planning", "Confirmatory tests").
  - F0-H3, accuracy on sufficient vs relevant-insufficient plans: 0.97 vs 1.00 / 1.00 vs 0.97 / 0.99 vs 0.98 / 0.60 vs 0.91; Holm p 0.0234 / 0.00781 / 0.5 / 2.46e-13. Supported for qwen3.8 only; reversed for qwen3.5 and gemma (same file; [`hypothesis_tracker.md`](../research/hypothesis_tracker.md)).
  - F0-H4a/H4b: Holm p 1 / 1 / 1 / 0.0781 and 1 / 1 / 1 / 0.146. Not supported (same file).
  - F1, EOP − A (DC): +0.07 [+0.04, +0.10] / +0.02 [+0.01, +0.04] / +0.02 [+0.01, +0.04] / +0.57 [+0.51, +0.62]; Holm p < 0.001 / 0.005 / 0.004 / < 0.001. EOP optimal 1.00 / 1.00 / 1.00 / 0.99; native 0.93 / 0.98 / 0.98 / 0.42; structured prompt 0.62 / 0.96 / 0.94 / 0.40 ([`RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md)).
  - F2, acting on newly sufficient states: 0.20 [0.14, 0.27] / 0.00 / 0.00 / 0.72 [0.64, 0.79]; supported for qwen3.5 and gemma (Holm p < 0.001) (same file).
  - Descriptive: defers on NEITHER (DC) 0.89 / 0.87 / 0.97 / 0.00 (same file).
- **Interpretation.** Native planning replicates near ceiling for three models. F1 is evidence for the amended method only; it does not turn the registered dev result into a success. The gain is large only for gemma, and P matches EOP on this text.
- **Limitations.** First viewed during a provider outage with one run incomplete (see Deviations). Seven gemma calls failed all three attempts and count as wrong ([`paper/report.md`](../paper/report.md) Appendix B).
- **Sources.** [`chain_final.sh`](chain_final.sh); [`final_finalize.sh`](final_finalize.sh); [`analyze_final.py`](analyze_final.py); [`eop_tables.md`](../results/aggregate/final_test/eop/eop_tables.md); logs `final_chain_*.log`; archives `final_runs_plan*`, `final_runs_extract*`, `final_runs_decision`, `final_runs_judgment`, `final_runs_heuristics`, `final_runs_logs_ledger` (all `_2026-11-15.tar.gz`; mapping to studies by archive name, not unpacked).
- **Next decision.** The re-certification split of qwen3.5's over-intervention (21 of 34 unnecessary plans re-obtain values the text lists as known; script committed 2026-11-14 22:12 UTC, before the held-out analysis) led to Study 1 ([`PREREG_FOLLOWUP.md`](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1).

### X13. Rewording study

- **Question.** Does extraction, and EOP with it, survive rewording? Does an LLM extractor give anything the parser does not?
- **Population.** `robust_v1`: 18 dev families, 137 states, four wordings (lexical, syntax, reorder, prose), 548 items, E2E; 2,192 calls per model (INDEX §4.13). Four models.
- **Conditions.** A, B, EOP (frozen configuration), EOP-N (normalising prompt v3), P.
- **Test.** One: EOP − A on plan optimality, pooled over wordings; one-sided bootstrap, Holm across models.
- **Registration.** [`PREREG_ROBUST.md`](../experiments/preregistrations/PREREG_ROBUST.md), commit `ba04b37`/`35b983b`, 2026-11-14 20:20 UTC.
- **Result.** Pooled EOP − A: +0.01 [−0.00, +0.03], Holm p 0.154 / +0.03 [+0.01, +0.06], Holm p 0.014 / −0.03 [−0.06, +0.00], Holm p 0.984 / +0.36 [+0.29, +0.43], Holm p < 0.001. EOP on syntax: 1.00 / 1.00 / 0.81 / 0.05. Parser 0.00 on lexical, syntax and prose ([`robust_report.md`](../results/aggregate/robust_dev/robust_report.md)).
- **Interpretation.** EOP holds for the two qwen models and breaks for deepseek and gemma on some wordings. EOP − P is +0.40 to +0.75, so the LLM extractor adds coverage the parser lacks.
- **Limitations.** Variants are template-made. Under EOP-N gemma's answers written as message text were scored as empty; Study 3 showed this understates EOP-N for gemma ([`paper/report.md`](../paper/report.md) §4).
- **Sources.** [`generate_robust.py`](generate_robust.py); [`run_robust.py`](run_robust.py); [`chain_robust.sh`](chain_robust.sh); logs `robust_chain_*.log`; archives `final_runs_extract_rb*`, `final_runs_plan_rb*`.
- **Next decision.** Extraction failures (gemma syntax: 118 of 137 rejected) motivated Study 3 ([`PREREG_REPAIR.md`](../experiments/preregistrations/PREREG_REPAIR.md) §0).

### X14. Follow-up Study 1: wording clarity

- **Hypothesis.** Over-intervention on sufficient states comes partly from the benchmark text, which calls every certified value "not yet known" while listing some as known.
- **Population.** First 60 train families: 436 states, 872 items (W0 original, W1 clarified); 256 ALREADY_SUFFICIENT states (60 from the start, 196 after one edit), 60 each COMPUTATION_ONLY, BOTH, NEITHER as controls. E2E, native. qwen3.5-397b, qwen3.8-27b, gemma (deepseek excluded to finish its held-out run).
- **Test.** Primary: rate of acting on the 256 sufficient states, W1 − W0 paired, one-sided bootstrap, Holm across three models. Readings fixed in advance.
- **Registration.** [`PREREG_FOLLOWUP.md`](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1, commit `fd8145c`, 2026-11-15 21:03 UTC, after the held-out results were viewed (20:23 UTC). Freeze `data/FREEZE_FOLLOWUP.json`.
- **Result.** Acts: 0.14 [0.09, 0.19] → 0.03 [0.01, 0.05], Holm p < 0.001 / 0.00 → 0.00, Holm p 0.368 / gemma 0.73 [0.67, 0.79] → 0.59 [0.51, 0.66], Holm p < 0.001 ([`followup_report.md`](../results/aggregate/followup/followup_report.md)).
- **Interpretation.** The wording contributes for qwen3.5 and gemma; the error persists without the ambiguity for gemma only. Most of qwen3.5's over-intervention came from an ambiguity in the benchmark text, which changes the reading of F2 for that model (F2 stands as measured).
- **Limitations.** A new wording intervention on new items, not a replication of F2. No premature-stop harm beyond the registered threshold ([`hypothesis_tracker.md`](../research/hypothesis_tracker.md)).
- **Sources.** [`generate_followup.py`](generate_followup.py); [`run_followup.py`](run_followup.py); [`chain_followup.sh`](chain_followup.sh); logs `followup_chain_clarity_*.log`; archive `final_runs_plan_clar_2026-11-15.tar.gz`.
- **Next decision.** The extended report's reading "what remains is stopping" was marked superseded ([`paper/extended_report.md`](../paper/extended_report.md)).

### X15. Follow-up Study 2: cost sensitivity (E10)

- **Hypothesis.** Cost insensitivity: optimal-plan rate is higher just above a price boundary than just below it, where the cheapest plan has changed.
- **Population.** 60 other train families with a complete sweep: 209 sweeps, 780 items (209 below, 209 equal, 362 above). DC, native. Same three models.
- **Test.** Above − below, one-sided bootstrap, Holm across three models.
- **Registration.** PREREG_FOLLOWUP.md §2, same commit. E10 had been planned in EXPERIMENT_PLAN.md and not started on 2026-11-14.
- **Result.** Above / below optimal: 0.95 / 0.97, −0.02 [−0.06, 0.02], Holm p 1.0; 0.95 / 0.98, −0.03 [−0.08, 0.01], Holm p 1.0; gemma 0.31 / 0.16, +0.14 [0.06, 0.23], Holm p 0.0003 ([`followup_report.md`](../results/aggregate/followup/followup_report.md)).
- **Interpretation.** Null result for the qwen models: they follow the price. Cost insensitivity supported for gemma, which picks the repriced action about equally often at every price (0.28 / 0.34 / 0.36).
- **Limitations.** EOP not run (its planner is exact given the state). Three models only.
- **Sources.** As X14; logs `followup_chain_cost_*.log`; archive `final_runs_plan_cost_2026-11-15.tar.gz`.

### X16. Follow-up Study 3: one diagnostic repair call (exploratory)

- **Question.** Does one repair call for a rejected extraction raise the share of exactly recovered states, and at what cost in accepted-but-wrong states?
- **Population.** First 12 train families not used by Studies 1–2: 87 states in the syntax and prose rewordings, 174 items. gemma and deepseek; first prompt F (frozen) or N (translating v3), each with and without repair.
- **Readings (no test).** Useful if the lower end of the gain interval exceeds 0.05; harmful if the accepted-but-wrong rise has an interval excluding 0.
- **Registration.** [`PREREG_REPAIR.md`](../experiments/preregistrations/PREREG_REPAIR.md), commit `2935522`, 2026-11-16 00:13 UTC. Exploratory by its own registration.
- **Result.** Exact state, first → with repair: gemma F 0.21 → 0.78 (gain 0.56 [0.47, 0.65]); gemma N 0.67 → 0.74 (0.07 [0.02, 0.12]); deepseek F 0.89 → 0.97 (0.09 [0.04, 0.13]); deepseek N 0.95 → 0.97 (0.02 [0.01, 0.05]). Accepted-but-wrong, gemma F 0.07 → 0.16 ([`repair_report.md`](../results/aggregate/repair/repair_report.md)); rise 0.086 [0.029, 0.150]; gemma N rise 0.023 [0.006, 0.051]; deepseek 0 ([`repair_supplement.json`](../results/aggregate/repair/repair_supplement.json)).
- **Interpretation.** By the fixed readings: useful and harmful for gemma F; harmful, not useful, for gemma N; neither for deepseek (lower end of its F gain 0.04) ([`hypothesis_tracker.md`](../research/hypothesis_tracker.md)). Repair trades visible failures for some invisible ones.
- **Limitations.** Designed with knowledge of the rewording results. The planned third arm (source-grounded typed extraction) was not run.
- **Sources.** [`run_repair.py`](run_repair.py); [`chain_repair.sh`](chain_repair.sh); [`repair_supplement.py`](repair_supplement.py); logs `repair_chain_*.log`; archives `final_runs_extract_fx*_2026-11-15.tar.gz`.

### X17. Planned but not executed

| Item | What exists | Source |
|---|---|---|
| E11 risk sensitivity | Frozen variants; no model run | [`ROADMAP_MATRIX.md`](../research/working_documents/ROADMAP_MATRIX.md) |
| E12 structural shift | Variants (theme shift only on v3); no model run. The rewording study is not E12 | INDEX §4.14 |
| E13 external validity | Converter only | INDEX §4.14 |
| E14 computation capability | Opt-in runner; no model run | PROTOCOL.md §9 |
| T3 necessity vs relevance | Design text only | [`CHALLENGE_V4_DESIGN.md`](../research/working_documents/CHALLENGE_V4_DESIGN.md) §3 |
| S4 hybrid planner; S5 shift robustness vs learned router | Not built | INDEX §4.14 |
| Confidence-based and routing baselines of H6 | Not built; H6 tested against A and B only | INDEX §3 |
| Proprietary models of PROTOCOL.md §3 | Not run | INDEX §1 |
| Study 3 third arm (typed extraction) | Not run; would touch frozen code | PREREG_REPAIR.md §0 |
| 64 dev T1 pairs of the 10 calibration families | Generated, in no item set | INDEX §4.14 |

E10, listed as not run in the index, was run as Study 2 (X15).

## Known defects in analysis outputs

The defects of [`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §5 still apply. Most important, and new ones:

| Defect | Effect | Recorded in |
|---|---|---|
| E5 fields `decoy_selected`, `decoy_only_plan` invalid on v3 (look for v2 action names) | Not to be read | GATE2_DEV_REPORT.md "Corrections" |
| Model reports print H2–H4 under "Confirmatory tests" citing PROTOCOL.md §4; the tests are in §8. On dev they are descriptive | Heading only; on test they are F0 | INDEX §5; [`pilot_test/report.md`](../results/aggregate/final_test/v3/pilot_test/report.md) |
| A missing gemma response is dropped from the denominator in the model report (341 of 342 held-out; 400 of 401 dev) but counted as wrong in the EOP analysis | Small deviation from "all attempted" | [`hypothesis_tracker.md`](../research/hypothesis_tracker.md) notes; INDEX §5 |
| No p-value for C′ − A on dev | Intervals only | INDEX §5 |
| T1 edit-tracking rule met by construction near ceiling | Uninformative | T1_PILOT_FINDINGS.md |
| Label mismatch: code and PROTOCOL.md §10 call the extractor S2; PREREG_EOP.md calls it S3. Result keys `C2`, `D2` = C′, D′ | Naming only | INDEX §5 |
| EOP-N in the rewording study scored gemma's message-text answers as empty | Understates EOP-N for gemma | [`paper/report.md`](../paper/report.md) §4; PREREG_REPAIR.md §2 |
| Frozen Study 3 analysis printed both accepted-but-wrong rates but not the registered interval of their difference | Interval computed afterwards by [`repair_supplement.py`](repair_supplement.py) | commit `1b6af3b` |
| [`EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.12–4.13 say "pending"; ROADMAP_MATRIX.md and CLAIMS.md are older still; [`paper/extended_report.md`](../paper/extended_report.md) is superseded on the stopping claim | Use this registry and `paper/report.md` | the documents themselves |
| Freeze records FREEZE_EOP, _A1, _A2 no longer verify (later amendments changed the pinned files); FREEZE_FINAL pins the current versions | Expected; not re-checked for this registry | INDEX §6 |

## Protocol amendments and deviations

Earlier entries (T1, T1B, EOP registrations; Amendments 1 and 2; PREREG_FINAL §8 changes; held-out and rewording scheduling restarts on 2026-11-14) are in [`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §6. Additions:

| When (UTC) | Event | Recorded in |
|---|---|---|
| 2026-11-14 23:28 | Network guard added: pauses run processes while the provider is unreachable, resumes after. No protocol change. On 2026-11-15 it paused runs 00:29:19–00:29:40 and 00:30:58–00:50:39 | commit `acd2207`; [`results/raw/network_guard.log`](../results/raw/network_guard.log) |
| 2026-11-15 19:57 | **Provider outage** for deepseek-v4-flash: every call answered with 504, then 502; about 190 failures in a row | [`INTERIM_NOTE.md`](../results/aggregate/final_test/INTERIM_NOTE.md) |
| 2026-11-15 20:22 | deepseek held-out run paused by hand so calls would not use up their three attempts | network_guard.log |
| 2026-11-15 20:23 | **First view under INTERIM_NOTE.md.** The note fixing the rule for missing calls was committed before any held-out summary was opened (resume with the same commands; re-run the frozen analysis on complete data if done by 2026-11-16 00:00; otherwise drop the last priority step for all models). Departs from PREREG_FINAL.md, which said the analysis runs once after all chains finish. Interim results committed 20:32 | commits `c3aed44`, `98e045d` |
| 2026-11-15 20:55–22:26 | deepseek resumed, answered again, finished 7,759 of 7,759 calls before the cut-off | network_guard.log |
| 2026-11-15 22:46 | Final held-out and rewording results on complete data. Only deepseek's rows changed (native optimal 0.73 with 108 unanswered items, then 0.98) | commit `2863f90`; [`paper/report.md`](../paper/report.md) Appendix B |
| — | **Seven gemma calls failed all three registered attempts** and count as wrong; every call of the other models has an answer | paper/report.md Appendix B |
| 2026-11-15 21:03 | Studies 1–2 registered after viewing; deepseek excluded to keep capacity for its held-out run | PREREG_FOLLOWUP.md §1 |
| 2026-11-15 22:27 – 2026-11-16 00:54 | **Chain restarts with more workers** (scheduling only, cached jobs not re-requested): qwen3.5 clarity 5 → 9 (22:27, after the deepseek run ended); qwen3.8 cost 4 → 8 (23:35); qwen3.5 cost 8 → 16 (00:25); deepseek repair 5 → 16 (00:54). gemma fill passes at 00:54 and 00:56 left 1 clarity and 2 cost calls in error | `results/raw/followup_chain_*.log`, `results/raw/repair_chain_*.log` |
| 2026-11-16 00:13 | **Study 3 message-text reading rule**: when a forced-schema answer has no function call, the frozen reader is given the message text; the function-call-only count is reported beside it. Same kind of rule as Amendment 2. For gemma N, 29 first answers were accepted by function-call reading only, 143 with the rule | PREREG_REPAIR.md §2; repair_report.md |
| 2026-11-16 00:57–01:12 | Follow-up analysis run once (00:57); Study 3 analysis run once, then [`repair_supplement.py`](repair_supplement.py) computed the one registered interval the frozen script omitted, from the same records | commits `35b07aa`, `1b6af3b` |

No deviation changed a registered outcome ([`paper/report.md`](../paper/report.md) Appendix B).

## Before the sprint and during the sprint

The sprint ran 2026-11-13 to 2026-11-15. By author-local date, the repository has 16 commits on 2026-11-03 and 2026-11-04 and 70 from 2026-11-13 to 2026-11-15 (`git log --date=short`). No commit lies between 2026-11-04 and 2026-11-13. Times above are UTC: the follow-up studies and final analyses, dated 2026-11-16 UTC, fall on 2026-11-15 local time ([`paper/report.md`](../paper/report.md) Appendix B).

- **Before the sprint** (X1, X2; PROTOCOL.md; hypotheses H1–H6): formal model, exact oracle and its validation, benchmark templates and shortcut audit, planner, extraction prompt v1, evaluation code and protocol. No language model had been called.
- **During the sprint** (X3–X16): every model run; T1 items; the structured prompt; extraction prompts v2 and v3; reworded items; every registration other than PROTOCOL.md and EXPERIMENT_PLAN.md; all analyses.
