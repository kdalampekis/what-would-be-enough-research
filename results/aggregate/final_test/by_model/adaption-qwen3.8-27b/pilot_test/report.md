# Model results: pilot_test

> `heuristic-*` rows are real deterministic baselines (no language model, text only); `policy-*` rows are fixed visible-only intervention policies (always answer / ask everything / compute everything / abstain). `mock-*` rows are synthetic fixtures.

Split(s): test · families: 63 · generated from `summary.json` by `msep.eval.report`.

Every number names its mode. End-to-End mixes detection with planning and is never read as a planning failure. Intervals are 95% family-clustered bootstrap.

## Plan sufficiency by mode (resolvable states)

![](figures/plan_sufficiency_by_mode.png)

Two bases, the same in every mode. **All answers:** an unparsed or truncated answer counts as a failure. **Parsed only:** unparsed answers are left out; the number left out is shown as `unparsed/n`. A gap between the two means output-format or truncation failures, not planning failures.

| Agent / model | E2E all | E2E parsed | DC all | DC parsed | DxC all | DxC parsed | unparsed/n (E2E, DC, DxC) |
|---|---|---|---|---|---|---|---|
| adaption-qwen3.8-27b | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.99 [0.97, 1.00] | 1.00 [0.99, 1.00] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 5/342, 3/342, 2/342 |
| heuristic-h1 | 0.70 [0.63, 0.78] | 0.70 [0.63, 0.78] | 0.70 [0.63, 0.78] | 0.70 [0.63, 0.78] | 0.70 [0.63, 0.78] | 0.70 [0.63, 0.78] | 0/342, 0/342, 0/342 |
| heuristic-h1p | 0.67 [0.58, 0.76] | 0.67 [0.58, 0.76] | 0.67 [0.59, 0.75] | 0.67 [0.59, 0.75] | 0.67 [0.58, 0.75] | 0.67 [0.58, 0.75] | 0/342, 0/342, 0/342 |
| heuristic-h1pp | 0.88 [0.84, 0.91] | 0.88 [0.84, 0.91] | 0.88 [0.84, 0.91] | 0.88 [0.84, 0.91] | 0.88 [0.84, 0.91] | 0.88 [0.84, 0.91] | 0/342, 0/342, 0/342 |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0/342, 0/342, 0/342 |
| policy-always_ask | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0/342, 0/342, 0/342 |
| policy-always_compute | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0/342, 0/342, 0/342 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0/342, 0/342, 0/342 |

## Diagnosis vs planning (H2), Detection-Controlled

| Agent / model | Class correct | Plan sufficient | Plan sufficient given class correct | McNemar p |
|---|---|---|---|---|
| adaption-qwen3.8-27b | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 1.00 [1.00, 1.00] | 1 |
| heuristic-h1 | 0.77 [0.71, 0.83] | 0.70 [0.63, 0.78] | 0.81 [0.75, 0.87] | 0.0154 |
| heuristic-h1p | 0.59 [0.51, 0.67] | 0.67 [0.59, 0.75] | 1.00 [1.00, 1.00] | 2.98e-08 |
| heuristic-h1pp | 0.77 [0.72, 0.82] | 0.88 [0.84, 0.91] | 1.00 [1.00, 1.00] | 2.91e-11 |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1 |
| policy-always_ask | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 1.00 [1.00, 1.00] | 1 |
| policy-always_compute | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 1.00 [1.00, 1.00] | 1 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1 |

## E3 Resource diagnosis

| Agent / model | Mode | Accuracy | Macro-F1 | Balanced acc. | Surface-feature baseline (all counts) |
|---|---|---|---|---|---|
| adaption-qwen3.8-27b | Detection-Controlled | 0.97 [0.95, 0.98] | 0.97 [0.96, 0.99] | 0.96 [0.94, 0.98] | 0.45 |
| adaption-qwen3.8-27b | End-to-End | 0.97 [0.95, 0.98] | 0.98 [0.96, 0.99] | 0.96 [0.94, 0.98] | 0.45 |
| heuristic-h1 | Detection-Controlled | 0.69 [0.63, 0.73] | 0.61 [0.56, 0.66] | 0.62 [0.57, 0.67] | 0.45 |
| heuristic-h1 | End-to-End | 0.69 [0.63, 0.74] | 0.61 [0.56, 0.67] | 0.62 [0.57, 0.67] | 0.45 |
| heuristic-h1p | Detection-Controlled | 0.66 [0.59, 0.73] | 0.67 [0.61, 0.73] | 0.69 [0.63, 0.75] | 0.45 |
| heuristic-h1p | End-to-End | 0.66 [0.59, 0.73] | 0.67 [0.61, 0.73] | 0.69 [0.63, 0.75] | 0.45 |
| heuristic-h1pp | Detection-Controlled | 0.81 [0.77, 0.85] | 0.80 [0.76, 0.84] | 0.80 [0.76, 0.84] | 0.45 |
| heuristic-h1pp | End-to-End | 0.81 [0.77, 0.85] | 0.80 [0.75, 0.84] | 0.80 [0.76, 0.84] | 0.45 |
| policy-always_answer | Detection-Controlled | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.45 |
| policy-always_answer | End-to-End | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.45 |
| policy-always_ask | Detection-Controlled | 0.19 [0.18, 0.21] | 0.08 [0.08, 0.09] | 0.25 [0.25, 0.25] | 0.45 |
| policy-always_ask | End-to-End | 0.19 [0.18, 0.21] | 0.08 [0.07, 0.09] | 0.25 [0.25, 0.25] | 0.45 |
| policy-always_compute | Detection-Controlled | 0.21 [0.18, 0.23] | 0.09 [0.08, 0.09] | 0.25 [0.25, 0.25] | 0.45 |
| policy-always_compute | End-to-End | 0.21 [0.19, 0.23] | 0.09 [0.08, 0.09] | 0.25 [0.25, 0.25] | 0.45 |
| policy-always_abstain | Detection-Controlled | 0.16 [0.15, 0.16] | 0.07 [0.07, 0.07] | 0.25 [0.25, 0.25] | 0.45 |
| policy-always_abstain | End-to-End | 0.16 [0.15, 0.16] | 0.07 [0.07, 0.07] | 0.25 [0.25, 0.25] | 0.45 |

![](figures/confusion_detection_controlled.png)

## E7 BOTH vs single-resource (Detection-Controlled)

