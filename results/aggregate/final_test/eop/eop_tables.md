## v3test: 468 items, 63 families

### detection_controlled — optimal / sufficient (all attempted, resolvable); stop = correct stopping on ALREADY_SUFFICIENT and NEITHER

| model | A native | B structured | EOP | verifier only | P parser | EOP − A (optimal) | EOP − B | EOP − verifier | stop A → EOP | unparsed A / B / EOP |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.93 / 1.00 | 0.62 / 0.69 | 1.00 / 1.00 (C2) | 0.69 / 0.69 (D2) | 1.00 / 1.00 | +0.07 [+0.04, +0.10] | +0.38 [+0.32, +0.43] | +0.31 [+0.26, +0.36] | 0.98 → 1.00 | 2/405 / 119/405 / 0/405 |
| qwen3.8-27b | 0.98 / 0.99 | 0.96 / 0.98 | 1.00 / 1.00 (C2) | 0.98 / 0.98 (D2) | 1.00 / 1.00 | +0.02 [+0.01, +0.04] | +0.04 [+0.01, +0.07] | +0.02 [+0.01, +0.04] | 0.90 → 1.00 | 9/405 / 5/405 / 0/405 |
| gemma-4-26b-a4b-it-schema | 0.42 / 0.88 | 0.40 / 0.43 (Bt) | 0.99 / 0.99 (C) | 0.41 / 0.42 (Dt) | 1.00 / 1.00 | +0.57 [+0.51, +0.62] | +0.58 [+0.51, +0.66] | +0.58 [+0.50, +0.65] | 0.97 → 1.00 | 4/405 / 238/405 / 4/405 |
| deepseek-v4-flash | 0.98 / 0.99 | 0.94 / 0.96 | 1.00 / 1.00 (C2) | 0.95 / 0.96 (D2) | 1.00 / 1.00 | +0.02 [+0.01, +0.04] | +0.06 [+0.04, +0.08] | +0.05 [+0.03, +0.07] | 0.97 → 1.00 | 5/405 / 19/405 / 0/405 |

### end_to_end — optimal / sufficient (all attempted, resolvable); stop = correct stopping on ALREADY_SUFFICIENT and NEITHER

| model | A native | B structured | EOP | verifier only | P parser | EOP − A (optimal) | EOP − B | EOP − verifier | stop A → EOP | unparsed A / B / EOP |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.95 / 0.99 | 0.62 / 0.70 | 1.00 / 1.00 (C2) | 0.69 / 0.70 (D2) | 1.00 / 1.00 | +0.05 [+0.03, +0.07] | +0.38 [+0.33, +0.43] | +0.31 [+0.26, +0.36] | 0.92 → 1.00 | 2/468 / 126/468 / 0/468 |
| qwen3.8-27b | 0.98 / 0.98 | 0.97 / 0.98 | 1.00 / 1.00 (C2) | 0.98 / 0.98 (D2) | 1.00 / 1.00 | +0.02 [+0.01, +0.04] | +0.03 [+0.01, +0.05] | +0.02 [+0.01, +0.04] | 0.95 → 1.00 | 10/468 / 6/468 / 0/468 |
| gemma-4-26b-a4b-it-schema | 0.39 / 0.84 | 0.46 / 0.50 (Bt) | 0.99 / 0.99 (C) | 0.46 / 0.49 (Dt) | 1.00 / 1.00 | +0.59 [+0.53, +0.65] | +0.53 [+0.45, +0.61] | +0.53 [+0.45, +0.61] | 0.55 → 0.98 | 7/468 / 235/468 / 6/468 |
| deepseek-v4-flash | 0.97 / 0.97 | 0.92 / 0.94 | 1.00 / 1.00 (C2) | 0.94 / 0.94 (D2) | 1.00 / 1.00 | +0.03 [+0.01, +0.05] | +0.08 [+0.05, +0.11] | +0.06 [+0.03, +0.10] | 0.97 → 1.00 | 13/468 / 22/468 / 0/468 |

**confirmatory_final_EOP_minus_A_optimal_DC:** qwen3.5-397b: {'comparison': 'C2-A', 'p': 0.0, 'holm_p': 0.0}; qwen3.8-27b: {'comparison': 'C2-A', 'p': 0.0049, 'holm_p': 0.0049}; gemma-4-26b-a4b-it-schema: {'comparison': 'C-A', 'p': 0.0, 'holm_p': 0.0}; deepseek-v4-flash: {'comparison': 'C2-A', 'p': 0.0019, 'holm_p': 0.0038}

Extraction calls and failures: qwen3.5-397b: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 468, 'planner_seconds_mean': None}; qwen3.8-27b: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 468, 'planner_seconds_mean': None}; gemma-4-26b-a4b-it-schema: v2 - | v1 {'extraction_failed': 6, 'planner_seconds_mean': 0.0003}; deepseek-v4-flash: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 468, 'planner_seconds_mean': None}

## t1test: 804 items, 63 families

### end_to_end — optimal / sufficient (all attempted, resolvable); stop = correct stopping on ALREADY_SUFFICIENT and NEITHER

