# Dev decision gate 2 (2026-11-14, 16:45 UTC)

Dev split only; held-out test untouched. Four models: qwen3.5-397b (served `qwen3.5-397b-a17b-nvfp4`),
qwen3.8-27b, gemma-4-26b-a4b-it +schema (forced function-tool schema), deepseek-v4-flash; temperature 0.0,
max_tokens 16000, streaming. Intervals: 95% family-clustered bootstrap. Sources:
`results/aggregate/v3dev/pilot_dev/report.md`, `results/aggregate/t1b_dev/t1b_summary.json`,
`results/aggregate/eop_dev/eop_summary.json`. Raw responses: `results/raw/dev_gate2_*_2026-11-14.tar.gz`.

## 1. EOP: native (A) vs structured prompt (B) vs realistic EOP (C), v3 dev (72 families)

Optimal-plan rate on resolvable states, all attempted (unparsed = failure). Detection-Controlled / End-to-End.

| Model | A native | B S1 prompt | C (registered, extraction v1) | **C′ (Amendment 1, extraction v2)** | D′ (B verified on C′, no search) |
|---|---|---|---|---|---|
| qwen3.5-397b | 0.96 / 0.96 | 0.68 / 0.70 | 0.69 / 0.69 | **1.00 / 1.00** | 0.74 / 0.75 |
| qwen3.8-27b | 0.98 / 0.96 | 0.98 / 0.98 | 0.65 / 0.65 | **1.00 / 1.00** | 0.99 / 0.99 |
| gemma-4-26b +schema | 0.45 / 0.41 | Bt 0.39 / 0.48 (A2) | **0.99 / 0.99** | (C already valid) | Dt 0.41 / 0.52 (A2) |
| deepseek-v4-flash | 0.96 / 0.95 | 0.95 / 0.94 | 0.03 / 0.03 | **1.00 / 1.00** | 0.97 / 0.94 |
| exact-parse + planner (upper bound) | 1.00 | | | | |

Paired differences, Detection-Controlled, optimality [95% CI]: C′−A qwen3.5 +0.04 [0.02, 0.07], qwen3.8
+0.02 [0.01, 0.04], deepseek +0.04 [0.02, 0.06]; gemma C−A +0.55 [0.48, 0.61]. C′−B: qwen3.5 +0.32, qwen3.8
+0.02, deepseek +0.05. C′−D′: qwen3.5 +0.26, qwen3.8 +0.01, deepseek +0.03.

**Registered confirmatory test (C−A, optimality, DC, Holm across models):** supported for gemma (Holm p <
0.001); not supported for qwen3.5, qwen3.8, deepseek (C−A = −0.26, −0.33, −0.94), because the v1 extraction
prompt never showed the required JSON layout and most v1 extractions failed on layout (Amendment 1).
C′−A is an amended secondary analysis, not the registered confirmatory result.

Correct stopping (empty plan and correct answer on ALREADY_SUFFICIENT; defer on NEITHER), End-to-End: A
qwen3.5 0.96, qwen3.8 0.93, gemma 0.51, deepseek 0.97 → C′/C 1.00, 1.00, 0.99, 1.00. Unnecessary-action
rate: A 0.01–0.04 (strong), 0.43 (gemma) → C/C′ 0.00. Regret (parsed): C′ 0.00 for all.

Parsed-only (sensitivity): every parsed C′ plan is optimal (1.00); parsed registered C is 0.98 (qwen3.8) to 1.00; B parsed-only
qwen3.5 0.91–0.93, gemma Bt 0.89–0.91; A parsed-only 0.96–0.99 (strong), 0.41–0.45 (gemma).

**Extraction validity:** C′ extractions were valid and **exactly matched the visible formal state
(variables and kinds, known values, actions with costs and reveals, logically equivalent rule set;
`src/msep/eval/extraction_match.py`) in 545/545 cases for each of qwen3.5, qwen3.8 and deepseek**; v1
extractions were invalid in 171/545 (qwen3.5), 191/545 (qwen3.8), 533/545 (deepseek), mostly through JSON
layout; gemma +schema 3/545 invalid, and 523/545 exactly equal to the visible state (14 with wrong
variables and rules, 5 with wrong actions), so some of its optimal plans come from inexact states.

**Efficiency (per item, v3 dev):** C′ is one extraction call per state (shared across modes) plus ~0.3 ms
of planning. Output tokens / cost per call: qwen3.5 A 7,737 / 0.029 vs C′ 3,235 / 0.013; qwen3.8 4,891 /
0.0062 vs 1,134 / 0.0015; deepseek 3,250 / 0.0005 vs 922 / 0.0002; gemma A 229 / 0.0003 vs C 492 / 0.0004
(credits).

**Format artefacts to report (not reasoning):** B for qwen3.5 lost 252/1,018 answers to JSON parsing
(the S1 prompt allows reasoning before the JSON; in 249 of the 252 that reasoning contains braces, which break the answer extractor);
gemma +schema answered every S1 prompt as message text without the forced call (Amendment 2, Bt/Dt).

## 2. Over-intervention regime (T1B, prospectively registered, 42 new dev families)