| Agent / model | INFORMATION_ONLY | COMPUTATION_ONLY | BOTH | BOTH plans using one resource |
|---|---|---|---|---|
| adaption-qwen3.8-27b | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.92, 1.00] | 0.02 [0.00, 0.05] |
| heuristic-h1 | 0.84 [0.75, 0.92] | 0.73 [0.60, 0.84] | 0.68 [0.57, 0.79] | 0.16 [0.08, 0.25] |
| heuristic-h1p | 0.78 [0.67, 0.87] | 0.65 [0.52, 0.76] | 0.67 [0.54, 0.78] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | 0.89 [0.81, 0.97] | 0.90 [0.83, 0.97] | 0.87 [0.78, 0.95] | 0.00 [0.00, 0.00] |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| policy-always_compute | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## E5 Relevance vs sufficiency (judgments)

| Agent / model | Accuracy, sufficient plans | Accuracy, relevant-insufficient plans | Pairs both correct | McNemar p |
|---|---|---|---|---|
| adaption-qwen3.8-27b | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 0.97 [0.95, 0.99] | 0.00195 |
| heuristic-h1 | 0.70 [0.62, 0.78] | 0.88 [0.84, 0.92] | 0.65 [0.57, 0.73] | 0.000189 |
| heuristic-h1p | 0.47 [0.37, 0.57] | 1.00 [1.00, 1.00] | 0.49 [0.38, 0.60] | 1.04e-53 |
| heuristic-h1pp | 0.61 [0.53, 0.69] | 1.00 [1.00, 1.00] | 0.67 [0.58, 0.75] | 2.41e-35 |
| policy-always_answer | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.74e-105 |
| policy-always_ask | 0.93 [0.89, 0.96] | 0.34 [0.29, 0.39] | 0.32 [0.27, 0.37] | 1.07e-55 |
| policy-always_compute | 0.96 [0.93, 0.98] | 0.38 [0.34, 0.42] | 0.36 [0.32, 0.40] | 1.47e-54 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.74e-105 |

## E1, E2, E4, E6, E8, E9

| Agent / model | E1 base decision acc. | E2 detection acc. (E2E) | E2 over-answering | E4 exact match (DxC) | E6 optimal given sufficient (DC) | E8 correct defer (DC) | E9 premature stop (DC) | E9 continued after ex-post sufficiency (DC; compare with oracle) |
|---|---|---|---|---|---|---|---|---|
| adaption-qwen3.8-27b | 1.00 [1.00, 1.00] | 0.97 [0.96, 0.99] | 0.00 [0.00, 0.01] | 0.99 [0.99, 1.00] | 0.99 [0.99, 1.00] | 0.87 [0.79, 0.95] | 0.00 [0.00, 0.01] | 0.16 [0.11, 0.21] |
| heuristic-h1 | 0.73 [0.62, 0.84] | 0.93 [0.91, 0.94] | 0.00 [0.00, 0.00] | 0.51 [0.44, 0.58] | 0.73 [0.65, 0.80] | 0.24 [0.14, 0.35] | 0.24 [0.17, 0.31] | 0.16 [0.10, 0.22] |
| heuristic-h1p | 0.73 [0.62, 0.84] | 0.93 [0.91, 0.94] | 0.00 [0.00, 0.00] | 0.48 [0.41, 0.56] | 0.72 [0.64, 0.80] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.18 [0.12, 0.24] |
| heuristic-h1pp | 0.75 [0.63, 0.86] | 0.93 [0.91, 0.95] | 0.00 [0.00, 0.00] | 0.61 [0.54, 0.67] | 0.69 [0.62, 0.76] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.27 [0.20, 0.35] |
| policy-always_answer | 0.51 [0.38, 0.63] | 0.13 [0.13, 0.14] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | – | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | 0.51 [0.38, 0.63] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.04 [0.00, 0.10] | 0.00 [0.00, 0.00] | 0.67 [0.61, 0.73] | 0.29 [0.24, 0.34] |
| policy-always_compute | 0.51 [0.38, 0.63] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.05 [0.01, 0.10] | 0.00 [0.00, 0.00] | 0.67 [0.61, 0.73] | 0.29 [0.23, 0.36] |
| policy-always_abstain | 0.49 [0.37, 0.62] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Mode decomposition (same instances across modes; resolvable states)

An End-to-End failure that disappears in Detection-Controlled is attributed to detection/framing; a Detection-Controlled failure that disappears in Diagnosis-Controlled to diagnosis; only failures in all three modes are planning failures. Only instances whose answers parsed in all three modes are used; the number excluded is in the last column.

| Agent / model | e2e_success | e2e_fail_detection_wrong | e2e_fail_but_dc_success | dc_fail_but_dxc_success (diagnosis-attributable) | fail_in_all_modes (planning) | excluded (unparsed in some mode) |
|---|---|---|---|---|---|---|
| adaption-qwen3.8-27b | 0.99 [0.98, 1.00] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 8 |
| heuristic-h1 | 0.63 [0.55, 0.70] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.08 [0.05, 0.11] | 0.30 [0.22, 0.37] | 0 |
| heuristic-h1p | 0.59 [0.51, 0.67] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.08 [0.05, 0.11] | 0.33 [0.25, 0.42] | 0 |
| heuristic-h1pp | 0.77 [0.72, 0.82] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.11 [0.07, 0.14] | 0.12 [0.09, 0.16] | 0 |
| policy-always_answer | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0 |
| policy-always_ask | 0.23 [0.21, 0.25] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.77 [0.75, 0.79] | 0 |
| policy-always_compute | 0.25 [0.22, 0.27] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.75 [0.73, 0.78] | 0 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0 |

## Instruction compliance and hierarchical metrics

