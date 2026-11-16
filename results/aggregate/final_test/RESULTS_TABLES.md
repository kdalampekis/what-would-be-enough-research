# Result tables


### Headline table, held-out test split (63 families)

Columns 2-5: optimal-plan rate on resolvable states, Detection-Controlled, all attempted. Defers: on NEITHER states. Acts: proposes an action on a state that one edit made sufficient (n=169). Test p-values: tables below.

| Model | Native | Structured prompt | EOP | Parser | EOP − native | Defers when nothing helps | Acts on newly sufficient states |
|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.93 | 0.62 | 1.00 | 1.00 | +0.07 [+0.04, +0.10] | 0.89 | 0.20 [0.14, 0.27] |
| qwen3.8-27b | 0.98 | 0.96 | 1.00 | 1.00 | +0.02 [+0.01, +0.04] | 0.87 | 0.00 [0.00, 0.00] |
| deepseek-v4-flash | 0.98 | 0.94 | 1.00 | 1.00 | +0.02 [+0.01, +0.04] | 0.97 | 0.00 [0.00, 0.00] |
| gemma-4-26b +schema | 0.42 | 0.40 | 0.99 | 1.00 | +0.57 [+0.51, +0.62] | 0.00 | 0.72 [0.64, 0.79] |

### Stopping, held-out test split (63 families)

Native answer, all attempted. Defers: empty plan and "defer" when no available action can settle the question. Acts: proposes any action on a state that is already sufficient, from the start or after one edit. Last column: registered test T-OI-1, one-sided, Holm across models.

| Model | Defers on NEITHER (DC) | Acts when sufficient from the start (E2E) | Acts when one edit made it sufficient (E2E) | Above 0.05? (Holm p) |
|---|---|---|---|---|
| qwen3.5-397b | 0.89 [0.81, 0.97] | 0.13 | 0.20 [0.14, 0.27] (n=169) | yes (< 0.001) |
| qwen3.8-27b | 0.87 [0.79, 0.95] | 0.00 | 0.00 [0.00, 0.00] (n=169) | no (1.000) |
| deepseek-v4-flash | 0.97 [0.92, 1.00] | 0.00 | 0.00 [0.00, 0.00] (n=169) | no (1.000) |
| gemma-4-26b +schema | 0.00 [0.00, 0.00] | 0.67 | 0.72 [0.64, 0.79] (n=169) | yes (< 0.001) |

### Main-text conditions, held-out test split, detection-controlled

Optimal-plan rate on resolvable states, all attempted. Intervals for every cell are in the full table below.

| Model | A native | B structured | EOP | P parser | EOP − A | Holm p (one-sided) |
|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.93 | 0.62 | 1.00 | 1.00 | +0.07 [+0.04, +0.10] | < 0.001 |
| qwen3.8-27b | 0.98 | 0.96 | 1.00 | 1.00 | +0.02 [+0.01, +0.04] | 0.005 |
| deepseek-v4-flash | 0.98 | 0.94 | 1.00 | 1.00 | +0.02 [+0.01, +0.04] | 0.004 |
| gemma-4-26b +schema | 0.42 | 0.40 | 0.99 | 1.00 | +0.57 [+0.51, +0.62] | < 0.001 |

### Native planning, held-out test split (63 families)

All attempted. Detection: says correctly whether the state is sufficient (End-to-End). Sufficient and optimal: resolvable states. Defer: empty plan and "defer" on NEITHER states. Acts when sufficient: proposes an action on an ALREADY_SUFFICIENT state.

