# Model results: pilot_dev

> `heuristic-*` rows are real deterministic baselines (no language model, text only); `policy-*` rows are fixed visible-only intervention policies (always answer / ask everything / compute everything / abstain). `mock-*` rows are synthetic fixtures.

Split(s): dev · families: 72 · generated from `summary.json` by `msep.eval.report`.

Every number names its mode. End-to-End mixes detection with planning and is never read as a planning failure. Intervals are 95% family-clustered bootstrap.

## Plan sufficiency by mode (resolvable states)

![](figures/plan_sufficiency_by_mode.png)

Two bases, the same in every mode. **All answers:** an unparsed or truncated answer counts as a failure. **Parsed only:** unparsed answers are left out; the number left out is shown as `unparsed/n`. A gap between the two means output-format or truncation failures, not planning failures.

| Agent / model | E2E all | E2E parsed | DC all | DC parsed | DxC all | DxC parsed | unparsed/n (E2E, DC, DxC) |
|---|---|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | 0.96 [0.94, 0.98] | 1.00 [1.00, 1.00] | 0.98 [0.96, 0.99] | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 1.00 [1.00, 1.00] | 15/401, 5/401, 3/401 |
| heuristic-h1 | 0.66 [0.59, 0.72] | 0.66 [0.59, 0.72] | 0.66 [0.59, 0.72] | 0.66 [0.59, 0.72] | 0.66 [0.59, 0.72] | 0.66 [0.59, 0.72] | 0/401, 0/401, 0/401 |
| heuristic-h1p | 0.56 [0.48, 0.64] | 0.56 [0.48, 0.64] | 0.56 [0.49, 0.63] | 0.56 [0.49, 0.63] | 0.56 [0.49, 0.64] | 0.56 [0.49, 0.64] | 0/401, 0/401, 0/401 |
| heuristic-h1pp | 0.85 [0.81, 0.88] | 0.85 [0.81, 0.88] | 0.85 [0.81, 0.88] | 0.85 [0.81, 0.88] | 0.85 [0.81, 0.88] | 0.85 [0.81, 0.88] | 0/401, 0/401, 0/401 |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0/401, 0/401, 0/401 |
| policy-always_ask | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0/401, 0/401, 0/401 |
| policy-always_compute | 0.24 [0.21, 0.27] | 0.24 [0.21, 0.27] | 0.24 [0.22, 0.27] | 0.24 [0.22, 0.27] | 0.24 [0.22, 0.27] | 0.24 [0.22, 0.27] | 0/401, 0/401, 0/401 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0/401, 0/401, 0/401 |

## Diagnosis vs planning (H2), Detection-Controlled

| Agent / model | Class correct | Plan sufficient | Plan sufficient given class correct | McNemar p |
|---|---|---|---|---|
| adaption-deepseek-v4-flash | 0.98 [0.97, 1.00] | 0.98 [0.96, 0.99] | 0.99 [0.99, 1.00] | 1 |
| heuristic-h1 | 0.78 [0.73, 0.83] | 0.66 [0.59, 0.72] | 0.75 [0.69, 0.81] | 2.35e-06 |
| heuristic-h1p | 0.51 [0.44, 0.58] | 0.56 [0.49, 0.63] | 1.00 [1.00, 1.00] | 4.77e-07 |
| heuristic-h1pp | 0.74 [0.69, 0.78] | 0.85 [0.81, 0.88] | 1.00 [1.00, 1.00] | 1.14e-13 |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1 |
| policy-always_ask | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 1.00 [1.00, 1.00] | 1 |
| policy-always_compute | 0.24 [0.22, 0.27] | 0.24 [0.22, 0.27] | 1.00 [1.00, 1.00] | 1 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1 |

## E3 Resource diagnosis

| Agent / model | Mode | Accuracy | Macro-F1 | Balanced acc. | Surface-feature baseline (all counts) |
|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | Detection-Controlled | 0.97 [0.96, 0.99] | 0.98 [0.97, 0.99] | 0.97 [0.95, 0.98] | 0.42 |
| adaption-deepseek-v4-flash | End-to-End | 0.96 [0.94, 0.97] | 0.97 [0.96, 0.99] | 0.95 [0.93, 0.98] | 0.42 |
| heuristic-h1 | Detection-Controlled | 0.69 [0.65, 0.74] | 0.62 [0.57, 0.67] | 0.63 [0.59, 0.68] | 0.42 |
| heuristic-h1 | End-to-End | 0.69 [0.64, 0.74] | 0.62 [0.56, 0.67] | 0.63 [0.58, 0.68] | 0.42 |
| heuristic-h1p | Detection-Controlled | 0.58 [0.52, 0.64] | 0.60 [0.54, 0.65] | 0.62 [0.57, 0.67] | 0.42 |
| heuristic-h1p | End-to-End | 0.58 [0.52, 0.64] | 0.60 [0.54, 0.65] | 0.62 [0.57, 0.68] | 0.42 |
| heuristic-h1pp | Detection-Controlled | 0.78 [0.73, 0.81] | 0.77 [0.72, 0.81] | 0.78 [0.74, 0.82] | 0.42 |
| heuristic-h1pp | End-to-End | 0.78 [0.74, 0.82] | 0.77 [0.72, 0.81] | 0.78 [0.74, 0.82] | 0.42 |
| policy-always_answer | Detection-Controlled | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.42 |
| policy-always_answer | End-to-End | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.42 |
| policy-always_ask | Detection-Controlled | 0.22 [0.19, 0.24] | 0.09 [0.08, 0.10] | 0.25 [0.25, 0.25] | 0.42 |
| policy-always_ask | End-to-End | 0.22 [0.19, 0.25] | 0.09 [0.08, 0.10] | 0.25 [0.25, 0.25] | 0.42 |
| policy-always_compute | Detection-Controlled | 0.20 [0.18, 0.22] | 0.08 [0.08, 0.09] | 0.25 [0.25, 0.25] | 0.42 |
| policy-always_compute | End-to-End | 0.20 [0.18, 0.23] | 0.08 [0.08, 0.09] | 0.25 [0.25, 0.25] | 0.42 |
| policy-always_abstain | Detection-Controlled | 0.15 [0.15, 0.16] | 0.07 [0.06, 0.07] | 0.25 [0.25, 0.25] | 0.42 |
| policy-always_abstain | End-to-End | 0.15 [0.15, 0.16] | 0.07 [0.06, 0.07] | 0.25 [0.25, 0.25] | 0.42 |

![](figures/confusion_detection_controlled.png)

## E7 BOTH vs single-resource (Detection-Controlled)