| Agent / model | DC: claims sufficient (contradicts prompt) | DxC: class differs from given | A_D | A_G | A_P (DC) | A_P' (DxC) | A_S | A_E2E |
|---|---|---|---|---|---|---|---|---|
| adaption-qwen3.8-27b | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.97 [0.96, 0.99] | 0.97 [0.95, 0.98] | 1.00 [0.99, 1.00] | 0.99 [0.98, 1.00] | 0.97 [0.95, 0.99] | 0.97 [0.95, 0.98] |
| heuristic-h1 | 0.00 [0.00, 0.00] | 0.23 [0.18, 0.29] | 0.93 [0.91, 0.94] | 0.69 [0.63, 0.73] | 0.67 [0.59, 0.74] | 0.51 [0.44, 0.58] | 0.65 [0.57, 0.73] | 0.47 [0.40, 0.52] |
| heuristic-h1p | 0.00 [0.00, 0.00] | 0.41 [0.33, 0.49] | 0.93 [0.91, 0.94] | 0.66 [0.59, 0.73] | 0.81 [0.74, 0.89] | 0.48 [0.41, 0.56] | 0.49 [0.38, 0.60] | 0.55 [0.49, 0.61] |
| heuristic-h1pp | 0.00 [0.00, 0.00] | 0.23 [0.18, 0.27] | 0.93 [0.91, 0.95] | 0.81 [0.77, 0.85] | 0.78 [0.71, 0.85] | 0.61 [0.54, 0.67] | 0.67 [0.58, 0.75] | 0.64 [0.59, 0.69] |
| policy-always_answer | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | – | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.07 [0.05, 0.09] |
| policy-always_ask | 0.00 [0.00, 0.00] | 0.77 [0.75, 0.79] | 0.87 [0.86, 0.87] | 0.19 [0.18, 0.21] | 0.04 [0.00, 0.10] | 0.01 [0.00, 0.02] | 0.32 [0.27, 0.37] | 0.01 [0.00, 0.02] |
| policy-always_compute | 0.00 [0.00, 0.00] | 0.75 [0.73, 0.78] | 0.87 [0.86, 0.87] | 0.21 [0.18, 0.23] | 0.05 [0.01, 0.10] | 0.01 [0.00, 0.02] | 0.36 [0.32, 0.40] | 0.01 [0.00, 0.02] |
| policy-always_abstain | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.87 [0.86, 0.87] | 0.16 [0.15, 0.16] | – | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.13 [0.13, 0.14] |

## Strata: shallow-heuristic difficulty and template

`heuristic_hard` = instances where the text-only h1pp baseline fails. A model's advantage over shallow reading shows only there.

