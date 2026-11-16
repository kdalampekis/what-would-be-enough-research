# Oracle and its validation

This document explains how the benchmark's labels are computed and why they can be trusted on the instance sizes used. It answers: what the oracle records for each state, how the SAT, MaxSAT and obligation paths work, what the independent brute-force path does, what the validation run compared and how many checks it made, which other re-verifications cover the frozen datasets, how the mutation tests show that the agreement checks can fail, and what the validation does not show. The counts come from [results/oracle_validation.md](../results/oracle_validation.md), the audit report [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) and the test suite under [tests/](../tests/). No language model is part of the oracle: "No LLM may be used as the authoritative oracle" ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §11). Tier of everything here: no-model reference.

The definitions the oracle implements (sufficiency, classes, obligations) are in [formal_problem.md](formal_problem.md).

## 1. What the oracle records for one state

The front end is `solve` in [src/msep/oracle/minimal_plan.py](../src/msep/oracle/minimal_plan.py). For each formal state it stores:

| Field | Content |
|---|---|
| `current_status` | entailed, contradicted or undetermined |
| `current_sufficient` | whether the empty plan is sufficient |
| `resource_class` | one of the five classes, or AMBIGUOUS (excluded from the benchmark) |
| `optimal_cost`, `optimal_plans` | the minimum cost and every plan that reaches it |
| `minimal_sufficient_plans` | every inclusion-minimal sufficient plan, with cost and composition |
| `necessity` | whether information, or computation, is in every sufficient plan; whether the class is cost-invariant |
| `actions` | for each action: relevant or not, sufficient alone or not, and a category (`optimal`, `dominated`, `relevant_insufficient`, `irrelevant`) |
| `obligations`, `obligation_discharge`, `unresolvable_obligations` | the obligations, the actions that discharge each, and those no action can discharge |
| `why_necessary` | for each optimal plan and each of its actions, the obligations that only this action discharges |

Scoring does not compare a model's plan with the stored plan text. "Every plan is re-checked with the oracle (`is_sufficient`), so scores do not depend on matching the oracle's plan text" ([src/msep/eval/plan_metrics.py](../src/msep/eval/plan_metrics.py)).

## 2. The exact paths

"Three exact paths for the logical rule: brute-force enumeration (used to re-verify every benchmark label); a SAT distinguishing-pair check with weighted MaxSAT refinement, which also enumerates all inclusion-minimal plans; and obligation extraction with a MaxSAT hitting set" ([paper/extended_report.md](../paper/extended_report.md), Appendix D). A fourth path, weighted model counting, covers the posterior rule, which the benchmark does not use.

### 2.1 SAT: the distinguishing-pair encoding

Source: [src/msep/oracle/logic.py](../src/msep/oracle/logic.py), solver CaDiCaL through pysat.

The encoding uses two copies of the variables:

> "copy 1 satisfies C, E, M and q; copy 2 satisfies C, E, M and not q; e_v <-> (v in copy 1 == v in copy 2) for every variable v."

> "A plan revealing the variables R is sufficient (logical rule) iff the encoding is UNSAT under the assumptions {e_v : v in R}: no two assignments that the plan cannot tell apart disagree on q."

The status of a state uses two single-copy satisfiability calls, one with q true and one with q false.

### 2.2 MaxSAT: cheapest plans by counterexample-guided refinement

Source: [src/msep/oracle/solver.py](../src/msep/oracle/solver.py), weighted MaxSAT solver RC2.

"Static MSEP is a 2-level problem: find the cheapest action set such that no distinguishing pair survives it." The loop, as documented in the module:

1. "A weighted MaxSAT solver (RC2) proposes the cheapest action set that satisfies all blocking clauses found so far (a minimum-cost hitting set; soft clauses 'not a' with weight cost(a))."
2. "The pair solver looks for a q-true / q-false pair that the proposed set cannot tell apart."
3. "If one exists, the actions revealing any variable on which the pair differs form a new blocking clause: every sufficient plan must contain one of them. Go to 1."
4. "If none exists, the proposal is an optimal sufficient plan."

If a pair is found that no available action can separate, the blocking clause is empty and the state is NEITHER. To list every inclusion-minimal sufficient plan, "each found plan's supersets are blocked and the loop continues. With positive costs, every plan found this way is inclusion-minimal, and plans arrive in nondecreasing cost." Enumeration has a cap of 512 plans.