| Agent / model | INFORMATION_ONLY | COMPUTATION_ONLY | BOTH | BOTH plans using one resource |
|---|---|---|---|---|
| adaption-deepseek-v4-flash | 0.99 [0.96, 1.00] | 0.97 [0.93, 1.00] | 0.97 [0.93, 1.00] | 0.01 [0.00, 0.04] |
| heuristic-h1 | 0.79 [0.69, 0.89] | 0.74 [0.62, 0.83] | 0.56 [0.44, 0.67] | 0.24 [0.14, 0.33] |
| heuristic-h1p | 0.64 [0.54, 0.75] | 0.61 [0.50, 0.72] | 0.54 [0.43, 0.65] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | 0.92 [0.85, 0.97] | 0.86 [0.78, 0.93] | 0.81 [0.72, 0.89] | 0.00 [0.00, 0.00] |
| policy-always_answer | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| policy-always_compute | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## E5 Relevance vs sufficiency (judgments)

| Agent / model | Accuracy, sufficient plans | Accuracy, relevant-insufficient plans | Pairs both correct | McNemar p |
|---|---|---|---|---|
| adaption-deepseek-v4-flash | 1.00 [1.00, 1.00] | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 0.0625 |
| heuristic-h1 | 0.69 [0.61, 0.76] | 0.86 [0.82, 0.90] | 0.62 [0.56, 0.69] | 0.000446 |
| heuristic-h1p | 0.35 [0.27, 0.44] | 1.00 [1.00, 1.00] | 0.37 [0.28, 0.46] | 1.38e-76 |
| heuristic-h1pp | 0.54 [0.47, 0.63] | 1.00 [1.00, 1.00] | 0.61 [0.52, 0.69] | 2.19e-47 |
| policy-always_answer | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.55e-120 |
| policy-always_ask | 0.91 [0.87, 0.95] | 0.37 [0.33, 0.41] | 0.33 [0.29, 0.37] | 8e-54 |
| policy-always_compute | 0.90 [0.85, 0.94] | 0.38 [0.34, 0.41] | 0.35 [0.31, 0.38] | 4.02e-55 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.55e-120 |

## E1, E2, E4, E6, E8, E9

| Agent / model | E1 base decision acc. | E2 detection acc. (E2E) | E2 over-answering | E4 exact match (DxC) | E6 optimal given sufficient (DC) | E8 correct defer (DC) | E9 premature stop (DC) | E9 continued after ex-post sufficiency (DC; compare with oracle) |
|---|---|---|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.98] | 0.00 [0.00, 0.00] | 0.98 [0.97, 0.99] | 0.98 [0.97, 0.99] | 0.93 [0.86, 0.99] | 0.00 [0.00, 0.01] | 0.19 [0.13, 0.25] |
| heuristic-h1 | 0.78 [0.68, 0.88] | 0.94 [0.92, 0.95] | 0.00 [0.00, 0.00] | 0.50 [0.43, 0.57] | 0.76 [0.68, 0.84] | 0.22 [0.14, 0.32] | 0.19 [0.14, 0.25] | 0.15 [0.10, 0.22] |
| heuristic-h1p | 0.78 [0.68, 0.88] | 0.94 [0.92, 0.95] | 0.00 [0.00, 0.00] | 0.42 [0.35, 0.49] | 0.75 [0.66, 0.83] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.15 [0.09, 0.21] |
| heuristic-h1pp | 0.78 [0.68, 0.88] | 0.94 [0.93, 0.96] | 0.00 [0.00, 0.00] | 0.59 [0.52, 0.65] | 0.69 [0.62, 0.76] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.29 [0.22, 0.36] |
| policy-always_answer | 0.50 [0.39, 0.61] | 0.13 [0.13, 0.14] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | – | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | 0.50 [0.39, 0.61] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.03] | 0.07 [0.02, 0.13] | 0.00 [0.00, 0.00] | 0.62 [0.55, 0.68] | 0.34 [0.28, 0.41] |
| policy-always_compute | 0.50 [0.39, 0.61] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.03 [0.00, 0.07] | 0.00 [0.00, 0.00] | 0.65 [0.58, 0.70] | 0.30 [0.25, 0.35] |
| policy-always_abstain | 0.50 [0.39, 0.61] | 0.87 [0.86, 0.87] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Mode decomposition (same instances across modes; resolvable states)

An End-to-End failure that disappears in Detection-Controlled is attributed to detection/framing; a Detection-Controlled failure that disappears in Diagnosis-Controlled to diagnosis; only failures in all three modes are planning failures. Only instances whose answers parsed in all three modes are used; the number excluded is in the last column.