| Agent / model | Stratum | Instances | DC class correct | DC plan sufficient | DC plan optimal |
|---|---|---|---|---|---|
| adaption-qwen3.8-27b | heuristic_easy | 300 | 0.96 [0.93, 0.98] | 0.99 [0.96, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | 168 | 0.99 [0.96, 1.00] | 0.99 [0.98, 1.00] | 0.98 [0.95, 1.00] |
| adaption-qwen3.8-27b | v3 | 468 | 0.97 [0.95, 0.98] | 0.99 [0.97, 1.00] | 0.98 [0.97, 1.00] |
| heuristic-h1 | heuristic_easy | 300 | 0.75 [0.69, 0.80] | 0.79 [0.71, 0.87] | 0.76 [0.68, 0.84] |
| heuristic-h1 | heuristic_hard | 168 | 0.56 [0.46, 0.66] | 0.57 [0.46, 0.68] | 0.13 [0.06, 0.20] |
| heuristic-h1 | v3 | 468 | 0.69 [0.63, 0.73] | 0.70 [0.63, 0.78] | 0.51 [0.44, 0.58] |
| heuristic-h1p | heuristic_easy | 300 | 0.84 [0.77, 0.90] | 0.80 [0.70, 0.88] | 0.80 [0.70, 0.88] |
| heuristic-h1p | heuristic_hard | 168 | 0.28 [0.17, 0.40] | 0.47 [0.35, 0.60] | 0.00 [0.00, 0.00] |
| heuristic-h1p | v3 | 468 | 0.66 [0.59, 0.73] | 0.67 [0.59, 0.75] | 0.48 [0.40, 0.56] |
| heuristic-h1pp | heuristic_easy | 300 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_hard | 168 | 0.42 [0.33, 0.52] | 0.69 [0.60, 0.77] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | v3 | 468 | 0.81 [0.77, 0.85] | 0.88 [0.84, 0.91] | 0.61 [0.54, 0.67] |
| policy-always_answer | heuristic_easy | 300 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | 168 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | v3 | 468 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | 300 | 0.17 [0.14, 0.20] | 0.23 [0.19, 0.27] | 0.01 [0.00, 0.03] |
| policy-always_ask | heuristic_hard | 168 | 0.23 [0.17, 0.30] | 0.23 [0.17, 0.30] | 0.01 [0.00, 0.02] |
| policy-always_ask | v3 | 468 | 0.19 [0.18, 0.21] | 0.23 [0.21, 0.25] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | 300 | 0.14 [0.11, 0.18] | 0.19 [0.15, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_hard | 168 | 0.33 [0.26, 0.42] | 0.33 [0.26, 0.42] | 0.01 [0.00, 0.04] |
| policy-always_compute | v3 | 468 | 0.21 [0.18, 0.23] | 0.25 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_abstain | heuristic_easy | 300 | 0.23 [0.22, 0.25] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | 168 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | v3 | 468 | 0.16 [0.15, 0.16] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Calibration (stated confidence vs plan sufficiency)

| Agent / model | Mode | n | Brier | ECE |
|---|---|---|---|---|
| adaption-qwen3.8-27b | End-to-End | 458 | 0.22 | 0.24 |
| adaption-qwen3.8-27b | Detection-Controlled | 396 | 0.36 | 0.38 |
| adaption-qwen3.8-27b | Diagnosis-Controlled | 340 | 0.36 | 0.43 |
| heuristic-h1 | End-to-End | 468 | 0.25 | 0.07 |
| heuristic-h1 | Detection-Controlled | 405 | 0.25 | 0.10 |
| heuristic-h1 | Diagnosis-Controlled | 342 | 0.25 | 0.20 |
| heuristic-h1p | End-to-End | 468 | 0.25 | 0.05 |
| heuristic-h1p | Detection-Controlled | 405 | 0.25 | 0.07 |
| heuristic-h1p | Diagnosis-Controlled | 342 | 0.25 | 0.17 |
| heuristic-h1pp | End-to-End | 468 | 0.25 | 0.21 |
| heuristic-h1pp | Detection-Controlled | 405 | 0.25 | 0.24 |
| heuristic-h1pp | Diagnosis-Controlled | 342 | 0.25 | 0.38 |
| policy-always_answer | End-to-End | 468 | 0.25 | 0.37 |
| policy-always_answer | Detection-Controlled | 405 | 0.25 | 0.50 |
| policy-always_answer | Diagnosis-Controlled | 342 | 0.25 | 0.50 |
| policy-always_ask | End-to-End | 468 | 0.25 | 0.33 |
| policy-always_ask | Detection-Controlled | 405 | 0.25 | 0.31 |
| policy-always_ask | Diagnosis-Controlled | 342 | 0.25 | 0.27 |
| policy-always_compute | End-to-End | 468 | 0.25 | 0.32 |
| policy-always_compute | Detection-Controlled | 405 | 0.25 | 0.29 |
| policy-always_compute | Diagnosis-Controlled | 342 | 0.25 | 0.25 |
| policy-always_abstain | End-to-End | 468 | 0.25 | 0.50 |
| policy-always_abstain | Detection-Controlled | 405 | 0.25 | 0.50 |
| policy-always_abstain | Diagnosis-Controlled | 342 | 0.25 | 0.50 |

## Model vs shallow heuristic h1pp (same instances, plan optimal on resolvable states)

| Model | Mode | Model minus h1pp [CI] | McNemar p |
|---|---|---|---|
| adaption-qwen3.8-27b | Detection-Controlled | 0.38 [0.31, 0.44] | 1.88e-35 |
| adaption-qwen3.8-27b | Diagnosis-Controlled | 0.38 [0.32, 0.44] | 4.22e-37 |
| adaption-qwen3.8-27b | End-to-End | 0.37 [0.31, 0.44] | 6.26e-34 |

## Breakdown: stratum x mode x resource class (plan optimal on resolvable states)

Full v3 is primary; heuristic_hard is a pre-registered stress test (it contains no NEITHER items, so compare within class).

| Agent / model | Stratum | Mode | Class | n | Class correct | Plan sufficient | Plan optimal |
|---|---|---|---|---|---|---|---|
| adaption-qwen3.8-27b | all | End-to-End | ALL | 468 | 0.97 [0.95, 0.98] | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] |
| adaption-qwen3.8-27b | all | End-to-End | ALREADY_SUFFICIENT | 63 | 1.00 [1.00, 1.00] | – | – |
| adaption-qwen3.8-27b | all | End-to-End | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | all | End-to-End | COMPUTATION_ONLY | 84 | 0.98 [0.94, 1.00] | 0.99 [0.96, 1.00] | 0.98 [0.94, 1.00] |
| adaption-qwen3.8-27b | all | End-to-End | BOTH | 180 | 0.97 [0.95, 0.99] | 0.97 [0.95, 0.99] | 0.97 [0.95, 0.99] |
| adaption-qwen3.8-27b | all | End-to-End | NEITHER | 63 | 0.89 [0.81, 0.95] | – | – |
| adaption-qwen3.8-27b | all | Detection-Controlled | ALL | 405 | 0.97 [0.95, 0.98] | 0.99 [0.97, 1.00] | 0.98 [0.97, 1.00] |
| adaption-qwen3.8-27b | all | Detection-Controlled | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.99 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | all | Detection-Controlled | BOTH | 180 | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-qwen3.8-27b | all | Detection-Controlled | NEITHER | 63 | 0.87 [0.79, 0.95] | – | – |
| adaption-qwen3.8-27b | all | Diagnosis-Controlled | ALL | 342 | 0.99 [0.99, 1.00] | 0.99 [0.99, 1.00] | 0.99 [0.98, 1.00] |
| adaption-qwen3.8-27b | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | all | Diagnosis-Controlled | BOTH | 180 | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.98 [0.96, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | End-to-End | ALL | 168 | 0.98 [0.96, 1.00] | 0.99 [0.96, 1.00] | 0.97 [0.94, 0.99] |
| adaption-qwen3.8-27b | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 1.00 [1.00, 1.00] | – | – |
| adaption-qwen3.8-27b | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.90, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.98 [0.93, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.93, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | End-to-End | BOTH | 59 | 0.97 [0.91, 1.00] | 0.97 [0.91, 1.00] | 0.97 [0.91, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Detection-Controlled | ALL | 135 | 0.99 [0.96, 1.00] | 0.99 [0.98, 1.00] | 0.98 [0.95, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.90, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.98 [0.93, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.93, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.90, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.94, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | ALL | 300 | 0.96 [0.94, 0.98] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 1.00 [1.00, 1.00] | – | – |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.97 [0.92, 1.00] | 0.97 [0.92, 1.00] | 0.97 [0.92, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | BOTH | 121 | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | End-to-End | NEITHER | 63 | 0.89 [0.81, 0.95] | – | – |
| adaption-qwen3.8-27b | heuristic_easy | Detection-Controlled | ALL | 270 | 0.96 [0.93, 0.98] | 0.99 [0.96, 1.00] | 0.99 [0.96, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.98 [0.94, 1.00] | 0.98 [0.94, 1.00] | 0.98 [0.94, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Detection-Controlled | NEITHER | 63 | 0.87 [0.79, 0.95] | – | – |
| adaption-qwen3.8-27b | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-qwen3.8-27b | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] |
| heuristic-h1 | all | End-to-End | ALL | 468 | 0.65 [0.60, 0.70] | 0.70 [0.63, 0.78] | 0.51 [0.44, 0.58] |
| heuristic-h1 | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.44 [0.33, 0.56] | – | – |
| heuristic-h1 | all | End-to-End | INFORMATION_ONLY | 78 | 0.74 [0.65, 0.84] | 0.83 [0.74, 0.92] | 0.56 [0.45, 0.68] |
| heuristic-h1 | all | End-to-End | COMPUTATION_ONLY | 84 | 0.69 [0.57, 0.80] | 0.73 [0.62, 0.83] | 0.46 [0.35, 0.58] |
| heuristic-h1 | all | End-to-End | BOTH | 180 | 0.82 [0.74, 0.89] | 0.64 [0.54, 0.74] | 0.51 [0.42, 0.62] |
| heuristic-h1 | all | End-to-End | NEITHER | 63 | 0.24 [0.14, 0.35] | – | – |
| heuristic-h1 | all | Detection-Controlled | ALL | 405 | 0.69 [0.63, 0.73] | 0.70 [0.63, 0.78] | 0.51 [0.44, 0.58] |
| heuristic-h1 | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.74 [0.65, 0.84] | 0.83 [0.74, 0.92] | 0.56 [0.45, 0.67] |
| heuristic-h1 | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.69 [0.58, 0.80] | 0.73 [0.62, 0.83] | 0.46 [0.35, 0.58] |
| heuristic-h1 | all | Detection-Controlled | BOTH | 180 | 0.82 [0.73, 0.89] | 0.64 [0.54, 0.74] | 0.51 [0.41, 0.61] |
| heuristic-h1 | all | Detection-Controlled | NEITHER | 63 | 0.24 [0.14, 0.35] | – | – |
| heuristic-h1 | all | Diagnosis-Controlled | ALL | 342 | 0.77 [0.71, 0.82] | 0.70 [0.63, 0.78] | 0.51 [0.44, 0.58] |
| heuristic-h1 | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.74 [0.65, 0.84] | 0.83 [0.74, 0.92] | 0.56 [0.45, 0.68] |
| heuristic-h1 | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.69 [0.57, 0.80] | 0.73 [0.63, 0.82] | 0.46 [0.35, 0.58] |
| heuristic-h1 | all | Diagnosis-Controlled | BOTH | 180 | 0.82 [0.73, 0.89] | 0.64 [0.53, 0.73] | 0.51 [0.41, 0.61] |
| heuristic-h1 | heuristic_hard | End-to-End | ALL | 168 | 0.45 [0.36, 0.54] | 0.57 [0.47, 0.68] | 0.13 [0.06, 0.20] |
| heuristic-h1 | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1 | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.42 [0.25, 0.61] | 0.84 [0.70, 0.97] | 0.16 [0.04, 0.29] |
| heuristic-h1 | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.49 [0.32, 0.67] | 0.60 [0.45, 0.75] | 0.11 [0.02, 0.21] |
| heuristic-h1 | heuristic_hard | End-to-End | BOTH | 59 | 0.69 [0.55, 0.82] | 0.41 [0.25, 0.56] | 0.12 [0.03, 0.22] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | ALL | 135 | 0.56 [0.46, 0.66] | 0.57 [0.46, 0.68] | 0.13 [0.06, 0.20] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.42 [0.24, 0.60] | 0.84 [0.70, 0.97] | 0.16 [0.04, 0.30] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.49 [0.33, 0.64] | 0.60 [0.45, 0.74] | 0.11 [0.02, 0.21] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.69 [0.55, 0.83] | 0.41 [0.25, 0.56] | 0.12 [0.03, 0.22] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.56 [0.46, 0.66] | 0.57 [0.47, 0.68] | 0.13 [0.06, 0.20] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.42 [0.24, 0.61] | 0.84 [0.70, 0.96] | 0.16 [0.03, 0.29] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.49 [0.33, 0.66] | 0.60 [0.45, 0.75] | 0.11 [0.02, 0.21] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.69 [0.56, 0.83] | 0.41 [0.25, 0.56] | 0.12 [0.04, 0.22] |
| heuristic-h1 | heuristic_easy | End-to-End | ALL | 300 | 0.77 [0.71, 0.81] | 0.79 [0.71, 0.87] | 0.76 [0.68, 0.85] |
| heuristic-h1 | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 0.93 [0.83, 1.00] | – | – |
| heuristic-h1 | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 0.96 [0.89, 1.00] | 0.83 [0.71, 0.94] | 0.83 [0.71, 0.94] |
| heuristic-h1 | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.92 [0.83, 1.00] | 0.87 [0.74, 0.97] | 0.87 [0.74, 0.97] |
| heuristic-h1 | heuristic_easy | End-to-End | BOTH | 121 | 0.88 [0.79, 0.94] | 0.75 [0.64, 0.85] | 0.70 [0.59, 0.81] |
| heuristic-h1 | heuristic_easy | End-to-End | NEITHER | 63 | 0.24 [0.14, 0.35] | – | – |
| heuristic-h1 | heuristic_easy | Detection-Controlled | ALL | 270 | 0.75 [0.69, 0.80] | 0.79 [0.71, 0.87] | 0.76 [0.68, 0.84] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 0.96 [0.89, 1.00] | 0.83 [0.71, 0.94] | 0.83 [0.71, 0.94] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 0.92 [0.84, 1.00] | 0.87 [0.74, 0.97] | 0.87 [0.74, 0.97] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.88 [0.80, 0.94] | 0.75 [0.64, 0.85] | 0.70 [0.59, 0.81] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | NEITHER | 63 | 0.24 [0.14, 0.35] | – | – |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.90 [0.84, 0.95] | 0.79 [0.71, 0.87] | 0.76 [0.67, 0.85] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 0.96 [0.89, 1.00] | 0.83 [0.71, 0.94] | 0.83 [0.71, 0.94] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 0.92 [0.83, 1.00] | 0.87 [0.75, 0.97] | 0.87 [0.75, 0.97] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.88 [0.80, 0.94] | 0.75 [0.63, 0.85] | 0.70 [0.58, 0.80] |
| heuristic-h1p | all | End-to-End | ALL | 468 | 0.63 [0.57, 0.69] | 0.67 [0.58, 0.76] | 0.48 [0.41, 0.56] |
| heuristic-h1p | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.44 [0.32, 0.57] | – | – |
| heuristic-h1p | all | End-to-End | INFORMATION_ONLY | 78 | 0.60 [0.49, 0.71] | 0.78 [0.69, 0.87] | 0.51 [0.40, 0.63] |
| heuristic-h1p | all | End-to-End | COMPUTATION_ONLY | 84 | 0.54 [0.42, 0.64] | 0.68 [0.58, 0.78] | 0.40 [0.30, 0.51] |
| heuristic-h1p | all | End-to-End | BOTH | 180 | 0.62 [0.50, 0.73] | 0.62 [0.50, 0.73] | 0.51 [0.39, 0.61] |
| heuristic-h1p | all | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | all | Detection-Controlled | ALL | 405 | 0.66 [0.59, 0.73] | 0.67 [0.59, 0.75] | 0.48 [0.40, 0.56] |
| heuristic-h1p | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.60 [0.50, 0.71] | 0.78 [0.68, 0.87] | 0.51 [0.41, 0.62] |
| heuristic-h1p | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.54 [0.43, 0.65] | 0.68 [0.57, 0.77] | 0.40 [0.30, 0.52] |
| heuristic-h1p | all | Detection-Controlled | BOTH | 180 | 0.62 [0.51, 0.72] | 0.62 [0.51, 0.72] | 0.51 [0.40, 0.61] |
| heuristic-h1p | all | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | all | Diagnosis-Controlled | ALL | 342 | 0.59 [0.51, 0.67] | 0.67 [0.58, 0.75] | 0.48 [0.41, 0.56] |
| heuristic-h1p | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.60 [0.50, 0.71] | 0.78 [0.69, 0.87] | 0.51 [0.41, 0.62] |
| heuristic-h1p | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.54 [0.43, 0.65] | 0.68 [0.58, 0.78] | 0.40 [0.29, 0.52] |
| heuristic-h1p | all | Diagnosis-Controlled | BOTH | 180 | 0.62 [0.50, 0.73] | 0.62 [0.50, 0.73] | 0.51 [0.40, 0.61] |
| heuristic-h1p | heuristic_hard | End-to-End | ALL | 168 | 0.23 [0.13, 0.32] | 0.47 [0.35, 0.59] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1p | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.23 [0.07, 0.40] | 0.68 [0.50, 0.83] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.24 [0.12, 0.38] | 0.51 [0.36, 0.66] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | BOTH | 59 | 0.34 [0.18, 0.51] | 0.34 [0.18, 0.51] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | ALL | 135 | 0.28 [0.17, 0.40] | 0.47 [0.35, 0.60] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.23 [0.07, 0.40] | 0.68 [0.50, 0.84] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.24 [0.12, 0.40] | 0.51 [0.36, 0.67] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.34 [0.18, 0.52] | 0.34 [0.18, 0.52] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.28 [0.18, 0.39] | 0.47 [0.36, 0.59] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.23 [0.07, 0.40] | 0.68 [0.50, 0.84] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.24 [0.11, 0.39] | 0.51 [0.36, 0.67] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.34 [0.17, 0.51] | 0.34 [0.17, 0.51] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_easy | End-to-End | ALL | 300 | 0.85 [0.80, 0.91] | 0.80 [0.70, 0.88] | 0.80 [0.70, 0.88] |
| heuristic-h1p | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 0.93 [0.83, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] |
| heuristic-h1p | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.87 [0.76, 0.97] | 0.87 [0.76, 0.97] | 0.87 [0.76, 0.97] |
| heuristic-h1p | heuristic_easy | End-to-End | BOTH | 121 | 0.75 [0.64, 0.85] | 0.75 [0.64, 0.85] | 0.75 [0.64, 0.85] |
| heuristic-h1p | heuristic_easy | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | Detection-Controlled | ALL | 270 | 0.84 [0.77, 0.90] | 0.80 [0.70, 0.88] | 0.80 [0.70, 0.88] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 0.87 [0.76, 0.97] | 0.87 [0.76, 0.97] | 0.87 [0.76, 0.97] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.75 [0.64, 0.86] | 0.75 [0.64, 0.86] | 0.75 [0.64, 0.86] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.80 [0.71, 0.88] | 0.80 [0.71, 0.88] | 0.80 [0.71, 0.88] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] | 0.85 [0.74, 0.94] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 0.87 [0.75, 0.97] | 0.87 [0.75, 0.97] | 0.87 [0.75, 0.97] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.75 [0.64, 0.85] | 0.75 [0.64, 0.85] | 0.75 [0.64, 0.85] |
| heuristic-h1pp | all | End-to-End | ALL | 468 | 0.76 [0.72, 0.80] | 0.88 [0.84, 0.91] | 0.61 [0.54, 0.67] |
| heuristic-h1pp | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.48 [0.35, 0.60] | – | – |
| heuristic-h1pp | all | End-to-End | INFORMATION_ONLY | 78 | 0.72 [0.61, 0.81] | 0.90 [0.83, 0.96] | 0.60 [0.49, 0.71] |
| heuristic-h1pp | all | End-to-End | COMPUTATION_ONLY | 84 | 0.63 [0.52, 0.74] | 0.89 [0.82, 0.96] | 0.46 [0.35, 0.58] |
| heuristic-h1pp | all | End-to-End | BOTH | 180 | 0.86 [0.80, 0.92] | 0.86 [0.80, 0.92] | 0.67 [0.59, 0.76] |
| heuristic-h1pp | all | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | all | Detection-Controlled | ALL | 405 | 0.81 [0.77, 0.85] | 0.88 [0.84, 0.91] | 0.61 [0.54, 0.67] |
| heuristic-h1pp | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.72 [0.62, 0.82] | 0.90 [0.83, 0.96] | 0.60 [0.49, 0.71] |
| heuristic-h1pp | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.63 [0.52, 0.75] | 0.89 [0.82, 0.96] | 0.46 [0.35, 0.58] |
| heuristic-h1pp | all | Detection-Controlled | BOTH | 180 | 0.86 [0.80, 0.92] | 0.86 [0.80, 0.92] | 0.67 [0.59, 0.76] |
| heuristic-h1pp | all | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | all | Diagnosis-Controlled | ALL | 342 | 0.77 [0.73, 0.82] | 0.88 [0.84, 0.91] | 0.61 [0.54, 0.67] |
| heuristic-h1pp | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.72 [0.62, 0.82] | 0.90 [0.83, 0.96] | 0.60 [0.49, 0.71] |
| heuristic-h1pp | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.63 [0.52, 0.74] | 0.89 [0.82, 0.95] | 0.46 [0.35, 0.58] |
| heuristic-h1pp | all | Diagnosis-Controlled | BOTH | 180 | 0.86 [0.80, 0.91] | 0.86 [0.80, 0.91] | 0.67 [0.58, 0.76] |
| heuristic-h1pp | heuristic_hard | End-to-End | ALL | 168 | 0.34 [0.26, 0.42] | 0.69 [0.60, 0.77] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1pp | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.29 [0.13, 0.47] | 0.74 [0.59, 0.89] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.31 [0.17, 0.46] | 0.80 [0.67, 0.92] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | BOTH | 59 | 0.58 [0.44, 0.71] | 0.58 [0.44, 0.71] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | ALL | 135 | 0.42 [0.33, 0.52] | 0.69 [0.60, 0.77] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.29 [0.13, 0.48] | 0.74 [0.59, 0.88] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.31 [0.17, 0.46] | 0.80 [0.67, 0.91] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.58 [0.45, 0.71] | 0.58 [0.45, 0.71] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.42 [0.32, 0.52] | 0.69 [0.60, 0.77] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.29 [0.12, 0.48] | 0.74 [0.58, 0.90] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.31 [0.17, 0.47] | 0.80 [0.67, 0.93] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.58 [0.44, 0.70] | 0.58 [0.44, 0.70] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | ALL | 300 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | BOTH | 121 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | ALL | 270 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | BOTH | 121 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| policy-always_answer | all | End-to-End | ALL | 468 | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | ALREADY_SUFFICIENT | 63 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | all | End-to-End | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | all | Detection-Controlled | ALL | 405 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | all | Diagnosis-Controlled | ALL | 342 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | ALL | 168 | 0.20 [0.15, 0.24] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | ALL | 135 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | ALL | 300 | 0.10 [0.08, 0.12] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | heuristic_easy | Detection-Controlled | ALL | 270 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | ALL | 468 | 0.17 [0.15, 0.18] | 0.23 [0.21, 0.25] | 0.01 [0.00, 0.02] |
| policy-always_ask | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | End-to-End | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.10] |
| policy-always_ask | all | End-to-End | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | Detection-Controlled | ALL | 405 | 0.19 [0.18, 0.21] | 0.23 [0.21, 0.25] | 0.01 [0.00, 0.02] |
| policy-always_ask | all | Detection-Controlled | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.10] |
| policy-always_ask | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Detection-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | Diagnosis-Controlled | ALL | 342 | 0.23 [0.21, 0.25] | 0.23 [0.21, 0.25] | 0.01 [0.00, 0.02] |
| policy-always_ask | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.10] |
| policy-always_ask | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Diagnosis-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | End-to-End | ALL | 168 | 0.18 [0.14, 0.24] | 0.23 [0.17, 0.29] | 0.01 [0.00, 0.02] |
| policy-always_ask | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.10] |
| policy-always_ask | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | End-to-End | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Detection-Controlled | ALL | 135 | 0.23 [0.17, 0.30] | 0.23 [0.17, 0.30] | 0.01 [0.00, 0.02] |
| policy-always_ask | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.09] |
| policy-always_ask | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.23 [0.17, 0.29] | 0.23 [0.17, 0.29] | 0.01 [0.00, 0.02] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.10] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | ALL | 300 | 0.16 [0.13, 0.18] | 0.23 [0.19, 0.26] | 0.01 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.13] |
| policy-always_ask | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | Detection-Controlled | ALL | 270 | 0.17 [0.14, 0.20] | 0.23 [0.19, 0.27] | 0.01 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.13] |
| policy-always_ask | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.23 [0.19, 0.27] | 0.23 [0.19, 0.27] | 0.01 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.13] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | ALL | 468 | 0.18 [0.16, 0.20] | 0.25 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | End-to-End | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | COMPUTATION_ONLY | 84 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.01, 0.10] |
| policy-always_compute | all | End-to-End | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | Detection-Controlled | ALL | 405 | 0.21 [0.18, 0.23] | 0.25 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.01, 0.10] |
| policy-always_compute | all | Detection-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | Diagnosis-Controlled | ALL | 342 | 0.25 [0.22, 0.27] | 0.25 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.01, 0.10] |
| policy-always_compute | all | Diagnosis-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | End-to-End | ALL | 168 | 0.27 [0.21, 0.33] | 0.33 [0.26, 0.41] | 0.01 [0.00, 0.04] |
| policy-always_compute | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.11] |
| policy-always_compute | heuristic_hard | End-to-End | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Detection-Controlled | ALL | 135 | 0.33 [0.26, 0.42] | 0.33 [0.26, 0.42] | 0.01 [0.00, 0.04] |
| policy-always_compute | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.11] |
| policy-always_compute | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.33 [0.26, 0.41] | 0.33 [0.26, 0.41] | 0.01 [0.00, 0.04] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.12] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | ALL | 300 | 0.13 [0.10, 0.16] | 0.19 [0.15, 0.23] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.00, 0.14] |
| policy-always_compute | heuristic_easy | End-to-End | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | Detection-Controlled | ALL | 270 | 0.14 [0.11, 0.18] | 0.19 [0.15, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.00, 0.14] |
| policy-always_compute | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Detection-Controlled | NEITHER | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.19 [0.14, 0.23] | 0.19 [0.14, 0.23] | 0.01 [0.00, 0.03] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.05 [0.00, 0.14] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | ALL | 468 | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | ALREADY_SUFFICIENT | 63 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | all | End-to-End | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | all | Detection-Controlled | ALL | 405 | 0.16 [0.15, 0.16] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | all | Diagnosis-Controlled | ALL | 342 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | INFORMATION_ONLY | 78 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | COMPUTATION_ONLY | 84 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | BOTH | 180 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | ALL | 168 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 33 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | heuristic_hard | End-to-End | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | ALL | 135 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | ALL | 135 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 31 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 45 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | BOTH | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | ALL | 300 | 0.21 [0.20, 0.23] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 30 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | heuristic_easy | End-to-End | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | heuristic_easy | Detection-Controlled | ALL | 270 | 0.23 [0.22, 0.25] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | NEITHER | 63 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | ALL | 207 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 47 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 39 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | BOTH | 121 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Confirmatory tests (Holm-adjusted; see PROTOCOL.md §4)

