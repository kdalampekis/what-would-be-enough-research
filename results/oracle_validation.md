# Oracle validation (E0)

**Status: PASS** — 228199 checks, 0 failed.

Commit `1d147932a8f014590e171c3ef5eb3d4fdc2f88ab` · Python 3.13.18 · pysat 1.9.dev17 · 145.4 s

No language model was called. Paths compared: brute-force enumeration (formula evaluation, no SAT), SAT/MaxSAT refinement (CNF, CaDiCaL + RC2), SAT obligation extraction + MaxSAT hitting set (obligation planner), and weighted model counting (posterior rule).

## Instances

| Suite | Instances | Classes | Decision rules | Mean vars / actions | Max vars / actions |
|---|---|---|---|---|---|
| random_small | 10000 | ALREADY_SUFFICIENT 4192, AMBIGUOUS 92, BOTH 644, COMPUTATION_ONLY 697, INFORMATION_ONLY 1687, NEITHER 2688 | logical_entailment 7493, posterior_threshold 2507 | 5.0 / 3.3 | 8 / 7 |
| random_medium | 2000 | ALREADY_SUFFICIENT 869, AMBIGUOUS 11, BOTH 143, COMPUTATION_ONLY 126, INFORMATION_ONLY 333, NEITHER 518 | logical_entailment 1576, posterior_threshold 424 | 6.5 / 4.5 | 10 / 9 |

Families: 200 families, 2200 instances (mean 1.00 base samples per accepted family).

| Sibling type | Instances |
|---|---|
| ALREADY_SUFFICIENT | 200 |
| INFORMATION_ONLY | 200 |
| COMPUTATION_ONLY | 200 |
| BOTH | 200 |
| NEITHER | 200 |
| RELEVANT_INSUFFICIENT_INFORMATION | 200 |
| RELEVANT_INSUFFICIENT_COMPUTATION | 200 |
| SUFFICIENT_NON_MINIMAL | 200 |
| MULTIPLE_PLANS_DIFFERENT_COSTS | 200 |
| PREMATURE_STOP | 200 |
| UNNECESSARY_EXTRA_ACTION | 200 |

Template v3: 100 families, 765 instances.

| Sibling type (v3) | Instances |
|---|---|
| ALREADY_SUFFICIENT | 100 |
| INFORMATION_ONLY | 100 |
| COMPUTATION_ONLY | 100 |
| BOTH | 100 |
| NEITHER | 100 |
| SUFFICIENT_NON_MINIMAL | 61 |
| RELEVANT_INSUFFICIENT_COMPUTATION | 59 |
| PREMATURE_STOP | 78 |
| RELEVANT_INSUFFICIENT_INFORMATION | 67 |

## Checks

| Check | Passed | Failed | Skipped | What it compares |
|---|---|---|---|---|
| `both_every_optimal_plan_mixed` | 1477 | 0 | 0 | BOTH: every optimal plan has an information and a computation action |
| `both_single_resource_insufficient` | 1459 | 0 | 0 | BOTH (both necessary): all information actions alone and all computation actions alone are insufficient |
| `computation_outcome_world_invariant` | 24256 | 0 | 0 | Computation outcomes are identical in every consistent world (no leakage) |
| `family_label_oracle_vs_brute` | 2200 | 0 | 0 | Family instances: stored class equals enumeration |
| `family_plans_oracle_vs_brute` | 2200 | 0 | 0 | Family instances: stored plan labels equal enumeration |
| `family_v3_label_oracle_vs_brute` | 765 | 0 | 0 | Template v3 instances: stored class equals enumeration |
| `family_v3_plans_oracle_vs_brute` | 765 | 0 | 0 | Template v3 instances: stored plan labels equal enumeration |
| `latent_world_exists` | 14965 | 0 | 0 | Some latent world is consistent with the instance |
| `neither_full_plan_insufficient` | 2899 | 0 | 0 | NEITHER (logical): even the full action set is insufficient |
| `neither_no_sufficient_plan` | 607 | 0 | 0 | NEITHER (posterior): no action set is sufficient |
| `no_obligations_iff_sufficient` | 12034 | 0 | 0 | No obligations exactly when the current state is sufficient |
| `obligations_sat_vs_brute` | 12034 | 0 | 0 | Obligation sets (minimal distinguishing variable sets), SAT vs enumeration |
| `optimal_plan_cheapest` | 11813 | 0 | 0 | No sufficient plan is cheaper than an optimal plan |
| `optimal_plan_inclusion_minimal` | 11813 | 0 | 0 | Removing any action from an optimal plan makes it insufficient |
| `optimal_plan_sufficient` | 11813 | 0 | 0 | Every optimal plan is sufficient |
| `plan_analysis_solver_vs_brute` | 12034 | 0 | 0 | SAT/MaxSAT refinement vs enumeration: empty-plan sufficiency, optimal cost, all optimal plans, all inclusion-minimal plans |
| `plan_analysis_wmc_vs_brute` | 2931 | 0 | 0 | Posterior rule: weighted model counting vs enumeration, full plan analysis |
| `planner_neither` | 2899 | 0 | 0 | Obligation planner defers exactly on NEITHER |
| `planner_optimal_cost` | 9135 | 0 | 0 | Obligation planner returns an optimal plan |
| `posterior_tau1_equals_logical` | 12034 | 0 | 0 | Posterior rule with tau = 1 reproduces the logical rule (enumeration) |
| `posteriors_wmc_vs_brute` | 2931 | 0 | 0 | Posterior rule: exact posteriors per uncomputed completion, WMC vs enumeration |
| `random_plan_sufficiency_sat_vs_brute` | 60170 | 0 | 0 | Sufficiency of random plans, SAT vs enumeration |
| `resource_class_solver_vs_brute` | 12034 | 0 | 0 | Resource class, SAT/MaxSAT vs enumeration |
| `resource_class_wmc_vs_brute` | 2931 | 0 | 0 | Posterior rule: resource class, WMC vs enumeration |

Skipped = the SAT enumeration of minimal plans or obligations hit its cap (512); those instances are compared on optimal plans only.