| Model | Detection (E2E) | Plan sufficient (E2E) | Plan optimal (DC) | Defers on NEITHER (DC) | Acts when sufficient (E2E) |
|---|---|---|---|---|---|
| qwen3.5-397b | 0.97 [0.96, 0.99] | 0.99 [0.99, 1.00] | 0.93 [0.90, 0.96] | 0.89 [0.81, 0.97] | 0.13 [0.05, 0.22] |
| qwen3.8-27b | 0.97 [0.96, 0.99] | 0.98 [0.97, 0.99] | 0.98 [0.97, 1.00] | 0.87 [0.79, 0.95] | 0.00 [0.00, 0.00] |
| deepseek-v4-flash | 0.97 [0.96, 0.99] | 0.97 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.92, 1.00] | 0.00 [0.00, 0.00] |
| gemma-4-26b +schema | 0.90 [0.89, 0.92] | 0.84 [0.79, 0.89] | 0.42 [0.36, 0.48] | 0.00 [0.00, 0.00] | 0.67 [0.56, 0.78] |

### Native planning, development split (72 families)

All attempted. Detection: says correctly whether the state is sufficient (End-to-End). Sufficient and optimal: resolvable states. Defer: empty plan and "defer" on NEITHER states. Acts when sufficient: proposes an action on an ALREADY_SUFFICIENT state.

| Model | Detection (E2E) | Plan sufficient (E2E) | Plan optimal (DC) | Defers on NEITHER (DC) | Acts when sufficient (E2E) |
|---|---|---|---|---|---|
| qwen3.5-397b | 0.99 [0.98, 0.99] | 1.00 [0.99, 1.00] | 0.96 [0.93, 0.98] | 0.81 [0.71, 0.89] | 0.08 [0.03, 0.15] |
| qwen3.8-27b | 0.96 [0.94, 0.98] | 0.97 [0.95, 0.99] | 0.98 [0.96, 0.99] | 0.88 [0.79, 0.94] | 0.00 [0.00, 0.00] |
| deepseek-v4-flash | 0.97 [0.95, 0.98] | 0.96 [0.94, 0.98] | 0.96 [0.94, 0.98] | 0.93 [0.86, 0.99] | 0.01 [0.00, 0.04] |
| gemma-4-26b +schema | 0.89 [0.88, 0.90] | 0.85 [0.80, 0.89] | 0.45 [0.39, 0.51] | 0.00 [0.00, 0.00] | 0.61 [0.49, 0.72] |

### Conditions, held-out test split, detection-controlled

Optimal-plan rate on resolvable states, all attempted, 95% family-clustered bootstrap interval. EOP uses the frozen extraction prompt of each model (v2; gemma +schema: registered v1).