| Agent / model | e2e_success | e2e_fail_detection_wrong | e2e_fail_but_dc_success | dc_fail_but_dxc_success (diagnosis-attributable) | fail_in_all_modes (planning) | excluded (unparsed in some mode) |
|---|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 23 |
| heuristic-h1 | 0.58 [0.52, 0.65] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.07 [0.04, 0.10] | 0.34 [0.28, 0.41] | 0 |
| heuristic-h1p | 0.51 [0.43, 0.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.05 [0.03, 0.08] | 0.44 [0.36, 0.52] | 0 |
| heuristic-h1pp | 0.74 [0.69, 0.78] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.11 [0.08, 0.14] | 0.15 [0.12, 0.19] | 0 |
| policy-always_answer | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0 |
| policy-always_ask | 0.26 [0.23, 0.29] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.74 [0.71, 0.77] | 0 |
| policy-always_compute | 0.24 [0.22, 0.27] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.76 [0.73, 0.78] | 0 |
| policy-always_abstain | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0 |

## Instruction compliance and hierarchical metrics

| Agent / model | DC: claims sufficient (contradicts prompt) | DxC: class differs from given | A_D | A_G | A_P (DC) | A_P' (DxC) | A_S | A_E2E |
|---|---|---|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.97 [0.95, 0.98] | 0.97 [0.96, 0.99] | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 0.99 [0.98, 1.00] | 0.95 [0.94, 0.97] |
| heuristic-h1 | 0.00 [0.00, 0.00] | 0.22 [0.17, 0.27] | 0.94 [0.92, 0.95] | 0.69 [0.65, 0.74] | 0.64 [0.58, 0.71] | 0.50 [0.43, 0.57] | 0.62 [0.56, 0.69] | 0.47 [0.41, 0.52] |
| heuristic-h1p | 0.00 [0.00, 0.00] | 0.49 [0.42, 0.56] | 0.94 [0.92, 0.95] | 0.58 [0.52, 0.64] | 0.83 [0.75, 0.91] | 0.42 [0.35, 0.49] | 0.37 [0.28, 0.46] | 0.51 [0.46, 0.57] |
| heuristic-h1pp | 0.00 [0.00, 0.00] | 0.26 [0.22, 0.31] | 0.94 [0.93, 0.96] | 0.78 [0.73, 0.81] | 0.80 [0.73, 0.86] | 0.59 [0.52, 0.65] | 0.61 [0.52, 0.69] | 0.63 [0.58, 0.68] |
| policy-always_answer | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | – | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.07 [0.05, 0.08] |
| policy-always_ask | 0.00 [0.00, 0.00] | 0.74 [0.71, 0.77] | 0.87 [0.86, 0.87] | 0.22 [0.19, 0.24] | 0.07 [0.02, 0.13] | 0.02 [0.00, 0.03] | 0.33 [0.29, 0.37] | 0.01 [0.00, 0.02] |
| policy-always_compute | 0.00 [0.00, 0.00] | 0.76 [0.73, 0.78] | 0.87 [0.86, 0.87] | 0.20 [0.18, 0.22] | 0.03 [0.00, 0.07] | 0.01 [0.00, 0.02] | 0.35 [0.31, 0.38] | 0.01 [0.00, 0.01] |
| policy-always_abstain | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.87 [0.86, 0.87] | 0.15 [0.15, 0.16] | – | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.13 [0.13, 0.14] |

## Strata: shallow-heuristic difficulty and template

`heuristic_hard` = instances where the text-only h1pp baseline fails. A model's advantage over shallow reading shows only there.

| Agent / model | Stratum | Instances | DC class correct | DC plan sufficient | DC plan optimal |
|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | heuristic_easy | 347 | 0.97 [0.95, 0.99] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | 198 | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] | 0.94 [0.91, 0.97] |
| adaption-deepseek-v4-flash | v3 | 545 | 0.97 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.96 [0.94, 0.98] |
| heuristic-h1 | heuristic_easy | 347 | 0.75 [0.70, 0.79] | 0.74 [0.65, 0.82] | 0.73 [0.64, 0.81] |
| heuristic-h1 | heuristic_hard | 198 | 0.60 [0.52, 0.68] | 0.54 [0.43, 0.64] | 0.18 [0.09, 0.28] |
| heuristic-h1 | v3 | 545 | 0.69 [0.65, 0.74] | 0.66 [0.59, 0.72] | 0.50 [0.43, 0.57] |
| heuristic-h1p | heuristic_easy | 347 | 0.79 [0.71, 0.85] | 0.72 [0.62, 0.81] | 0.72 [0.62, 0.81] |
| heuristic-h1p | heuristic_hard | 198 | 0.20 [0.12, 0.29] | 0.34 [0.23, 0.44] | 0.00 [0.00, 0.00] |
| heuristic-h1p | v3 | 545 | 0.58 [0.52, 0.64] | 0.56 [0.49, 0.63] | 0.42 [0.35, 0.49] |
| heuristic-h1pp | heuristic_easy | 347 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_hard | 198 | 0.36 [0.28, 0.45] | 0.63 [0.55, 0.70] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | v3 | 545 | 0.78 [0.73, 0.81] | 0.85 [0.81, 0.88] | 0.59 [0.52, 0.66] |
| policy-always_answer | heuristic_easy | 347 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | 198 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | v3 | 545 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | 347 | 0.19 [0.16, 0.23] | 0.25 [0.21, 0.30] | 0.02 [0.00, 0.03] |
| policy-always_ask | heuristic_hard | 198 | 0.27 [0.20, 0.33] | 0.27 [0.20, 0.33] | 0.02 [0.00, 0.05] |
| policy-always_ask | v3 | 545 | 0.22 [0.19, 0.24] | 0.26 [0.23, 0.29] | 0.02 [0.00, 0.03] |
| policy-always_compute | heuristic_easy | 347 | 0.16 [0.13, 0.19] | 0.20 [0.17, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_hard | 198 | 0.29 [0.23, 0.35] | 0.29 [0.23, 0.35] | 0.01 [0.00, 0.02] |
| policy-always_compute | v3 | 545 | 0.20 [0.18, 0.22] | 0.24 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_abstain | heuristic_easy | 347 | 0.23 [0.22, 0.26] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | 198 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | v3 | 545 | 0.15 [0.15, 0.16] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Calibration (stated confidence vs plan sufficiency)

| Agent / model | Mode | n | Brier | ECE |
|---|---|---|---|---|
| adaption-deepseek-v4-flash | End-to-End | 526 | 0.59 | 0.59 |
| adaption-deepseek-v4-flash | Detection-Controlled | 464 | 0.75 | 0.75 |
| adaption-deepseek-v4-flash | Diagnosis-Controlled | 398 | 0.86 | 0.86 |
| heuristic-h1 | End-to-End | 545 | 0.25 | 0.05 |
| heuristic-h1 | Detection-Controlled | 473 | 0.25 | 0.06 |
| heuristic-h1 | Diagnosis-Controlled | 401 | 0.25 | 0.16 |
| heuristic-h1p | End-to-End | 545 | 0.25 | 0.02 |
| heuristic-h1p | Detection-Controlled | 473 | 0.25 | 0.02 |
| heuristic-h1p | Diagnosis-Controlled | 401 | 0.25 | 0.06 |
| heuristic-h1pp | End-to-End | 545 | 0.25 | 0.20 |
| heuristic-h1pp | Detection-Controlled | 473 | 0.25 | 0.22 |
| heuristic-h1pp | Diagnosis-Controlled | 401 | 0.25 | 0.35 |
| policy-always_answer | End-to-End | 545 | 0.25 | 0.37 |
| policy-always_answer | Detection-Controlled | 473 | 0.25 | 0.50 |
| policy-always_answer | Diagnosis-Controlled | 401 | 0.25 | 0.50 |
| policy-always_ask | End-to-End | 545 | 0.25 | 0.31 |
| policy-always_ask | Detection-Controlled | 473 | 0.25 | 0.28 |
| policy-always_ask | Diagnosis-Controlled | 401 | 0.25 | 0.24 |
| policy-always_compute | End-to-End | 545 | 0.25 | 0.32 |
| policy-always_compute | Detection-Controlled | 473 | 0.25 | 0.30 |
| policy-always_compute | Diagnosis-Controlled | 401 | 0.25 | 0.26 |
| policy-always_abstain | End-to-End | 545 | 0.25 | 0.50 |
| policy-always_abstain | Detection-Controlled | 473 | 0.25 | 0.50 |
| policy-always_abstain | Diagnosis-Controlled | 401 | 0.25 | 0.50 |

## Model vs shallow heuristic h1pp (same instances, plan optimal on resolvable states)

| Model | Mode | Model minus h1pp [CI] | McNemar p |
|---|---|---|---|
| adaption-deepseek-v4-flash | Detection-Controlled | 0.38 [0.31, 0.44] | 5.98e-40 |
| adaption-deepseek-v4-flash | Diagnosis-Controlled | 0.39 [0.33, 0.45] | 8.7e-46 |
| adaption-deepseek-v4-flash | End-to-End | 0.36 [0.29, 0.44] | 3.1e-34 |

## Breakdown: stratum x mode x resource class (plan optimal on resolvable states)

Full v3 is primary; heuristic_hard is a pre-registered stress test (it contains no NEITHER items, so compare within class).

| Agent / model | Stratum | Mode | Class | n | Class correct | Plan sufficient | Plan optimal |
|---|---|---|---|---|---|---|---|
| adaption-deepseek-v4-flash | all | End-to-End | ALL | 545 | 0.96 [0.95, 0.98] | 0.96 [0.94, 0.98] | 0.95 [0.93, 0.97] |
| adaption-deepseek-v4-flash | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.99 [0.96, 1.00] | – | – |
| adaption-deepseek-v4-flash | all | End-to-End | INFORMATION_ONLY | 103 | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-deepseek-v4-flash | all | End-to-End | COMPUTATION_ONLY | 96 | 0.95 [0.90, 0.99] | 0.95 [0.90, 0.99] | 0.94 [0.89, 0.98] |
| adaption-deepseek-v4-flash | all | End-to-End | BOTH | 202 | 0.96 [0.94, 0.98] | 0.96 [0.94, 0.98] | 0.94 [0.91, 0.97] |
| adaption-deepseek-v4-flash | all | End-to-End | NEITHER | 72 | 0.93 [0.88, 0.99] | – | – |
| adaption-deepseek-v4-flash | all | Detection-Controlled | ALL | 473 | 0.97 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.96 [0.94, 0.98] |
| adaption-deepseek-v4-flash | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.99 [0.97, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-deepseek-v4-flash | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.97 [0.93, 1.00] | 0.98 [0.95, 1.00] | 0.97 [0.93, 1.00] |
| adaption-deepseek-v4-flash | all | Detection-Controlled | BOTH | 202 | 0.99 [0.96, 1.00] | 0.98 [0.95, 1.00] | 0.95 [0.91, 0.98] |
| adaption-deepseek-v4-flash | all | Detection-Controlled | NEITHER | 72 | 0.93 [0.86, 0.99] | – | – |
| adaption-deepseek-v4-flash | all | Diagnosis-Controlled | ALL | 401 | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 0.98 [0.96, 0.99] |
| adaption-deepseek-v4-flash | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] |
| adaption-deepseek-v4-flash | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.97 [0.93, 1.00] |
| adaption-deepseek-v4-flash | all | Diagnosis-Controlled | BOTH | 202 | 1.00 [0.98, 1.00] | 1.00 [0.98, 1.00] | 0.97 [0.95, 0.99] |
| adaption-deepseek-v4-flash | heuristic_hard | End-to-End | ALL | 198 | 0.97 [0.95, 0.99] | 0.98 [0.95, 0.99] | 0.95 [0.90, 0.98] |
| adaption-deepseek-v4-flash | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.97 [0.91, 1.00] | – | – |
| adaption-deepseek-v4-flash | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.96 [0.90, 1.00] | 0.96 [0.90, 1.00] | 0.94 [0.86, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | End-to-End | BOTH | 74 | 0.99 [0.96, 1.00] | 0.99 [0.96, 1.00] | 0.93 [0.86, 0.99] |
| adaption-deepseek-v4-flash | heuristic_hard | Detection-Controlled | ALL | 166 | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] | 0.94 [0.91, 0.97] |
| adaption-deepseek-v4-flash | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.98 [0.93, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.93, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.99 [0.96, 1.00] | 0.97 [0.93, 1.00] | 0.89 [0.82, 0.96] |
| adaption-deepseek-v4-flash | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.95 [0.91, 0.98] |
| adaption-deepseek-v4-flash | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.98 [0.93, 1.00] | 0.98 [0.93, 1.00] | 0.94 [0.85, 1.00] |
| adaption-deepseek-v4-flash | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.99] |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | ALL | 347 | 0.95 [0.93, 0.97] | 0.95 [0.93, 0.98] | 0.95 [0.93, 0.98] |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 1.00 [1.00, 1.00] | – | – |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 0.94 [0.87, 1.00] | 0.94 [0.87, 1.00] | 0.94 [0.87, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | BOTH | 128 | 0.95 [0.91, 0.98] | 0.95 [0.91, 0.98] | 0.95 [0.91, 0.98] |
| adaption-deepseek-v4-flash | heuristic_easy | End-to-End | NEITHER | 72 | 0.93 [0.88, 0.99] | – | – |
| adaption-deepseek-v4-flash | heuristic_easy | Detection-Controlled | ALL | 307 | 0.97 [0.95, 0.99] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.95, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.96 [0.89, 1.00] | 0.96 [0.89, 1.00] | 0.96 [0.89, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Detection-Controlled | NEITHER | 72 | 0.93 [0.86, 0.99] | – | – |
| adaption-deepseek-v4-flash | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 1.00 [0.99, 1.00] | 1.00 [0.99, 1.00] | 1.00 [0.99, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| adaption-deepseek-v4-flash | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.99 [0.97, 1.00] |
| heuristic-h1 | all | End-to-End | ALL | 545 | 0.67 [0.63, 0.71] | 0.66 [0.59, 0.72] | 0.50 [0.44, 0.57] |
| heuristic-h1 | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.51 [0.40, 0.62] | – | – |
| heuristic-h1 | all | End-to-End | INFORMATION_ONLY | 103 | 0.81 [0.72, 0.89] | 0.74 [0.62, 0.85] | 0.56 [0.45, 0.68] |
| heuristic-h1 | all | End-to-End | COMPUTATION_ONLY | 96 | 0.70 [0.59, 0.80] | 0.73 [0.63, 0.83] | 0.52 [0.41, 0.64] |
| heuristic-h1 | all | End-to-End | BOTH | 202 | 0.80 [0.73, 0.87] | 0.58 [0.49, 0.67] | 0.46 [0.38, 0.54] |
| heuristic-h1 | all | End-to-End | NEITHER | 72 | 0.22 [0.12, 0.32] | – | – |
| heuristic-h1 | all | Detection-Controlled | ALL | 473 | 0.69 [0.65, 0.74] | 0.66 [0.59, 0.72] | 0.50 [0.43, 0.57] |
| heuristic-h1 | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.81 [0.71, 0.89] | 0.74 [0.62, 0.84] | 0.56 [0.45, 0.68] |
| heuristic-h1 | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.70 [0.58, 0.80] | 0.73 [0.62, 0.83] | 0.52 [0.40, 0.65] |
| heuristic-h1 | all | Detection-Controlled | BOTH | 202 | 0.80 [0.73, 0.87] | 0.58 [0.49, 0.66] | 0.46 [0.38, 0.54] |
| heuristic-h1 | all | Detection-Controlled | NEITHER | 72 | 0.22 [0.14, 0.32] | – | – |
| heuristic-h1 | all | Diagnosis-Controlled | ALL | 401 | 0.78 [0.73, 0.83] | 0.66 [0.59, 0.72] | 0.50 [0.43, 0.57] |
| heuristic-h1 | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.81 [0.71, 0.88] | 0.74 [0.62, 0.85] | 0.56 [0.44, 0.68] |
| heuristic-h1 | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.70 [0.59, 0.80] | 0.73 [0.62, 0.82] | 0.52 [0.41, 0.63] |
| heuristic-h1 | all | Diagnosis-Controlled | BOTH | 202 | 0.80 [0.73, 0.87] | 0.58 [0.49, 0.67] | 0.46 [0.38, 0.54] |
| heuristic-h1 | heuristic_hard | End-to-End | ALL | 198 | 0.50 [0.43, 0.57] | 0.54 [0.43, 0.64] | 0.18 [0.10, 0.28] |
| heuristic-h1 | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1 | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.61 [0.44, 0.78] | 0.61 [0.44, 0.78] | 0.20 [0.07, 0.36] |
| heuristic-h1 | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.40 [0.24, 0.56] | 0.60 [0.44, 0.76] | 0.19 [0.07, 0.33] |
| heuristic-h1 | heuristic_hard | End-to-End | BOTH | 74 | 0.72 [0.60, 0.82] | 0.45 [0.30, 0.59] | 0.16 [0.05, 0.29] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | ALL | 166 | 0.60 [0.52, 0.68] | 0.54 [0.43, 0.64] | 0.18 [0.09, 0.28] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.61 [0.44, 0.78] | 0.61 [0.43, 0.79] | 0.20 [0.07, 0.36] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.40 [0.25, 0.56] | 0.60 [0.43, 0.76] | 0.19 [0.08, 0.33] |
| heuristic-h1 | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.72 [0.61, 0.82] | 0.45 [0.30, 0.59] | 0.16 [0.06, 0.29] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.60 [0.51, 0.67] | 0.54 [0.44, 0.64] | 0.18 [0.10, 0.28] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.61 [0.44, 0.77] | 0.61 [0.44, 0.79] | 0.20 [0.07, 0.36] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.40 [0.24, 0.55] | 0.60 [0.44, 0.77] | 0.19 [0.08, 0.33] |
| heuristic-h1 | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.72 [0.60, 0.83] | 0.45 [0.30, 0.60] | 0.16 [0.06, 0.29] |
| heuristic-h1 | heuristic_easy | End-to-End | ALL | 347 | 0.77 [0.72, 0.80] | 0.74 [0.66, 0.82] | 0.73 [0.64, 0.81] |
| heuristic-h1 | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 0.93 [0.82, 1.00] | – | – |
| heuristic-h1 | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.95 [0.88, 1.00] | 0.83 [0.71, 0.93] | 0.83 [0.71, 0.93] |
| heuristic-h1 | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 0.85 [0.75, 0.96] | 0.85 [0.75, 0.96] |
| heuristic-h1 | heuristic_easy | End-to-End | BOTH | 128 | 0.85 [0.76, 0.93] | 0.66 [0.54, 0.76] | 0.63 [0.52, 0.74] |
| heuristic-h1 | heuristic_easy | End-to-End | NEITHER | 72 | 0.22 [0.12, 0.32] | – | – |
| heuristic-h1 | heuristic_easy | Detection-Controlled | ALL | 307 | 0.75 [0.70, 0.79] | 0.74 [0.65, 0.82] | 0.73 [0.64, 0.81] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 0.95 [0.88, 1.00] | 0.83 [0.71, 0.93] | 0.83 [0.71, 0.93] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 0.85 [0.74, 0.96] | 0.85 [0.74, 0.96] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.85 [0.76, 0.93] | 0.66 [0.54, 0.77] | 0.63 [0.52, 0.74] |
| heuristic-h1 | heuristic_easy | Detection-Controlled | NEITHER | 72 | 0.22 [0.14, 0.32] | – | – |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.91 [0.85, 0.95] | 0.74 [0.66, 0.81] | 0.73 [0.65, 0.80] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 0.95 [0.89, 1.00] | 0.83 [0.72, 0.92] | 0.83 [0.72, 0.92] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 0.85 [0.74, 0.96] | 0.85 [0.74, 0.96] |
| heuristic-h1 | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.85 [0.77, 0.92] | 0.66 [0.55, 0.76] | 0.63 [0.53, 0.74] |
| heuristic-h1p | all | End-to-End | ALL | 545 | 0.57 [0.52, 0.63] | 0.56 [0.48, 0.64] | 0.42 [0.35, 0.49] |
| heuristic-h1p | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.51 [0.39, 0.62] | – | – |
| heuristic-h1p | all | End-to-End | INFORMATION_ONLY | 103 | 0.50 [0.38, 0.61] | 0.59 [0.48, 0.70] | 0.44 [0.33, 0.55] |
| heuristic-h1p | all | End-to-End | COMPUTATION_ONLY | 96 | 0.47 [0.37, 0.57] | 0.59 [0.49, 0.69] | 0.40 [0.30, 0.50] |
| heuristic-h1p | all | End-to-End | BOTH | 202 | 0.53 [0.44, 0.62] | 0.53 [0.44, 0.62] | 0.43 [0.34, 0.51] |
| heuristic-h1p | all | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | all | Detection-Controlled | ALL | 473 | 0.58 [0.52, 0.64] | 0.56 [0.49, 0.63] | 0.42 [0.35, 0.49] |
| heuristic-h1p | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.50 [0.38, 0.61] | 0.59 [0.48, 0.70] | 0.44 [0.33, 0.55] |
| heuristic-h1p | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.47 [0.36, 0.57] | 0.59 [0.49, 0.70] | 0.40 [0.29, 0.51] |
| heuristic-h1p | all | Detection-Controlled | BOTH | 202 | 0.53 [0.44, 0.62] | 0.53 [0.44, 0.62] | 0.43 [0.34, 0.50] |
| heuristic-h1p | all | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | all | Diagnosis-Controlled | ALL | 401 | 0.51 [0.44, 0.58] | 0.56 [0.49, 0.64] | 0.42 [0.35, 0.49] |
| heuristic-h1p | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.50 [0.39, 0.61] | 0.59 [0.49, 0.70] | 0.44 [0.33, 0.55] |
| heuristic-h1p | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.47 [0.37, 0.57] | 0.59 [0.49, 0.70] | 0.40 [0.30, 0.51] |
| heuristic-h1p | all | Diagnosis-Controlled | BOTH | 202 | 0.53 [0.44, 0.62] | 0.53 [0.44, 0.62] | 0.43 [0.34, 0.51] |
| heuristic-h1p | heuristic_hard | End-to-End | ALL | 198 | 0.17 [0.10, 0.25] | 0.34 [0.24, 0.45] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1p | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.14 [0.02, 0.27] | 0.36 [0.21, 0.51] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.15 [0.02, 0.28] | 0.40 [0.24, 0.56] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | End-to-End | BOTH | 74 | 0.28 [0.17, 0.42] | 0.28 [0.17, 0.42] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | ALL | 166 | 0.20 [0.12, 0.29] | 0.34 [0.23, 0.44] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.14 [0.02, 0.28] | 0.36 [0.22, 0.53] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.15 [0.02, 0.28] | 0.40 [0.23, 0.56] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.28 [0.16, 0.41] | 0.28 [0.16, 0.41] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.20 [0.12, 0.29] | 0.34 [0.23, 0.44] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.14 [0.04, 0.28] | 0.36 [0.21, 0.52] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.15 [0.02, 0.29] | 0.40 [0.23, 0.56] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.28 [0.16, 0.41] | 0.28 [0.16, 0.41] | 0.00 [0.00, 0.00] |
| heuristic-h1p | heuristic_easy | End-to-End | ALL | 347 | 0.80 [0.74, 0.86] | 0.72 [0.62, 0.81] | 0.72 [0.62, 0.81] |
| heuristic-h1p | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 0.93 [0.82, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.76 [0.64, 0.88] | 0.76 [0.64, 0.88] | 0.76 [0.64, 0.88] |
| heuristic-h1p | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 0.79 [0.66, 0.91] | 0.79 [0.66, 0.91] | 0.79 [0.66, 0.91] |
| heuristic-h1p | heuristic_easy | End-to-End | BOTH | 128 | 0.67 [0.55, 0.77] | 0.67 [0.55, 0.77] | 0.67 [0.55, 0.77] |
| heuristic-h1p | heuristic_easy | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | Detection-Controlled | ALL | 307 | 0.79 [0.71, 0.85] | 0.72 [0.62, 0.81] | 0.72 [0.62, 0.81] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 0.76 [0.64, 0.87] | 0.76 [0.64, 0.87] | 0.76 [0.64, 0.87] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.79 [0.67, 0.91] | 0.79 [0.67, 0.91] | 0.79 [0.67, 0.91] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.67 [0.56, 0.78] | 0.67 [0.56, 0.78] | 0.67 [0.56, 0.78] |
| heuristic-h1p | heuristic_easy | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.72 [0.62, 0.81] | 0.72 [0.62, 0.81] | 0.72 [0.62, 0.81] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 0.76 [0.64, 0.87] | 0.76 [0.64, 0.87] | 0.76 [0.64, 0.87] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.79 [0.67, 0.91] | 0.79 [0.67, 0.91] | 0.79 [0.67, 0.91] |
| heuristic-h1p | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.67 [0.55, 0.78] | 0.67 [0.55, 0.78] | 0.67 [0.55, 0.78] |
| heuristic-h1pp | all | End-to-End | ALL | 545 | 0.75 [0.71, 0.78] | 0.85 [0.81, 0.88] | 0.59 [0.52, 0.65] |
| heuristic-h1pp | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.56 [0.43, 0.67] | – | – |
| heuristic-h1pp | all | End-to-End | INFORMATION_ONLY | 103 | 0.68 [0.59, 0.77] | 0.87 [0.81, 0.94] | 0.57 [0.47, 0.67] |
| heuristic-h1pp | all | End-to-End | COMPUTATION_ONLY | 96 | 0.59 [0.49, 0.70] | 0.84 [0.77, 0.91] | 0.50 [0.39, 0.61] |
| heuristic-h1pp | all | End-to-End | BOTH | 202 | 0.83 [0.78, 0.88] | 0.83 [0.78, 0.88] | 0.63 [0.56, 0.71] |
| heuristic-h1pp | all | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | all | Detection-Controlled | ALL | 473 | 0.78 [0.73, 0.81] | 0.85 [0.81, 0.88] | 0.59 [0.52, 0.66] |
| heuristic-h1pp | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.68 [0.58, 0.77] | 0.87 [0.81, 0.93] | 0.57 [0.47, 0.68] |
| heuristic-h1pp | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.59 [0.49, 0.70] | 0.84 [0.77, 0.91] | 0.50 [0.39, 0.61] |
| heuristic-h1pp | all | Detection-Controlled | BOTH | 202 | 0.83 [0.78, 0.88] | 0.83 [0.78, 0.88] | 0.63 [0.56, 0.71] |
| heuristic-h1pp | all | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | all | Diagnosis-Controlled | ALL | 401 | 0.74 [0.69, 0.78] | 0.85 [0.81, 0.88] | 0.59 [0.52, 0.65] |
| heuristic-h1pp | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.68 [0.58, 0.77] | 0.87 [0.81, 0.93] | 0.57 [0.48, 0.67] |
| heuristic-h1pp | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.59 [0.49, 0.69] | 0.84 [0.76, 0.91] | 0.50 [0.39, 0.61] |
| heuristic-h1pp | all | Diagnosis-Controlled | BOTH | 202 | 0.83 [0.78, 0.89] | 0.83 [0.78, 0.89] | 0.63 [0.56, 0.71] |
| heuristic-h1pp | heuristic_hard | End-to-End | ALL | 198 | 0.30 [0.23, 0.38] | 0.63 [0.55, 0.70] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| heuristic-h1pp | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.25 [0.10, 0.42] | 0.70 [0.56, 0.84] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.19 [0.06, 0.33] | 0.69 [0.55, 0.82] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | End-to-End | BOTH | 74 | 0.54 [0.42, 0.66] | 0.54 [0.42, 0.66] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | ALL | 166 | 0.36 [0.28, 0.45] | 0.63 [0.55, 0.70] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.25 [0.10, 0.41] | 0.70 [0.56, 0.84] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.19 [0.06, 0.32] | 0.69 [0.55, 0.81] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.54 [0.41, 0.66] | 0.54 [0.41, 0.66] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.36 [0.28, 0.45] | 0.63 [0.55, 0.70] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.25 [0.10, 0.43] | 0.70 [0.56, 0.84] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.19 [0.06, 0.31] | 0.69 [0.56, 0.81] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.54 [0.42, 0.65] | 0.54 [0.42, 0.65] | 0.00 [0.00, 0.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | ALL | 347 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | BOTH | 128 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | ALL | 307 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | BOTH | 128 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| heuristic-h1pp | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| policy-always_answer | all | End-to-End | ALL | 545 | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | ALREADY_SUFFICIENT | 72 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | all | End-to-End | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | all | Detection-Controlled | ALL | 473 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | all | Diagnosis-Controlled | ALL | 401 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | all | Diagnosis-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | ALL | 198 | 0.16 [0.12, 0.20] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | End-to-End | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | ALL | 166 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | ALL | 347 | 0.12 [0.09, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 1.00 [1.00, 1.00] | – | – |
| policy-always_answer | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | heuristic_easy | Detection-Controlled | ALL | 307 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_answer | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | ALL | 545 | 0.19 [0.17, 0.21] | 0.26 [0.23, 0.29] | 0.02 [0.00, 0.03] |
| policy-always_ask | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | End-to-End | INFORMATION_ONLY | 103 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.13] |
| policy-always_ask | all | End-to-End | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | Detection-Controlled | ALL | 473 | 0.22 [0.19, 0.24] | 0.26 [0.23, 0.29] | 0.02 [0.00, 0.03] |
| policy-always_ask | all | Detection-Controlled | INFORMATION_ONLY | 103 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.13] |
| policy-always_ask | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Detection-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | all | Diagnosis-Controlled | ALL | 401 | 0.26 [0.23, 0.29] | 0.26 [0.23, 0.29] | 0.02 [0.00, 0.03] |
| policy-always_ask | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.13] |
| policy-always_ask | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | all | Diagnosis-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | End-to-End | ALL | 198 | 0.22 [0.17, 0.27] | 0.27 [0.20, 0.33] | 0.02 [0.00, 0.05] |
| policy-always_ask | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.00, 0.18] |
| policy-always_ask | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | End-to-End | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Detection-Controlled | ALL | 166 | 0.27 [0.20, 0.33] | 0.27 [0.20, 0.33] | 0.02 [0.00, 0.05] |
| policy-always_ask | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.00, 0.18] |
| policy-always_ask | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.27 [0.20, 0.33] | 0.27 [0.20, 0.33] | 0.02 [0.00, 0.05] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.00, 0.19] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | ALL | 347 | 0.17 [0.14, 0.20] | 0.25 [0.21, 0.30] | 0.02 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.14] |
| policy-always_ask | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | Detection-Controlled | ALL | 307 | 0.19 [0.16, 0.23] | 0.25 [0.21, 0.30] | 0.02 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.14] |
| policy-always_ask | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.25 [0.21, 0.29] | 0.25 [0.21, 0.29] | 0.02 [0.00, 0.03] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.07 [0.02, 0.14] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_ask | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | ALL | 545 | 0.18 [0.16, 0.20] | 0.24 [0.21, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | End-to-End | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | COMPUTATION_ONLY | 96 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.07] |
| policy-always_compute | all | End-to-End | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | Detection-Controlled | ALL | 473 | 0.20 [0.18, 0.22] | 0.24 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.07] |
| policy-always_compute | all | Detection-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | all | Diagnosis-Controlled | ALL | 401 | 0.24 [0.22, 0.27] | 0.24 [0.22, 0.27] | 0.01 [0.00, 0.02] |
| policy-always_compute | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.07] |
| policy-always_compute | all | Diagnosis-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | End-to-End | ALL | 198 | 0.24 [0.19, 0.29] | 0.29 [0.23, 0.35] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.02 [0.00, 0.07] |
| policy-always_compute | heuristic_hard | End-to-End | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Detection-Controlled | ALL | 166 | 0.29 [0.23, 0.35] | 0.29 [0.23, 0.35] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.02 [0.00, 0.07] |
| policy-always_compute | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.29 [0.23, 0.35] | 0.29 [0.23, 0.35] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.02 [0.00, 0.07] |
| policy-always_compute | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | ALL | 347 | 0.14 [0.11, 0.16] | 0.20 [0.17, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.11] |
| policy-always_compute | heuristic_easy | End-to-End | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | End-to-End | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | Detection-Controlled | ALL | 307 | 0.16 [0.13, 0.19] | 0.20 [0.17, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.10] |
| policy-always_compute | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Detection-Controlled | NEITHER | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.20 [0.17, 0.24] | 0.20 [0.17, 0.24] | 0.01 [0.00, 0.02] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.10] |
| policy-always_compute | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | ALL | 545 | 0.13 [0.13, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | ALREADY_SUFFICIENT | 72 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | all | End-to-End | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | all | Detection-Controlled | ALL | 473 | 0.15 [0.15, 0.16] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | all | Diagnosis-Controlled | ALL | 401 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | INFORMATION_ONLY | 103 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | COMPUTATION_ONLY | 96 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | all | Diagnosis-Controlled | BOTH | 202 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | ALL | 198 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | ALREADY_SUFFICIENT | 32 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | heuristic_hard | End-to-End | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | End-to-End | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | ALL | 166 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Detection-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | ALL | 166 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | INFORMATION_ONLY | 44 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_hard | Diagnosis-Controlled | BOTH | 74 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | ALL | 347 | 0.21 [0.19, 0.23] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | ALREADY_SUFFICIENT | 40 | 0.00 [0.00, 0.00] | – | – |
| policy-always_abstain | heuristic_easy | End-to-End | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | End-to-End | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | heuristic_easy | Detection-Controlled | ALL | 307 | 0.23 [0.22, 0.26] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Detection-Controlled | NEITHER | 72 | 1.00 [1.00, 1.00] | – | – |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | ALL | 235 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | INFORMATION_ONLY | 59 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | COMPUTATION_ONLY | 48 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| policy-always_abstain | heuristic_easy | Diagnosis-Controlled | BOTH | 128 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

## Confirmatory tests (Holm-adjusted; see PROTOCOL.md §4)

| Agent / model | Test | p | Holm p |
|---|---|---|---|
| adaption-deepseek-v4-flash | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| adaption-deepseek-v4-flash | H3_relevance_vs_sufficiency_judgment | 0.0625 | 0.25 |
| adaption-deepseek-v4-flash | H4_INFO_vs_BOTH_DC | 1 | 1 |
| adaption-deepseek-v4-flash | H4_COMP_vs_BOTH_DC | 1 | 1 |
| heuristic-h1 | H2_diagnosis_vs_plan_sufficiency_DC | 2.35e-06 | 9.41e-06 |
| heuristic-h1 | H3_relevance_vs_sufficiency_judgment | 0.000446 | 0.00134 |
| heuristic-h1 | H4_INFO_vs_BOTH_DC | 0.00232 | 0.00463 |
| heuristic-h1 | H4_COMP_vs_BOTH_DC | 0.0192 | 0.0192 |
| heuristic-h1p | H2_diagnosis_vs_plan_sufficiency_DC | 4.77e-07 | 1.43e-06 |
| heuristic-h1p | H3_relevance_vs_sufficiency_judgment | 1.38e-76 | 5.53e-76 |
| heuristic-h1p | H4_INFO_vs_BOTH_DC | 0.21 | 0.42 |
| heuristic-h1p | H4_COMP_vs_BOTH_DC | 0.405 | 0.42 |
| heuristic-h1pp | H2_diagnosis_vs_plan_sufficiency_DC | 1.14e-13 | 3.41e-13 |
| heuristic-h1pp | H3_relevance_vs_sufficiency_judgment | 2.19e-47 | 8.76e-47 |
| heuristic-h1pp | H4_INFO_vs_BOTH_DC | 0.115 | 0.231 |
| heuristic-h1pp | H4_COMP_vs_BOTH_DC | 0.503 | 0.503 |
| policy-always_answer | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_answer | H3_relevance_vs_sufficiency_judgment | 1.55e-120 | 6.2e-120 |
| policy-always_answer | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_answer | H4_COMP_vs_BOTH_DC | 1 | 1 |
| policy-always_ask | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_ask | H3_relevance_vs_sufficiency_judgment | 8e-54 | 3.2e-53 |
| policy-always_ask | H4_INFO_vs_BOTH_DC | 4.24e-22 | 1.27e-21 |
| policy-always_ask | H4_COMP_vs_BOTH_DC | 1 | 1 |
| policy-always_compute | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_compute | H3_relevance_vs_sufficiency_judgment | 4.02e-55 | 1.61e-54 |
| policy-always_compute | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_compute | H4_COMP_vs_BOTH_DC | 4.24e-22 | 1.27e-21 |
| policy-always_abstain | H2_diagnosis_vs_plan_sufficiency_DC | 1 | 1 |
| policy-always_abstain | H3_relevance_vs_sufficiency_judgment | 1.55e-120 | 6.2e-120 |
| policy-always_abstain | H4_INFO_vs_BOTH_DC | 1 | 1 |
| policy-always_abstain | H4_COMP_vs_BOTH_DC | 1 | 1 |

## Error taxonomy (first failing stage)

- adaption-deepseek-v4-flash: {'end_to_end': {'correct': 519, 'invalid': 19, 'minimality': 5, 'diagnosis': 2}, 'detection_controlled': {'correct': 453, 'invalid': 9, 'minimality': 6, 'sufficiency': 2, 'diagnosis': 3}, 'diagnosis_controlled': {'correct': 391, 'invalid': 3, 'minimality': 7}}
- heuristic-h1: {'end_to_end': {'correct': 254, 'diagnosis': 145, 'sufficiency': 72, 'minimality': 33, 'detection': 35, 'targeting': 6}, 'detection_controlled': {'correct': 217, 'diagnosis': 145, 'targeting': 6, 'sufficiency': 72, 'minimality': 33}, 'diagnosis_controlled': {'correct': 201, 'sufficiency': 72, 'diagnosis': 89, 'minimality': 33, 'targeting': 6}}
- heuristic-h1p: {'end_to_end': {'correct': 278, 'diagnosis': 198, 'minimality': 34, 'detection': 35}, 'detection_controlled': {'diagnosis': 198, 'correct': 241, 'minimality': 34}, 'diagnosis_controlled': {'diagnosis': 198, 'minimality': 34, 'correct': 169}}
- heuristic-h1pp: {'end_to_end': {'correct': 347, 'diagnosis': 106, 'detection': 32, 'minimality': 60}, 'detection_controlled': {'correct': 307, 'diagnosis': 106, 'minimality': 60}, 'diagnosis_controlled': {'minimality': 60, 'correct': 235, 'diagnosis': 106}}
- policy-always_answer: {'end_to_end': {'detection': 473, 'correct': 72}, 'detection_controlled': {'detection': 473}, 'diagnosis_controlled': {'detection': 401}}
- policy-always_ask: {'end_to_end': {'diagnosis': 370, 'correct': 7, 'detection': 72, 'minimality': 96}, 'detection_controlled': {'diagnosis': 370, 'minimality': 96, 'correct': 7}, 'diagnosis_controlled': {'diagnosis': 298, 'minimality': 96, 'correct': 7}}
- policy-always_compute: {'end_to_end': {'diagnosis': 377, 'minimality': 93, 'detection': 72, 'correct': 3}, 'detection_controlled': {'diagnosis': 377, 'minimality': 93, 'correct': 3}, 'diagnosis_controlled': {'diagnosis': 305, 'minimality': 93, 'correct': 3}}
- policy-always_abstain: {'end_to_end': {'diagnosis': 401, 'correct': 72, 'detection': 72}, 'detection_controlled': {'diagnosis': 401, 'correct': 72}, 'diagnosis_controlled': {'diagnosis': 401}}

## Ceiling / floor flags

- adaption-deepseek-v4-flash: E1 base decision accuracy ceiling (1.00), E3 detection_controlled class accuracy ceiling (0.97), E3 detection_controlled plan sufficient (resolvable) ceiling (0.98), E3 end_to_end class accuracy ceiling (0.96), E3 end_to_end plan sufficient (resolvable) ceiling (0.96), E5 judgment accuracy, sufficient plans ceiling (1.00), E5 judgment accuracy, relevant-insufficient plans ceiling (0.99), E7 detection_controlled INFORMATION_ONLY plan sufficient ceiling (0.99), E7 detection_controlled COMPUTATION_ONLY plan sufficient ceiling (0.97), E7 detection_controlled BOTH plan sufficient ceiling (0.97), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient ceiling (0.99), E7 diagnosis_controlled BOTH plan sufficient ceiling (0.99), E7 end_to_end INFORMATION_ONLY plan sufficient ceiling (0.99), E7 end_to_end COMPUTATION_ONLY plan sufficient ceiling (0.96), E7 end_to_end BOTH plan sufficient ceiling (0.99)
- heuristic-h1: none
- heuristic-h1p: E5 judgment accuracy, relevant-insufficient plans ceiling (1.00)
- heuristic-h1pp: E5 judgment accuracy, relevant-insufficient plans ceiling (1.00)
- policy-always_answer: E3 detection_controlled class accuracy floor (0.00), E3 detection_controlled plan sufficient (resolvable) floor (0.00), E3 end_to_end class accuracy floor (0.00), E3 end_to_end plan sufficient (resolvable) floor (0.00), E5 judgment accuracy, sufficient plans ceiling (1.00), E5 judgment accuracy, relevant-insufficient plans floor (0.00), E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_ask: E7 detection_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient ceiling (1.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_compute: E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient ceiling (1.00), E7 end_to_end BOTH plan sufficient floor (0.00)
- policy-always_abstain: E3 detection_controlled plan sufficient (resolvable) floor (0.00), E3 end_to_end plan sufficient (resolvable) floor (0.00), E5 judgment accuracy, sufficient plans floor (0.00), E5 judgment accuracy, relevant-insufficient plans ceiling (1.00), E7 detection_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 detection_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 detection_controlled BOTH plan sufficient floor (0.00), E7 diagnosis_controlled INFORMATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled COMPUTATION_ONLY plan sufficient floor (0.00), E7 diagnosis_controlled BOTH plan sufficient floor (0.00), E7 end_to_end INFORMATION_ONLY plan sufficient floor (0.00), E7 end_to_end COMPUTATION_ONLY plan sufficient floor (0.00), E7 end_to_end BOTH plan sufficient floor (0.00)

## Usage

- adaption-deepseek-v4-flash: 2105 requests, parse errors 0.02, refusals 0.00, truncations 0.02, cost 0.9473 credits; served models {'deepseek-v4-flash': 2105}
- heuristic-h1: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1': 2105}
- heuristic-h1p: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1p': 2105}
- heuristic-h1pp: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:h1pp': 2105}
- policy-always_answer: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_answer': 2105}
- policy-always_ask: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_ask': 2105}
- policy-always_compute: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_compute': 2105}
- policy-always_abstain: 2105 requests, parse errors 0.00, refusals 0.00, truncations 0.00, cost $0.0000; served models {'mock:always_abstain': 2105}