| model | A native | B structured | EOP | verifier only | P parser | EOP − A (optimal) | EOP − B | EOP − verifier | stop A → EOP | unparsed A / B / EOP |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.94 / 1.00 | 0.68 / 0.75 | 1.00 / 1.00 (C2) | 0.74 / 0.75 (D2) | 1.00 / 1.00 | +0.06 [+0.03, +0.09] | +0.32 [+0.27, +0.37] | +0.26 [+0.22, +0.30] | 0.85 → 1.00 | 1/804 / 186/804 / 0/804 |
| qwen3.8-27b | 0.98 / 0.98 | 0.98 / 0.99 | 1.00 / 1.00 (C2) | 0.99 / 0.99 (D2) | 1.00 / 1.00 | +0.02 [+0.01, +0.03] | +0.02 [+0.01, +0.04] | +0.01 [+0.00, +0.02] | 0.96 → 1.00 | 16/804 / 7/804 / 0/804 |
| gemma-4-26b-a4b-it-schema | 0.41 / 0.84 | 0.43 / 0.48 (Bt) | 0.99 / 0.99 (C) | 0.45 / 0.47 (Dt) | 1.00 / 1.00 | +0.58 [+0.53, +0.64] | +0.56 [+0.50, +0.62] | +0.54 [+0.48, +0.60] | 0.29 → 0.99 | 18/804 / 413/804 / 6/804 |
| deepseek-v4-flash | 0.94 / 0.95 | 0.94 / 0.95 | 1.00 / 1.00 (C2) | 0.95 / 0.95 (D2) | 1.00 / 1.00 | +0.06 [+0.04, +0.07] | +0.06 [+0.04, +0.08] | +0.05 [+0.03, +0.07] | 0.97 → 1.00 | 29/804 / 32/804 / 0/804 |

Extraction calls and failures: qwen3.5-397b: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 804, 'planner_seconds_mean': None}; qwen3.8-27b: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 804, 'planner_seconds_mean': None}; gemma-4-26b-a4b-it-schema: v2 - | v1 {'extraction_failed': 6, 'planner_seconds_mean': 0.0003}; deepseek-v4-flash: v2 {'planner_seconds_mean': 0.0003} | v1 {'extraction_missing': 804, 'planner_seconds_mean': None}

T1 pair joint accuracy (both items of a pair correct), End-to-End:

- qwen3.5-397b: A {"joint": {"mean": 0.845771144278607, "lo": 0.7969924812030075, "hi": 0.890818858560794}, "joint_within_permutable": {"mean": 0.8459530026109661, "lo": 0.793450, B {"joint": {"mean": 0.48507462686567165, "lo": 0.4177215189873418, "hi": 0.5523114355231143}, "joint_within_permutable": {"mean": 0.4856396866840731, "lo": 0.416, C {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, D {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, C2 {"joint": {"mean": 1.0, "lo": 1.0, "hi": 1.0}, "joint_within_permutable": {"mean": 1.0, "lo": 1.0, "hi": 1.0}}, D2 {"joint": {"mean": 0.599502487562189, "lo": 0.5433673469387755, "hi": 0.654320987654321}, "joint_within_permutable": {"mean": 0.6057441253263708, "lo": 0.546174
- qwen3.8-27b: A {"joint": {"mean": 0.9477611940298507, "lo": 0.9243902439024391, "hi": 0.9694656488549618}, "joint_within_permutable": {"mean": 0.9530026109660574, "lo": 0.9321, B {"joint": {"mean": 0.9577114427860697, "lo": 0.934010152284264, "hi": 0.9776674937965261}, "joint_within_permutable": {"mean": 0.95822454308094, "lo": 0.9343832, C {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, D {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, C2 {"joint": {"mean": 1.0, "lo": 1.0, "hi": 1.0}, "joint_within_permutable": {"mean": 1.0, "lo": 1.0, "hi": 1.0}}, D2 {"joint": {"mean": 0.972636815920398, "lo": 0.955, "hi": 0.9878640776699029}, "joint_within_permutable": {"mean": 0.9738903394255874, "lo": 0.9552631578947368, 
- gemma-4-26b-a4b-it-schema: A {"joint": {"mean": 0.236318407960199, "lo": 0.1884422110552764, "hi": 0.2857142857142857}, "joint_within_permutable": {"mean": 0.22715404699738903, "lo": 0.1780, B {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, C {"joint": {"mean": 0.9825870646766169, "lo": 0.9658536585365853, "hi": 0.9951573849878934}, "joint_within_permutable": {"mean": 0.9843342036553525, "lo": 0.9670, D {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}
- deepseek-v4-flash: A {"joint": {"mean": 0.9079601990049752, "lo": 0.8808933002481389, "hi": 0.9331683168316832}, "joint_within_permutable": {"mean": 0.9033942558746736, "lo": 0.8743, B {"joint": {"mean": 0.9079601990049752, "lo": 0.8766066838046273, "hi": 0.9356435643564357}, "joint_within_permutable": {"mean": 0.9060052219321149, "lo": 0.8743, C {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, D {"joint": {"mean": 0.0, "lo": 0.0, "hi": 0.0}, "joint_within_permutable": {"mean": 0.0, "lo": 0.0, "hi": 0.0}}, C2 {"joint": {"mean": 1.0, "lo": 1.0, "hi": 1.0}, "joint_within_permutable": {"mean": 1.0, "lo": 1.0, "hi": 1.0}}, D2 {"joint": {"mean": 0.9154228855721394, "lo": 0.8875305623471883, "hi": 0.9414758269720102}, "joint_within_permutable": {"mean": 0.9138381201044387, "lo": 0.8860

