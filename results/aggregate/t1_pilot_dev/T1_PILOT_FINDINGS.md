# T1 dev pilot — findings at the decision gate (2026-11-13)

Pre-registered in `PREREG_T1.md`, frozen in `data/FREEZE_T1.json` (verified before and after the run).
Full tables: `t1_report.md`, `t1_summary.json` (`experiments/analyze_t1.py`). Dev only; the test split was
not used. Raw responses: `results/raw/t1_pilot_raw_2026-11-13.tar.gz`; logs `results/raw/t1_pilot_*_2026-11-13.log`.

## Run

- 20 dev families (ranks 11–30), 133 pairs (85 direct, 48 indirect), 266 End-to-End items per model.
- All 266 answers per model. Five calls dropped by the server (RemoteProtocolError: 1 qwen3.8, 4 qwen3.5
  in a burst at 23:02 UTC) were retried once with identical settings and succeeded.
- Unparsed (all truncations except gemma): qwen3.5 2, qwen3.8 4, gemma +schema 8 (3 truncated).
- Spend: ledger 10.6908 → 19.4324 = **8.74 credits** of the 12-credit cap (qwen3.5 ≈ 7.3, qwen3.8 ≈ 1.36, gemma ≈ 0.08).

## Primary outcomes (all attempted; 95% family-clustered bootstrap)

| Model | Stratum | Item A | Item B | Joint (P1) | Transition (P2) | Excess vs family perm. (P3) |
|---|---|---|---|---|---|---|
| qwen3.5-397b | all (133) | 0.940 [0.889, 0.978] | 0.880 [0.828, 0.927] | 0.827 [0.757, 0.888] | 0.833 [0.761, 0.895] | −0.037 [−0.064, −0.007] |
| qwen3.5-397b | indirect (48) | 0.938 [0.870, 1.000] | 0.854 [0.737, 0.946] | 0.792 [0.667, 0.902] | 0.759 [0.571, 0.892] | −0.047 [−0.116, 0.009] |
| qwen3.8-27b | all | 0.970 [0.941, 0.993] | 1.000 | 0.970 [0.941, 0.993] | 0.974 [0.945, 1.000] | −0.011 [−0.025, 0.001] |
| qwen3.8-27b | indirect | 0.938 [0.870, 1.000] | 1.000 | 0.938 [0.870, 1.000] | 0.931 [0.826, 1.000] | −0.005 [−0.040, 0.028] |
| gemma-4-26b +schema | all | 0.526 [0.415, 0.642] | 0.376 [0.275, 0.489] | 0.286 [0.175, 0.410] | 0.377 [0.275, 0.487] | +0.076 [0.013, 0.132] |
| gemma-4-26b +schema | indirect | 0.604 [0.489, 0.756] | 0.271 [0.143, 0.417] | 0.146 [0.048, 0.278] | 0.034 [0.000, 0.115] | −0.004 [−0.092, 0.080] |
| h1++ (text heuristic) | indirect | 0.708 | 0.500 | 0.417 | 0.276 | +0.150 |

Parsed-only sensitivity changes no conclusion (qwen3.5 joint 0.840, qwen3.8 1.000, gemma 0.304).

## Pre-registered decision rules

- **Ceiling on T1** (indirect joint lower bound ≥ 0.90): met by no model.
- **Additional capability gap** (indirect joint upper bound < 0.90 and v3 calibration optimality ≥ 0.95):
  qwen3.5-397b upper bound 0.902 — **not met (by 0.002)**; qwen3.8-27b upper bound 1.000 — not met.
  Both are **inconclusive** under the registered rules.
- **Edit-tracking failure beyond difficulty** (indirect excess upper bound < h1++ point estimate 0.150):
  formally met by qwen3.5 (0.009), qwen3.8 (0.028) and gemma (0.080). **This rule is not informative near
  ceiling**: when a model is almost always right, joint and permuted joint are both ≈ 1 and excess ≈ 0 by
  construction. It should not be read as evidence of a failure for qwen3.8. This is a design flaw of the
  registered rule, reported rather than changed.

## Exploratory (not pre-registered): where qwen3.5-397b fails

qwen3.5-397b is worse on B members (one more fact known) than on A members (0.880 vs 0.940). Its errors
(26 of 266 items): **over-intervention when the edit makes the state already sufficient — 10 of 55
into-ALREADY_SUFFICIENT B items** (it still plans an action, e.g. `COMPUTE_i1` after K1's certified
result was added: re-computing a result it already has), redundant plans 9, insufficient 2, other 1,
unparsed 2. On v3 calibration its ALREADY_SUFFICIENT accuracy was 1.00 (n=10), so T1 shows a failure the
v3 items did not. It mirrors the dominant error in Ask, Relax, or Act? (over-intervention when the
available information suffices). qwen3.8-27b makes no B-member error. gemma's largest error class is the
same (30 of 55 into-ALREADY_SUFFICIENT B items), then redundant plans.

This is one pilot on 20 families and was not a registered hypothesis; it needs a registered test on fresh
families before any claim.