| Agent / model | Test | p | Holm p |
|---|---|---|---|
| adaption-qwen3.8-27b | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| adaption-qwen3.8-27b | H3_relevance_vs_sufficiency_judgment | 0.00195 | 0.00781 |
| adaption-qwen3.8-27b | H4_INFO_vs_BOTH_DC | 0.5 | 1 |
| adaption-qwen3.8-27b | H4_COMP_vs_BOTH_DC | 0.5 | 1 |
| heuristic-h1 | H2_diagnosis_vs_plan_sufficiency_DC | 0.0154 | 0.0463 |
| heuristic-h1 | H3_relevance_vs_sufficiency_judgment | 0.000189 | 0.000757 |
| heuristic-h1 | H4_INFO_vs_BOTH_DC | 0.0309 | 0.0618 |
| heuristic-h1 | H4_COMP_vs_BOTH_DC | 0.648 | 0.648 |
| heuristic-h1p | H2_diagnosis_vs_plan_sufficiency_DC | 2.98e-08 | 8.94e-08 |
| heuristic-h1p | H3_relevance_vs_sufficiency_judgment | 1.04e-53 | 4.18e-53 |
| heuristic-h1p | H4_INFO_vs_BOTH_DC | 0.118 | 0.237 |
| heuristic-h1p | H4_COMP_vs_BOTH_DC | 1 | 1 |
| heuristic-h1pp | H2_diagnosis_vs_plan_sufficiency_DC | 2.91e-11 | 8.73e-11 |
| heuristic-h1pp | H3_relevance_vs_sufficiency_judgment | 2.41e-35 | 9.63e-35 |
| heuristic-h1pp | H4_INFO_vs_BOTH_DC | 1 | 1 |
| heuristic-h1pp | H4_COMP_vs_BOTH_DC | 0.774 | 1 |
| policy-always_answer | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_answer | H3_relevance_vs_sufficiency_judgment | 1.74e-105 | 6.98e-105 |
| policy-always_answer | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_answer | H4_COMP_vs_BOTH_DC | 1 | 1 |
| policy-always_ask | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_ask | H3_relevance_vs_sufficiency_judgment | 1.07e-55 | 4.28e-55 |
| policy-always_ask | H4_INFO_vs_BOTH_DC | 2.17e-19 | 6.51e-19 |
| policy-always_ask | H4_COMP_vs_BOTH_DC | 1 | 1 |
| policy-always_compute | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_compute | H3_relevance_vs_sufficiency_judgment | 1.47e-54 | 5.88e-54 |
| policy-always_compute | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_compute | H4_COMP_vs_BOTH_DC | 2.17e-19 | 6.51e-19 |
| policy-always_abstain | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_abstain | H3_relevance_vs_sufficiency_judgment | 1.74e-105 | 6.98e-105 |
| policy-always_abstain | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_abstain | H4_COMP_vs_BOTH_DC | 1 | 1 |