| Model | O1 over-intervention after the edit | native ALREADY_SUFFICIENT | diff | T-OI-1 (>0.05) | T-OI-2 (edit-specific) |
|---|---|---|---|---|---|
| qwen3.5-397b | 0.172 [0.099, 0.256] | 0.119 | +0.053 [−0.050, 0.153] | **supported** (Holm p 0.001) | not supported |
| qwen3.8-27b | 0.000 | 0.000 | 0 | not supported | not supported |
| gemma +schema | 0.680 [0.561, 0.780] | 0.643 | +0.037 [−0.122, 0.197] | **supported** (Holm p < 0.001) | not supported |
| deepseek-v4-flash | 0.016 [0.000, 0.041] | 0.000 | +0.016 | not supported | not supported |

qwen3.5's extra actions are computations (O4 0.172 vs information O5 0.016); it never says "sufficient"
and then acts (O3 = 0): a failure to recognise sufficiency. On T1B, EOP stopping: qwen3.5 A 0.86 → C′ 1.00;
gemma A 0.26 → C 0.99; T1B pair joint accuracy qwen3.5 0.86 → 1.00, gemma 0.28 → 0.99.

## 3. Controlled v3 evaluation (E1–E9, 72 dev families) and H1–H6 (dev, descriptive)

Strong models (qwen3.5 / qwen3.8 / deepseek): E1 1.00; E2 detection 0.99 / 0.96 / 0.97; plan sufficiency
1.00 / 0.97–1.00 / 0.96–0.99 across modes; E4 exact match (DxC) 0.98; E6 optimal given sufficient (DC)
0.96–0.98; E7 BOTH 0.97–1.00; E5 pairs both correct 0.98–0.99; **E8 correct defer on NEITHER (DC) 0.81
[0.71, 0.89] / 0.88 / 0.93**. gemma: E1 0.57, E4 0.44, E6 0.51, E8 0.00. h1++: sufficiency 0.85, E6 0.69.
Mode decomposition (strong): failures in all modes 0.00; diagnosis-attributable 0.01–0.04.

- **H1** (DC > E2E with substantial planning error left): detection costs strong models 0–3 points;
  little planning error remains for them; gemma keeps substantial planning error in every mode.
- **H2** (diagnosis easier than planning): not supported for the strong models (plan sufficiency about
  equal to or above class accuracy, 0.97–0.99; plan sufficient given class correct 0.995–1.00).
- **H3** (sufficiency harder than relevance): ceiling for strong models; gemma's bias is the reverse
  (misjudges sufficient plans, 0.56 vs 0.92).
- **H4** (BOTH a failure regime): not supported (BOTH 0.97–1.00).
- **H5** (minimality and stopping distinct): partly supported: minimality near ceiling, but deferral on
  NEITHER 0.81–0.93 and qwen3.5 over-intervention on already-sufficient states (0.12–0.17).
- **H6** (explicit obligations help): registered C−A supported for gemma only; amended C′ (gemma: C) removes
  nearly all remaining planning, stopping and over-intervention errors (optimal 0.99–1.00; gemma has 3
  invalid extractions of 545, deepseek 1 of 266 on the T1 pilot items).
  Structured prompting alone (B) does not help; verification without search (D′) helps less than full
  planning (C′−D′ > 0).

## 4. What remains

Not done: E10, E11, E12, E13, E14, T3, S4, S5; held-out test evaluation; final paper. P0 next: freeze the
final protocol (HELDOUT_PLAN.md → PREREG_FINAL.md) and run held-out once.

Spend: ledger 200.20 credits (19.43 → 200.20 in this programme, of 500 authorised). The provider's shared
rate limit (~25–30 calls/min) is the time constraint.

## Corrections (2026-11-14, after an independent re-read of the result files)

Changed in place above; the earlier wording is recorded here.

- Structured prompt, qwen3.5: **252**/1,018 unparsed answers, not 225 (225 was the count of one error
  message). 249 of the 252 have a brace group in the reasoning before the final JSON.
- "Every parsed C and C′ plan is optimal": true for C′; parsed registered C is 0.977 for qwen3.8 (n = 265)
  and 0.997 for gemma.
- The 545/545 exact-match statement for C′ was first checked with rule counts. It has been re-checked
  with logical equivalence of the rule sets and holds. gemma's registered C extraction is exact in 523/545.
- "Removes every remaining error" was too strong; now "nearly all", with the counts.
- H2: for deepseek, class accuracy 0.983 against plan sufficiency 0.980; sufficient given class 0.995.
- Not valid on v3, and not to be read from any report: the E5 fields `decoy_selected` and
  `decoy_only_plan` (the code looks for v2 action names; they are 0.00 for every agent).
- `results/aggregate/v3dev/pilot_dev/report.md` prints the dev H2–H4 p values under "Confirmatory tests".
  They are confirmatory on the test split only (PROTOCOL.md §8). On dev they are descriptive; H2 goes in
  the opposite direction for qwen3.5 and gemma.
- `PROTOCOL.md`'s header still says "Not frozen" and lists models that were not run. It is pinned
  unchanged in `data/FREEZE_FINAL.json`, which carries the freeze; the models actually run are in its
  amendment section.