| Model | A native | B structured | Verifier only | EOP | P parser | EOP − A | Holm p (one-sided) |
|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.93 [0.90, 0.96] | 0.62 [0.57, 0.68] | 0.69 [0.64, 0.74] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.07 [+0.04, +0.10] | < 0.001 |
| qwen3.8-27b | 0.98 [0.97, 1.00] | 0.96 [0.93, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.02 [+0.01, +0.04] | 0.005 |
| deepseek-v4-flash | 0.98 [0.96, 0.99] | 0.94 [0.92, 0.96] | 0.95 [0.93, 0.97] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.02 [+0.01, +0.04] | 0.004 |
| gemma-4-26b +schema | 0.42 [0.36, 0.48] | 0.40 [0.33, 0.48] (text) | 0.41 [0.34, 0.49] | 0.99 [0.98, 1.00] (v1) | 1.00 | +0.57 [+0.51, +0.62] | < 0.001 |

### Conditions, held-out test split, end-to-end

Optimal-plan rate on resolvable states, all attempted, 95% family-clustered bootstrap interval. EOP uses the frozen extraction prompt of each model (v2; gemma +schema: registered v1).

| Model | A native | B structured | Verifier only | EOP | P parser | EOP − A | Holm p (one-sided) |
|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.95 [0.93, 0.97] | 0.62 [0.57, 0.68] | 0.69 [0.64, 0.74] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.05 [+0.03, +0.07] |  |
| qwen3.8-27b | 0.98 [0.96, 0.99] | 0.97 [0.95, 0.99] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.02 [+0.01, +0.04] |  |
| deepseek-v4-flash | 0.97 [0.95, 0.99] | 0.92 [0.89, 0.95] | 0.94 [0.90, 0.96] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.03 [+0.01, +0.05] |  |
| gemma-4-26b +schema | 0.39 [0.33, 0.46] | 0.46 [0.38, 0.54] (text) | 0.46 [0.39, 0.54] | 0.99 [0.98, 1.00] (v1) | 1.00 | +0.59 [+0.53, +0.65] |  |

### Conditions, development split, detection-controlled

Optimal-plan rate on resolvable states, all attempted, 95% family-clustered bootstrap interval. EOP uses the frozen extraction prompt of each model (v2; gemma +schema: registered v1).

| Model | A native | B structured | Verifier only | EOP | P parser | EOP − A | Holm p (one-sided) |
|---|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.96 [0.93, 0.98] | 0.68 [0.62, 0.73] | 0.74 [0.69, 0.78] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.04 [+0.02, +0.07] | n/a |
| qwen3.8-27b | 0.98 [0.96, 0.99] | 0.98 [0.96, 1.00] | 0.99 [0.98, 1.00] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.02 [+0.01, +0.04] | n/a |
| deepseek-v4-flash | 0.96 [0.94, 0.98] | 0.95 [0.93, 0.97] | 0.97 [0.95, 0.98] | 1.00 [1.00, 1.00] (v2) | 1.00 | +0.04 [+0.02, +0.06] | n/a |
| gemma-4-26b +schema | 0.45 [0.39, 0.51] | 0.39 [0.34, 0.45] (text) | 0.41 [0.35, 0.47] | 0.99 [0.98, 1.00] (v1) | 1.00 | +0.55 [+0.48, +0.61] | n/a |

### EOP as registered and as amended, development split, Detection-Controlled

| Model | A native | Registered EOP (prompt v1) | Amended EOP (prompt v2) | No usable extraction (registered) |
|---|---|---|---|---|
| qwen3.5-397b | 0.96 | 0.69 | 1.00 | 150/473 |
| qwen3.8-27b | 0.98 | 0.65 | 1.00 | 163/473 |
| deepseek-v4-flash | 0.96 | 0.03 | 1.00 | 461/473 |
| gemma-4-26b +schema | 0.45 | 0.99 | n/a | 3/473 |

### Over-intervention on states that one edit made sufficient (End-to-End)

Share of such states on which the model proposes any action. Beside it: the same rate on states that were sufficient from the start. Registered test T-OI-1: rate above 0.05, one-sided, Holm across models.

| Model | Dev: after the edit | Dev: sufficient from the start | Dev: above 0.05? (Holm p) | Test: after the edit | Test: sufficient from the start | Test: above 0.05? (Holm p) |
|---|---|---|---|---|---|---|
| qwen3.5-397b | 0.17 [0.10, 0.26] (n=122) | 0.12 | yes (0.001) | 0.20 [0.14, 0.27] (n=169) | 0.13 | yes (< 0.001) |
| qwen3.8-27b | 0.00 [0.00, 0.00] (n=122) | 0.00 | no (1.000) | 0.00 [0.00, 0.00] (n=169) | 0.00 | no (1.000) |
| deepseek-v4-flash | 0.02 [0.00, 0.04] (n=122) | 0.00 | no (1.000) | 0.00 [0.00, 0.00] (n=169) | 0.00 | no (1.000) |
| gemma-4-26b +schema | 0.68 [0.56, 0.78] (n=122) | 0.64 | yes (< 0.001) | 0.72 [0.64, 0.79] (n=169) | 0.67 | yes (< 0.001) |

### Rewording study (development families, End-to-End, all attempted)

Optimal-plan rate on resolvable states. State exact: the extracted state equals the true state.

**qwen3.5-397b**

| Wording | A native | B structured | EOP | EOP state exact | EOP-N | EOP-N state exact | P parser | EOP − A |
|---|---|---|---|---|---|---|---|---|
| canonical | 0.98 | 0.71 | 1.00 | 1.00 |  |  | 1.00 |  |
| lexical | 1.00 | 0.76 | 0.99 | 0.99 | 1.00 | 1.00 | 0.00 | -0.01 [-0.03, +0.00] |
| syntax | 0.98 | 0.72 | 1.00 | 1.00 | 1.00 | 0.99 | 0.00 | +0.02 [+0.00, +0.05] |
| reorder | 0.97 | 0.74 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.03 [+0.00, +0.08] |
| prose | 0.99 | 0.73 | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | +0.01 [+0.00, +0.03] |

Pooled over the four wordings: EOP − A +0.01 [-0.00, +0.03], Holm p 0.154; EOP-N − A +0.01 [-0.00, +0.03]; EOP − P +0.75 [+0.74, +0.75].

**qwen3.8-27b**

| Wording | A native | B structured | EOP | EOP state exact | EOP-N | EOP-N state exact | P parser | EOP − A |
|---|---|---|---|---|---|---|---|---|
| canonical | 0.96 | 0.98 | 1.00 | 1.00 |  |  | 1.00 |  |
| lexical | 0.98 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | +0.02 [+0.00, +0.05] |
| syntax | 0.98 | 0.97 | 1.00 | 0.99 | 1.00 | 0.99 | 0.00 | +0.02 [+0.00, +0.05] |
| reorder | 0.96 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.04 [+0.00, +0.11] |
| prose | 0.95 | 0.99 | 0.99 | 0.99 | 1.00 | 0.99 | 0.00 | +0.04 [-0.01, +0.09] |

Pooled over the four wordings: EOP − A +0.03 [+0.01, +0.06], Holm p 0.014; EOP-N − A +0.03 [+0.01, +0.06]; EOP − P +0.75 [+0.74, +0.75].

**deepseek-v4-flash**

| Wording | A native | B structured | EOP | EOP state exact | EOP-N | EOP-N state exact | P parser | EOP − A |
|---|---|---|---|---|---|---|---|---|
| canonical | 0.97 | 0.92 | 1.00 | 1.00 |  |  | 1.00 |  |
| lexical | 0.96 | 0.88 | 0.99 | 0.98 | 0.88 | 0.87 | 0.00 | +0.03 [-0.01, +0.07] |
| syntax | 0.98 | 0.98 | 0.81 | 0.81 | 0.97 | 0.98 | 0.00 | -0.17 [-0.25, -0.09] |
| reorder | 0.93 | 0.97 | 1.00 | 1.00 | 0.99 | 0.97 | 1.00 | +0.07 [+0.03, +0.12] |
| prose | 0.98 | 0.90 | 0.92 | 0.92 | 0.88 | 0.88 | 0.00 | -0.06 [-0.12, -0.01] |

Pooled over the four wordings: EOP − A -0.03 [-0.06, +0.00], Holm p 0.984; EOP-N − A -0.03 [-0.07, +0.01]; EOP − P +0.68 [+0.65, +0.71].

**gemma-4-26b +schema**

| Wording | A native | B structured | EOP | EOP state exact | EOP-N | EOP-N state exact | P parser | EOP − A |
|---|---|---|---|---|---|---|---|---|
| canonical | 0.37 | 0.49 | 0.99 | 0.98 |  |  | 1.00 |  |
| lexical | 0.17 | 0.50 | 0.93 | 0.93 | 0.05 | 0.05 | 0.00 | +0.76 [+0.65, +0.87] |
| syntax | 0.35 | 0.37 | 0.05 | 0.07 | 0.05 | 0.04 | 0.00 | -0.30 [-0.44, -0.17] |
| reorder | 0.43 | 0.25 | 0.99 | 0.99 | 0.25 | 0.26 | 1.00 | +0.56 [+0.44, +0.68] |
| prose | 0.20 | 0.50 | 0.61 | 0.46 | 0.26 | 0.19 | 0.00 | +0.42 [+0.29, +0.53] |

Pooled over the four wordings: EOP − A +0.36 [+0.29, +0.43], Holm p < 0.001; EOP-N − A -0.13 [-0.21, -0.05]; EOP − P +0.40 [+0.36, +0.43].