## Error taxonomy (first failing stage)

- adaption-qwen3.8-27b: {'end_to_end': {'correct': 453, 'invalid': 10, 'diagnosis': 2, 'minimality': 1, 'detection': 2}, 'detection_controlled': {'correct': 391, 'invalid': 9, 'diagnosis': 4, 'minimality': 1}, 'diagnosis_controlled': {'correct': 338, 'minimality': 2, 'invalid': 2}}
- heuristic-h1: {'end_to_end': {'correct': 218, 'diagnosis': 127, 'minimality': 39, 'sufficiency': 43, 'detection': 35, 'targeting': 6}, 'detection_controlled': {'correct': 190, 'diagnosis': 127, 'sufficiency': 43, 'minimality': 39, 'targeting': 6}, 'diagnosis_controlled': {'sufficiency': 43, 'correct': 175, 'diagnosis': 79, 'minimality': 39, 'targeting': 6}}
- heuristic-h1p: {'end_to_end': {'correct': 256, 'diagnosis': 139, 'detection': 35, 'minimality': 38}, 'detection_controlled': {'diagnosis': 139, 'correct': 228, 'minimality': 38}, 'diagnosis_controlled': {'diagnosis': 139, 'correct': 165, 'minimality': 38}}
- heuristic-h1pp: {'end_to_end': {'correct': 300, 'diagnosis': 78, 'detection': 33, 'minimality': 57}, 'detection_controlled': {'correct': 270, 'minimality': 57, 'diagnosis': 78}, 'diagnosis_controlled': {'correct': 207, 'diagnosis': 78, 'minimality': 57}}
- policy-always_answer: {'end_to_end': {'correct': 63, 'detection': 405}, 'detection_controlled': {'detection': 405}, 'diagnosis_controlled': {'detection': 342}}
- policy-always_ask: {'end_to_end': {'diagnosis': 327, 'minimality': 75, 'detection': 63, 'correct': 3}, 'detection_controlled': {'diagnosis': 327, 'minimality': 75, 'correct': 3}, 'diagnosis_controlled': {'diagnosis': 264, 'minimality': 75, 'correct': 3}}
- policy-always_compute: {'end_to_end': {'diagnosis': 321, 'minimality': 80, 'detection': 63, 'correct': 4}, 'detection_controlled': {'diagnosis': 321, 'minimality': 80, 'correct': 4}, 'diagnosis_controlled': {'diagnosis': 258, 'minimality': 80, 'correct': 4}}
- policy-always_abstain: {'end_to_end': {'diagnosis': 342, 'detection': 63, 'correct': 63}, 'detection_controlled': {'diagnosis': 342, 'correct': 63}, 'diagnosis_controlled': {'diagnosis': 342}}