The module states why MaxSAT is used and where it stops: "once sufficiency is reduced to 'hit every distinguishing pair', minimum-cost plan selection is exactly weighted hitting set, which is what weighted MaxSAT encodes. MaxSAT alone could not express sufficiency (a for-all over outcomes); the refinement loop supplies that part." The solver is not the contribution: "The benchmark's novelty cannot depend on the choice of solver" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A17).

### 2.3 Obligations and a hitting set

Sources: [src/msep/obligations/extraction.py](../src/msep/obligations/extraction.py), [src/msep/controllers/obligation_planner.py](../src/msep/controllers/obligation_planner.py).

Obligation extraction enumerates the minimal difference sets of distinguishing pairs with the pair solver: find a pair whose difference set contains no known obligation; shrink it one variable at a time while a pair still exists inside the smaller set; record the result; block it; repeat. "A shrunk set S is minimal: for every v in S, no pair differs only within S \ {v}." The cap is 512 obligations.

The oracle planner then solves a weighted hitting set over the obligations with RC2: one hard clause per obligation listing the actions that discharge it, and one soft clause per action weighted by its cost. If some obligation has no discharging action, there is no plan. This planner "receives the exact formal state and the instance, so it cannot be evidence that anything helps an agent. It serves as a third exact path in E0."

### 2.4 Brute force: the independent path

Source: [src/msep/oracle/brute_force.py](../src/msep/oracle/brute_force.py).

"Independent of the SAT path: it never reads the CNF and never calls a solver. It enumerates every full assignment, keeps those that satisfy the rule formulas (evaluated directly) and the known values, and decides everything by set operations on those assignments. Exponential; intended for small worlds." Its limits are 16 variables and 14 actions.

- **Sufficiency:** the q-true and q-false assignments, projected on the known and revealed variables, must be disjoint sets.
- **Plans:** every subset of the action menu is tested; optimal and inclusion-minimal plans are read off the full table.
- **Obligations:** all pairwise differences between q-true and q-false assignments are formed, and the inclusion-minimal ones are kept.

The independence is in the method (direct formula evaluation and set operations against CNF and solvers). Both paths were written for this project.

### 2.5 Weighted model counting (posterior rule)

Source: [src/msep/oracle/probability.py](../src/msep/oracle/probability.py). "Second, independent path for probabilities: weighted model counting by DPLL-style splitting over the CNF, with exact rational arithmetic." Because the posterior rule is not monotone, "plan search therefore enumerates all plans instead of using refinement". This path is validated but is not used by any reported experiment.

## 3. The validation run (E0)

Recorded in [results/oracle_validation.md](../results/oracle_validation.md) and `results/oracle_validation.json`, written by [experiments/e0_oracle_validation.py](../experiments/e0_oracle_validation.py). "Any disagreement is a blocker: the script exits non-zero."

> "**Status: PASS** — 228199 checks, 0 failed."

| Item | Value |
|---|---|
| Recorded commit | `1d147932a8f014590e171c3ef5eb3d4fdc2f88ab` (2026-11-04) |
| Environment | Python 3.13.18, pysat 1.9.dev17, 145.4 s |
| Command | `python experiments/e0_oracle_validation.py --small 10000 --medium 2000 --families 200 --families-v3 100` ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.1) |
| Language model calls | none |
| Paths compared | "brute-force enumeration (formula evaluation, no SAT), SAT/MaxSAT refinement (CNF, CaDiCaL + RC2), SAT obligation extraction + MaxSAT hitting set (obligation planner), and weighted model counting (posterior rule)" |

The oracle and obligation source files are identical at the recorded commit and at the commit of the benchmark freeze (`2b496e7`); the freeze record pins their hash ([data/FREEZE_v3.json](../data/FREEZE_v3.json), `oracle_files_sha256`).

### 3.1 Instances

| Suite | Instances | Decision rules | Mean / max variables | Mean / max actions |
|---|---|---|---|---|
| Random, small | 10,000 | logical 7,493; posterior 2,507 | 5.0 / 8 | 3.3 / 7 |
| Random, medium | 2,000 | logical 1,576; posterior 424 | 6.5 / 10 | 4.5 / 9 |
| Families, earlier template | 200 families, 2,200 states (11 sibling types, 200 each) | logical | Not recorded | Not recorded |
| Families, template v3 | 100 families, 765 states | logical | Not recorded | Not recorded |

Classes in the random suites cover all cases, including ties: small has ALREADY_SUFFICIENT 4,192, AMBIGUOUS 92, BOTH 644, COMPUTATION_ONLY 697, INFORMATION_ONLY 1,687, NEITHER 2,688; medium has 869, 11, 143, 126, 333 and 518 in the same order.