## Ceiling / floor flags

- adaption-qwen3.8-27b: E1 base decision accuracy ceiling (1.00), E3 detection_controlled class accuracy ceiling (0.97), E3 detection_controlled plan sufficient (resolvable) ceiling (0.99), E3 end_to_end class accuracy ceiling (0.97), E3 end_to_end plan sufficient (resolvable) ceiling (0.98), E5 judgment accuracy, sufficient plans ceiling (1.00), E5 judgment accuracy, relevant-insufficient plans ceiling (0.97), E7 detection_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled BOTH plan sufficient ceiling (0.97), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled BOTH plan sufficient ceiling (1.00), E7 end_to_end INFORMATION_ONLY plan sufficient ceiling (1.00), E7 end_to_end COMPUTATION_ONLY plan sufficient ceiling (0.98), E7 end_to_end BOTH plan sufficient ceiling (0.98)
- heuristic-h1: none
- heuristic-h1p: E5 judgment accuracy, relevant-insufficient plans ceiling (1.00)
- heuristic-h1pp: E5 judgment accuracy, relevant-insufficient plans ceiling (1.00)
- policy-always_answer: E3 detection_controlled class accuracy floor (0.00), E3 detection_controlled plan sufficient (resolvable) floor (0.00), E3 end_to_end class accuracy floor (0.00), E3 end_to_end plan sufficient (resolvable) floor (0.00), E5 judgment accuracy, sufficient plans ceiling (1.00), E5 judgment accuracy, relevant-insufficient plans floor (0.00), E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_ask: E7 detection_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient ceiling (1.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_compute: E5 judgment accuracy, sufficient plans ceiling (0.96), E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_abstain: E3 detection_controlled plan sufficient (resolvable) floor (0.00), E3 end_to_end plan sufficient (resolvable) floor (0.00), E5 judgment accuracy, sufficient plans floor (0.00), E5 judgment accuracy, relevant-insufficient plans ceiling (1.00), E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)

## Usage

- adaption-qwen3.8-27b: 1814 requests, parse errors 0.02, refusals 0.00, truncations 0.02, cost 8.8796 credits; served models {'qwen3.8-27b': 1814}
- heuristic-h1: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1': 1814}
- heuristic-h1p: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1p': 1814}
- heuristic-h1pp: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1pp': 1814}
- policy-always_answer: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_answer': 1814}
- policy-always_ask: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_ask': 1814}
- policy-always_compute: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_compute': 1814}
- policy-always_abstain: 1814 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_abstain': 1814}