The random instances use simple computation tasks (two-digit divisibility, short sums), "where task difficulty plays no role" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F1). One simple task kind, syllogisms, adapts about 30 lines from an earlier project of the author; it is "used only in random oracle-validation instances" and was "checked against brute force first" ([paper/extended_report.md](../paper/extended_report.md), Appendix B).

### 3.2 Checks

The table reproduces [results/oracle_validation.md](../results/oracle_validation.md). Every check has 0 failed and 0 skipped.

| Check | Passed | What it compares |
|---|---|---|
| `plan_analysis_solver_vs_brute` | 12,034 | "SAT/MaxSAT refinement vs enumeration: empty-plan sufficiency, optimal cost, all optimal plans, all inclusion-minimal plans" |
| `resource_class_solver_vs_brute` | 12,034 | "Resource class, SAT/MaxSAT vs enumeration" |
| `random_plan_sufficiency_sat_vs_brute` | 60,170 | "Sufficiency of random plans, SAT vs enumeration" |
| `obligations_sat_vs_brute` | 12,034 | "Obligation sets (minimal distinguishing variable sets), SAT vs enumeration" |
| `no_obligations_iff_sufficient` | 12,034 | "No obligations exactly when the current state is sufficient" |
| `planner_optimal_cost` | 9,135 | "Obligation planner returns an optimal plan" |
| `planner_neither` | 2,899 | "Obligation planner defers exactly on NEITHER" |
| `optimal_plan_sufficient` | 11,813 | "Every optimal plan is sufficient" |
| `optimal_plan_cheapest` | 11,813 | "No sufficient plan is cheaper than an optimal plan" |
| `optimal_plan_inclusion_minimal` | 11,813 | "Removing any action from an optimal plan makes it insufficient" |
| `neither_full_plan_insufficient` | 2,899 | "NEITHER (logical): even the full action set is insufficient" |
| `both_every_optimal_plan_mixed` | 1,477 | "BOTH: every optimal plan has an information and a computation action" |
| `both_single_resource_insufficient` | 1,459 | "BOTH (both necessary): all information actions alone and all computation actions alone are insufficient" |
| `computation_outcome_world_invariant` | 24,256 | "Computation outcomes are identical in every consistent world (no leakage)" |
| `latent_world_exists` | 14,965 | "Some latent world is consistent with the instance" |
| `family_label_oracle_vs_brute` | 2,200 | "Family instances: stored class equals enumeration" |
| `family_plans_oracle_vs_brute` | 2,200 | "Family instances: stored plan labels equal enumeration" |
| `family_v3_label_oracle_vs_brute` | 765 | "Template v3 instances: stored class equals enumeration" |
| `family_v3_plans_oracle_vs_brute` | 765 | "Template v3 instances: stored plan labels equal enumeration" |
| `plan_analysis_wmc_vs_brute` | 2,931 | "Posterior rule: weighted model counting vs enumeration, full plan analysis" |
| `posteriors_wmc_vs_brute` | 2,931 | "Posterior rule: exact posteriors per uncomputed completion, WMC vs enumeration" |
| `resource_class_wmc_vs_brute` | 2,931 | "Posterior rule: resource class, WMC vs enumeration" |
| `neither_no_sufficient_plan` | 607 | "NEITHER (posterior): no action set is sufficient" |
| `posterior_tau1_equals_logical` | 12,034 | "Posterior rule with tau = 1 reproduces the logical rule (enumeration)" |
| **Total** | **228,199** | 0 failed |

A check is skipped when "the SAT enumeration of minimal plans or obligations hit its cap (512); those instances are compared on optimal plans only". No instance was skipped in this run.

The count 12,034 is the number of logical-rule states in the run: 7,493 + 1,576 random, 2,200 family and 765 v3 family states.

## 4. Re-verification of the frozen datasets

The E0 run covers 100 v3 families generated for the run. The frozen 300-family pool and the derived datasets were re-verified separately. The sentence in the paper, "a separate brute-force path re-verified every label (228,199 checks, 0 disagreements)" ([paper/report.md](../paper/report.md) §3.1), joins two records: the 228,199 checks of E0, and the full-pool re-verification in the first row below.

| Dataset | Check | Result | Source |
|---|---|---|---|
| `pool_v3` (2,282 states) | "Brute-force re-verification of class, optimal cost and every optimal plan" | 2,282 instances, 0 mismatches | [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4 |
| `pool_v3` | Rendering round trip: "state rebuilt from the prompt text alone, then re-solved" | 2,282 instances, 0 mismatches | same, §4d |
| `pool_v2` (3,300 states) | Brute-force re-verification of labels | 3,300, 0 mismatches | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.2 |
| Variants for E10–E12, deterministic sample | Brute-force label re-verification; rendering round trip | 534 variants, 0 mismatches each | [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §5 |
| T1 pairs (3,938 items) | "SAT oracle = brute-force oracle on every member", with three structural checks | 1,969 pairs, 0 failed checks | [PREREG_T1.md](../experiments/preregistrations/PREREG_T1.md) §1; EXPERIMENT_INDEX §4.1 |
| Rewordings (548 items) | Inverse parser recovers a state equal to the canonical one | 548, 0 failures | [data/robust_v1_validation.json](../data/robust_v1_validation.json) |
| Study 1 items (436 states) | The generator re-solves every state and asserts the stored class, cost and optimal plans | assertion in the generator; a failure stops generation | [experiments/generate_followup.py](../experiments/generate_followup.py), `check_oracle` |
| Study 2 items (209 sweeps) | The generator re-solves every item and checks the below / equal / above property and the stored labels | 0 sweeps dropped for failing re-verification; 49 dropped for lacking a side | [data/followup_v1_manifest.json](../data/followup_v1_manifest.json) |
| Study 3 items (174) | Inverse parser recovers the exact state for every item | assertion in the generator | [experiments/run_repair.py](../experiments/run_repair.py), `generate` |

## 5. Mutation tests: the checks can fail

An agreement check is only informative if a wrong solver would fail it. [tests/test_mutation.py](../tests/test_mutation.py) plants two bugs in the SAT path and requires that the comparison with brute force reports disagreements on 400 random instances.

| Planted bug | Effect | Required outcome |
|---|---|---|
| Difference sets truncated to one variable (`test_truncated_difference_sets_are_caught`) | The refinement loop adds blocking clauses that are too strong | at least one disagreement |
| Known values not fixed in the second copy of the pair encoding (`test_unfixed_knowledge_is_caught`) | The pair solver searches among assignments that contradict the evidence | at least one disagreement |

"The agreement checks must be able to fail: planted solver bugs are detected" (module docstring). The tests were committed on 2026-11-03 with an earlier E0 run (commit message "E0 oracle validation results and mutation tests"); the run reported in Section 3 was committed on 2026-11-04 (`6c820b5`).

## 6. Other tests that bear on the labels

| Test file | What it checks |
|---|---|
| [tests/test_oracle_agreement.py](../tests/test_oracle_agreement.py) | The E0 comparison on 600 seeds as part of the test suite: plan analysis, obligation sets, planner cost, random-plan sufficiency, posteriors |
| [tests/test_minimality.py](../tests/test_minimality.py) | On 300 random instances: optimal plans are sufficient, lose sufficiency when any action is removed, and are no dearer than any sufficient plan; minimal plans have no sufficient proper subset |
| [tests/test_sufficiency.py](../tests/test_sufficiency.py) | Hand-built cases: BOTH, single-resource classes, ALREADY_SUFFICIENT when one conjunct is false, NEITHER when an action is missing, a relevant-but-insufficient decoy, observing the target, "high probability is not entailment", non-monotonicity of the posterior rule |
| [tests/test_leakage.py](../tests/test_leakage.py) | On 400 random instances: computation outcomes are the same in every consistent world, and information outcomes vary |
| [tests/test_certified_tasks.py](../tests/test_certified_tasks.py) | "Each certified task is checked against an independent method" (for example Miller–Rabin against trial division) |
| [tests/test_multiple_optima.py](../tests/test_multiple_optima.py), [tests/test_scoring_ties.py](../tests/test_scoring_ties.py) | "Every equally optimal plan is accepted by every metric (not only a canonical one)" |
| [tests/test_freeze.py](../tests/test_freeze.py) | The freeze record holds, and the split function reproduces the frozen assignment |

## 7. What the validation does and does not show

- **It shows agreement, not a proof of the code.** Three methods that share no solving code agree on every compared instance. The proposition they implement is proved in [formal_problem.md](formal_problem.md) §8.
- **Sizes.** "Exactness is shown on the validated instance sizes only" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.1). "Worlds are small (up to 16 variables for brute force), so exactness is cheap and scaling claims are not yet tested" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F7).
- **Normative labels.** The oracle defines what a valid plan is. It does not say whether a model could carry out the computation ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A3).
- **The labels are about the formal state.** Whether the text says what the formal state says is a separate question. The round trip in Section 4 shows that the intended reading recovers the state; the known ambiguity in the text is described in [benchmark_design.md](benchmark_design.md) §14.
