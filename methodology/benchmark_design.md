# Benchmark design

This document describes how the MSEP benchmark was built and what is known to be wrong with it. It answers: what a family and its sibling states are, how trap siblings are chosen, how the split is made, how states are turned into text, what the first two templates gave away and how the third was redesigned, what the text-only heuristic baselines score, how the counterfactual pairs (T1), the cost variants (E10) and the four rewordings were generated and validated, what the two-line clarified wording of follow-up Study 1 changes, and how datasets are frozen. The last section lists the known defects of the benchmark text. The formal definitions are in [formal_problem.md](formal_problem.md); the oracle that labels every state is described in [oracle_validation.md](oracle_validation.md).

No language model was involved in generating, selecting or labelling any item. "Selection uses oracle labels only, never any agent's behaviour" ([src/msep/benchmark/template_v3.py](../src/msep/benchmark/template_v3.py)).

## 1. Size and composition

Benchmark v3.0 (`pool_v3`) has 300 families and 2,282 states ([data/pool_v3_manifest.json](../data/pool_v3_manifest.json)).

| Count | Value | Source |
|---|---|---|
| Families | 300 (train 165, dev 72, test 63) | `families_per_split` in the manifest |
| States | 2,282 | `instances` in the manifest |
| States by oracle class | ALREADY_SUFFICIENT 300, INFORMATION_ONLY 419, COMPUTATION_ONLY 415, BOTH 848, NEITHER 300 | `resource_classes` in the manifest |
| States by sibling type | five core types, 300 each; RELEVANT_INSUFFICIENT_INFORMATION 200; RELEVANT_INSUFFICIENT_COMPUTATION 173; SUFFICIENT_NON_MINIMAL 178; PREMATURE_STOP 231 | `sibling_types` in the manifest |
| Dev split | 545 states, 401 resolvable | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §1 |
| Test split | 468 states; 342 resolvable | [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §1; denominators in [paper/extended_report.md](../paper/extended_report.md) Appendix E.1 |
| Mean number of actions, mean prompt length (dev) | 7.66 actions; 5,770.91 characters | [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4d |

A resolvable state is one whose class is INFORMATION_ONLY, COMPUTATION_ONLY or BOTH.

## 2. Families and sibling states (template v3)

A **family** is one random theory: a set of variables, rules, a latent world, certified computation tasks and a menu of priced actions. Its **sibling states** share the theory and differ in what is known and which actions are offered.

**The theory** ([src/msep/benchmark/template_v3.py](../src/msep/benchmark/template_v3.py), `sample_theory`):

| Element | How it is drawn |
|---|---|
| Motif of the rule that defines Q | one of four: and/or tree, parity, threshold ("at least 2 of {a, b, c}"), case split ("which input matters depends on s"). The body is negated with probability 1/2 |
| Inputs | 3 or 4 for and/or, 3 for the others; the kinds start from one world fact and one computational fact, the rest are drawn at random |
| Indirection (probability 0.4) | one input becomes a node defined by a rule over two new leaves, and the node has no action ("must act on u1, u2") |
| Bridges (0 to 2) | one-way implications among inputs, so "an unknown input can be entailed" |
| Mixed route (probability 0.3) | "a world fact equivalent to a computed one", or the reverse |
| Decoys (1 or 2) | one-way implications into an input |
| Distractors (2 to 4) | variables "with same-shaped rules, disconnected from q" |
| Single actions | one per leaf, decoy and distractor; cost 1 to 4 |
| Bulk actions (probability 0.5 per kind, when at least two leaves of that kind exist) | "one action reveals several inputs, cheaper or dearer than the parts": cost is the sum of the two parts plus −1, +1 or +2 |

**The sibling states.** "Siblings are NOT built per class. Knowledge states and menus are drawn from ONE distribution, identical for every class; the oracle labels each draw and draws are binned by class" (module docstring of `template_v3.py`). In one draw, each non-target variable is shown as known with a probability chosen from {0.25, 0.4, 0.55}, and each action is kept on the menu with probability 0.85 (`_draw_state`). A known value is always the true value.

A draw is discarded if its class is AMBIGUOUS, if a resolvable class is not cost-invariant, or if a BOTH state does not need both resources (`_quick_label`; definitions in [formal_problem.md](formal_problem.md) §7). "A family is kept when every core class (ALREADY_SUFFICIENT, INFORMATION_ONLY, COMPUTATION_ONLY, BOTH, NEITHER) has a draw". A theory that cannot fill the five classes is replaced by a new one (up to 40 theories, 160 draws each).

## 3. Trap siblings

Trap siblings are optional. They "are added when a draw has that property" (`_trap_types` in `template_v3.py`). A trap sibling never duplicates the formal state of a core sibling.

| Trap type | Property of the state, decided by the oracle | States in v3 |
|---|---|---|
| RELEVANT_INSUFFICIENT_INFORMATION | An information action is relevant, is in no inclusion-minimal sufficient plan and is not sufficient alone | 200 |
| RELEVANT_INSUFFICIENT_COMPUTATION | The same for a computation action | 173 |
| SUFFICIENT_NON_MINIMAL | Some action is *dominated*: it is in an inclusion-minimal sufficient plan and in no cheapest one | 178 |
| PREMATURE_STOP | The first cheapest plan has at least two actions, and no single action of it settles Q in the actual world | 231 |

These states carry the two contrasts named in the paper: "relevant but insufficient plans; sufficient but not minimal plans" ([paper/report.md](../paper/report.md) §3.2). Because trap siblings are optional, "Families of the same sibling type that are missing in a family ... are excluded from the paired tests that need them; the counts are reported" ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §8).

## 4. The family-level split

"All counterfactual siblings from the same base scenario stay in the same split. Random row splitting is prohibited" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A13).

The split "is a deterministic function of the family id alone, so it cannot depend on row order and siblings cannot be separated" ([src/msep/benchmark/splits.py](../src/msep/benchmark/splits.py)). It is a salted SHA-256 hash of the family id with target shares 0.6 / 0.2 / 0.2, which gives 165 / 72 / 63 families. Variants, counterfactual pairs and rewordings keep the family id and split of their base state.

| Split | Families | Use | Source |
|---|---|---|---|
| train | 165 | Planned for prompt development and probe training. No train family was sent to any model before the follow-up studies, which then used 132 of them | [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §2; [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §0; [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §1 |
| dev | 72 | Calibration, development runs, the registered development comparisons, the rewording study (18 families) | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4 |
| test | 63 | "the single frozen final evaluation. The code refuses it without `--allow-test`" | PROTOCOL.md §2 |

Leakage checks on the frozen pool: "Families in more than one split: 0 (of 300)"; "Identical prompt texts across splits: 0" ([results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §2).

## 5. Text rendering

"Formal state is generated first. Language rendering is downstream" (ASSUMPTIONS A11). "Nothing here is read by any oracle" ([src/msep/benchmark/rendering.py](../src/msep/benchmark/rendering.py)).

- **Neutral handles.** Variables are shown as Q, F1, F2, … (world facts) and K1, K2, … (computational facts), "assigned by a per-family random permutation, so the internal role names (w1, dw, wa, ...) never reach the model".
- **Skins.** World facts get short phrases from one of three themes: warehouse, lab, abstract. A fourth theme (harbour) is held out for a shift experiment that was not run. A computational fact is labelled with the description of its certified task.
- **Action names.** `ASK_<handles>` for information actions. A computation action on one fact is named after its procedure (`EXECUTE_CODE_`, `RUN_PRIMALITY_TEST_`, `RUN_SOLVER_`, `COMPUTE_POSTERIOR_`); otherwise `COMPUTE_`.
- **Rule order.** In v3 the rules are shuffled per family with a stored seed, so "the rule about Q is not always in the same place".
- **Fixed sections.** Decision; facts about the world; computational facts; rules; "Known so far"; available actions; the decision rule and a closing paragraph. The closing paragraph is quoted in [paper/extended_report.md](../paper/extended_report.md) Appendix F. A full example is in [formal_problem.md](formal_problem.md) §10.

**Round trip.** A rule-based parser rebuilds the formal state from the text alone and the oracle re-solves it: "2282 instances, 0 mismatches. The prompt carries everything the oracle uses" ([results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4d). The same parser is the no-model baseline P of the evaluation ([eop_architecture.md](eop_architecture.md)).

## 6. Templates v1 and v2, and the shortcut the audit found

All three template versions were written on 2026-11-03 and 2026-11-04, before any model was run ([BENCHMARK_CHANGELOG.md](../research/working_documents/BENCHMARK_CHANGELOG.md)).

| Date | Version | Change | How the reason was found |
|---|---|---|---|
| 2026-11-03 | v1 | "First families; certified computation tasks replace trivial ones" | "Review: trivial tasks could be done in the head" |
| 2026-11-04 | v2 | "Randomised redundant actions, distractors, decoy noise" | "Own audit: count probe 86–90%" |
| 2026-11-04 | v3 | "New template: random motifs, class-independent sibling sampling, random implication signs, seeded rule order, version-2 certified tasks" | "Independent adversarial audit: v2 solved 100% by reading Q's rule; value, position and cost leaks; mental shortcuts" |
| 2026-11-04 | v3 | "Parenthesise complex left sides of biconditionals in rendering" | "Rendering round-trip check: ambiguous nested parity" |
| 2026-11-04 | v3.0 frozen | Freeze record [data/FREEZE_v3.json](../data/FREEZE_v3.json) (code commit 2b496e7) | Readiness review |

**Templates v1 and v2** ([src/msep/benchmark/families.py](../src/msep/benchmark/families.py)). One fixed structure: Q is defined by an and/or over two world requirements and one or two computed requirements, with one alias, two one-way decoys and distractors. Each family had eleven siblings built per type. Each pool has 300 families and 3,300 states ([data/pool_v1_manifest.json](../data/pool_v1_manifest.json), [data/pool_v2_manifest.json](../data/pool_v2_manifest.json)).

**Defect of v1: surface counts.** A lookup-table probe on counts of offered actions and of known and unknown variables predicted the class far above the majority baseline. Template v2 randomised, "independently of the sibling type", which redundant actions are offered, six distractor variables, and whether an uninformative decoy is shown as known ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F8).

**Defect of v2: the Q rule.** "Template v2 is solved 100% by reading only the rule that defines q. Rule order, rule signs and costs also leaked roles, and decoy rules copied hidden and certified values" (ASSUMPTIONS F12). The reason is structural: "in templates v1/v2 the target rule always lists every requirement directly, so 'act on the unknown variables in Q's rule' is a near-perfect shallow strategy" (`template_v3.py`). The recorded numbers for this claim are in the table below: on v2 dev the heuristics reach 100.0% class accuracy and 90.9% optimal plans. The sources' phrase "solved 100%" therefore matches the class accuracy, not the optimal-plan rate.

**Recorded measurements across versions** (no model; probe trained on train, read on dev):

| Measure | v1 | v2 | v3 | Source |
|---|---|---|---|---|
| Count probe, insufficient states only (action / knowledge / all counts) | 86.2% / 90.0% / 90.0%; majority 50.0% | 56.4% / 69.2% / 57.9%; majority 50.0% | 40.2% / 42.9% / 41.9%; majority 42.7% | [results/audit_v2/benchmark_audit.md](../results/audit_v2/benchmark_audit.md) §1; [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §1 |
| Heuristic h1: class accuracy / plan sufficient / plan optimal (dev, all states) | Not recorded | 90.9% / 90.9% / 87.2% | 67.0% / 61.5% / 46.2% | §4b of the two audit files |
| Heuristic h1p | Not recorded | 100.0% / 90.9% / 90.9% | 57.2% / 54.5% / 40.9% | same |
| Heuristic h1pp | Not recorded | 100.0% / 90.9% / 90.9% | 74.7% / 75.4% / 50.6% | same |
| Posterior task solved by rounded log-likelihood sums | Not recorded | 100.0% (n = 293) | 51.5% (n = 233) | §4c of the two audit files |

The v2 pool is kept only as "a shallow subset", for a structural comparison that was not run ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §1; [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.14).

## 7. The v3 redesign

What changed, with the measured result of each fix on the frozen pool ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F12; [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4a, §4c):

| Problem in v2 | Fix in v3 | Measured on v3 |
|---|---|---|
| Q's rule lists every requirement | Random theories from four motifs, with optional indirection, bridges, mixed routes and bulk actions (Section 2) | Heuristics in Section 8 |
| Siblings built per class could differ in systematic ways | "States are drawn from one class-independent distribution and binned by the oracle" | Count probe between 2.5 points below and 0.9 points above the majority baseline (Section 6; the "all classes" scope gives 34.9% / 38.0% / 35.6% against 37.1%) |
| Rule signs copied hidden values | "implication signs are random, made true through the antecedent" | "Implication rules whose consequent is true in the latent world: 0.51 of 1307" |
| Rule position gave away the Q rule | "rule order is shuffled per family with a stored seed" | "most common position holds 18% of instances across 8 positions" |
| Costs marked the right action | "costs are random" | Share of actions that are optimal, by cost 1 to 10: between 0.10 and 0.21 |
| Certified tasks had mental shortcuts | Certified tasks version 2: "modpow with a prime modulus; primes and semiprimes from the same size distribution; posterior with sixteen observations at a 0.0002–0.0015 margin" | Shortcuts at 51.5% (posterior), 47.6% (modular exponentiation; majority 52.4%), 49.3% (primality; majority 56.7%); "3-SAT near the threshold: no shortcut found by the audit" |
| A planner could evaluate a task from its description | "Agent-side states hold opaque tasks. They cannot be evaluated, so a planner obtains certified results only by running computation actions" | [tests/test_realistic_planner.py](../tests/test_realistic_planner.py) |

Balance of the frozen pool: the true rate of the target is between 0.48 and 0.51 for every sibling type, and the true rate of computational facts is 0.46 to 0.50 by task kind ([results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §3).

**What the redesign did not remove.** "A heuristic that resolves every unknown input of q's definition (one level of expansion) still gets about 50% optimal plans" (ASSUMPTIONS F12). "The residual is partly inherent. The class is defined by which *relevant* variables are unknown, so counts by kind carry some signal" (F8). Exactly balanced counts across classes were not attempted (F8).

## 8. Heuristic baselines and what they score

The baselines read only the prompt text, through the rule-based parser. They use no language model and no oracle ([src/msep/agents/heuristics.py](../src/msep/agents/heuristics.py)). Tier: no-model baseline.

| Baseline | Rule |
|---|---|
| h1 | "unknown variables in Q's rule -> class by their kinds; plan = actions on them" |
| h1p | h1, "plus: use an equivalent variable ('X if and only if Y') when its action is cheaper, and answer NEITHER when an unknown Q-rule variable has no action" |
| h1pp | h1p, "plus: a Q-rule variable with no action that is defined by a rule ... is replaced by the unknown variables of that formula" |
| Fixed policies | always answer, ask everything, compute everything, always abstain |

Scores on v3 (Detection-Controlled where a mode applies; no model):

| Baseline | Dev: plan sufficient / optimal, resolvable states (n = 401) | Held-out: plan sufficient, resolvable states (n = 342) | Held-out: correct deferral on NEITHER | Source |
|---|---|---|---|---|
| h1 | Not recorded on this basis | 0.70 [0.63, 0.78] | 0.24 [0.14, 0.35] | [paper/extended_report.md](../paper/extended_report.md) Appendix E.1 |
| h1p | Not recorded on this basis | 0.67 [0.59, 0.75] | 1.00 | same |
| h1pp | 0.845 / 0.586 | 0.88 [0.84, 0.91] | 1.00 | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.2; extended report E.1 |
| always ask / always compute | Not recorded | 0.23 / 0.25 | 0.00 / 0.00 | extended report E.1 |

How to read them:

- **Sufficiency alone is a weak metric on this benchmark.** "The strongest heuristic still gives a sufficient plan on 0.85 of resolvable dev states, so sufficiency alone is a weak metric here; optimality and stopping are harder" ([paper/extended_report.md](../paper/extended_report.md) §3.2).
- **Deferral on NEITHER is not evidence of reasoning by itself.** h1pp "defers on every NEITHER state, so NEITHER results are not evidence of reasoning" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.2).
- **`heuristic_hard`** is "a pre-registered stress-test subset": the states where h1pp fails, "determined from the prompt text alone". It has 198 of 545 dev states and no NEITHER state. "Compare within class only, never pooled against the full set" ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §6; [results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4d). The pre-registered secondary tests (H2–H4) on this subset are absent from the result files ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §5).
- **Surface-count probe.** It is "reported as a surface-feature baseline alongside every E3 result" (audit §1). In the held-out diagnosis table its value is 0.45 ([paper/extended_report.md](../paper/extended_report.md) Appendix E.1).

## 9. Counterfactual pairs (T1)

T1 was designed during the sprint, after calibration showed three models at ceiling, and was registered on 2026-11-13 before any model had seen a T1 item ([PREREG_T1.md](../experiments/preregistrations/PREREG_T1.md)).

**Construction** ([src/msep/benchmark/t1_flips.py](../src/msep/benchmark/t1_flips.py); PREREG_T1 §1):

- A pair is (A, B). "A is a frozen v3 record re-rendered unchanged; B is the same state with exactly one more variable fixed at its true value".
- Two edit kinds: **E_OBS**, "a world variable becomes observed evidence"; **E_CERT**, "a computed variable gets its certified result".
- "Rules, latent world, action menu, costs and rendering are identical". The two prompts "differ in exactly one line ('Known so far'), by 3–13 characters".
- "Both members are labelled from scratch by the exact oracle, and a pair is kept only if the set of optimal plans changes" or the class changes.
- One edit per base state, drawn with a seed derived from the base id, "uniformly over the non-empty (edit kind, transition type) groups". "Nothing here looks at model behaviour."
- Transition types: **direct**, where "dropping what became known is enough", and **indirect**, "anything else (the plan restructures ...)".

**Validation.** "A prompt equals v3; one-line diff; identical menus; SAT oracle = brute-force oracle on every member (3,938 items)", with 0 failures at registration (PREREG_T1 §1).

**Counts.**

| Set | Pairs (items) | Pairs whose edited state is ALREADY_SUFFICIENT | Source |
|---|---|---|---|
| Full set | 1,969 (3,938): train 1,098, dev 469, test 402 | Not recorded for the full set | PREREG_T1 §1 |
| Dev pilot, families ranked 11–30 | 133 (266): 85 direct, 48 indirect | 55 | PREREG_T1 §3; [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md) |
| Dev follow-up T1B, families ranked 31–72 | 272 (544) | 122 | PREREG_T1B, "Items" |
| Held-out test | 402 (804) | 169 | [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §1; [results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md) |
| Dev pairs of the 10 calibration families | 64 | in no item set | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.14 |

**Shortcut control.** On the pilot families, "text-only heuristics reach 0.81–0.84 transition accuracy on direct pairs and 0.00–0.28 on indirect pairs". So "the indirect stratum is the primary test; direct pairs are a shortcut control" (PREREG_T1 §2).

**Scoring.** "A model is correct on a pair only if it is correct on both states" ([paper/extended_report.md](../paper/extended_report.md) §3.4). The over-intervention measure uses only the pairs whose edited state is already sufficient; see [evaluation_protocol.md](evaluation_protocol.md).

## 10. Cost variants (E10)

Cost variants keep "the epistemic structure (variables, rules, knowledge, menu)" and change one price ([src/msep/benchmark/variants.py](../src/msep/benchmark/variants.py)). They were generated and frozen with the benchmark on 2026-11-04: 2,375 cost variants ([data/variants_v3_manifest.json](../data/variants_v3_manifest.json)). No model was run on them until follow-up Study 2.

**Construction for v3** (`generic_cost_sweep`). Take a dominated action d: "in some minimal sufficient plan, in no optimal plan". Compute the boundary cost b at which d's best plan ties the cheapest plan. Set d's cost to b − 1, b, b + 1 and its original value. Costs below 1 are skipped. Each variant is "relabelled from scratch by the oracle".

| Side | Price of d | Property checked by the oracle | Items in Study 2 |
|---|---|---|---|
| below | b − 1 | "every cheapest plan contains d. The cheapest plan has changed" | 209 |
| equal | b | "plans with and without d tie; all tied plans count as correct" | 209 |
| above | b + 1 and the original cost | "no cheapest plan contains d" | 362 |

**Selection for Study 2** ([PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §2; [experiments/generate_followup.py](../experiments/generate_followup.py); [data/followup_v1_manifest.json](../data/followup_v1_manifest.json)). The generator re-solves every item and checks the three properties and the stored labels. "Sweeps without all three sides (a cost below 1 would be needed) are dropped before families are chosen: 49 sweeps." Then "the first 60 train families, in sorted order after the 60 of Study 1, that have a complete sweep: 209 sweeps, 780 items". Tier of Study 2: follow-up, registered after the held-out results were viewed.

## 11. The four rewordings and their validation

The rewording study asks whether results depend on the benchmark's regular wording. It was registered separately on 2026-11-14 ([PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md)). Tier: rewording study (registered separately).

**Base items.** "v3 dev families at positions 0, 4, 8, … of the sorted family ids: 18 families, all 137 of their states. Chosen by position, not by any model result." Four variants per state give 548 items.

**What stays fixed.** "The formal state, the handles (Q, F1, K2, …), the action names, the costs and every oracle label are those of the base item. Only the wording of the state description changes; the task instructions and output format after it are unchanged."

| Wording | What changes | The benchmark's own parser still reads it |
|---|---|---|
| lexical | "same layout, order and rule notation; different terminology (e.g. 'Constraints', 'Established so far', 'evidence query', 'calculation', 'price', 'holds / does not hold')" | 0 of 137 |
| syntax | "canonical terminology and order; facts, rules, known values and actions as sentences with a different structure. Rules are in words" | 0 of 137 |
| reorder | "canonical wording; sections and the items inside them in a different order" | 137 of 137 |
| prose | "running paragraphs without list markup, combining the lexical terminology, the sentence forms and a different order. The least template-like rendering" | 0 of 137 |

One example state in all five wordings is in [paper/extended_report.md](../paper/extended_report.md) Appendix F.

**Validation, in three layers.**

1. **Inverse parser.** "an inverse parser written for these templates recovers, from each rendered unit, a state equal to the canonical one"; every handle and action name occurs in the variant; generation is deterministic. Result: 137 of 137 per wording, 0 failures over 548 items ([data/robust_v1_validation.json](../data/robust_v1_validation.json)); also run on "all 5,076 variants of the train split during development" (PREREG_ROBUST §1).
2. **Stated limit of layer 1.** "it shows that the intended reading recovers the state. It cannot show that no other reading is plausible."
3. **Independent reading of a sample** ([ROBUST_AUDIT.md](../experiments/preregistrations/ROBUST_AUDIT.md)). 24 train-split variants, 6 per wording, from 24 different families, were read by a language model that "received only the 24 texts: no code, no data, no labels, no description of the generator". "It is a language model, not a person. A human audit was not done." Its 24 written-down states were compared with the true states by program: "24 of 24 equal to the true state". It raised one scope risk: "It is not the case that (X) exactly when Y" could attach the negation to X or to the whole sentence. The fix: "a negated compound statement that is an argument of another connective is now parenthesised". After the fix "all 548 dev variants and all 5,076 train variants were regenerated and validated again (0 failures)". "The 24 audited texts were read before this last fix; the fix only adds parentheses."

**Reuse.** Follow-up Study 3 uses the same generator, unchanged, on other families: the first 12 train families used by neither Study 1 nor Study 2, every state (87), in the syntax and prose wordings, 174 items ([PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §1; [data/repair_v1_manifest.json](../data/repair_v1_manifest.json)).

## 12. The clarified wording of follow-up Study 1

**The ambiguity.** "The benchmark text says of every computational fact that 'its certified value is not yet known', while the 'Known so far' line can list such a value and the action for it is usually still offered" ([PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1). A model that re-runs that computation is counted as acting on a state that is already sufficient. "The intended reading: the known list is authoritative" ([ROBUST_AUDIT.md](../experiments/preregistrations/ROBUST_AUDIT.md)).

**The intervention.** Each state is rendered twice. W0 is the benchmark text, unchanged. W1 differs in two lines only (PREREG_FOLLOWUP §1; [data/followup_v1_manifest.json](../data/followup_v1_manifest.json)):

| Line | W0 (benchmark text) | W1 (clarified) |
|---|---|---|
| Header of the computational facts | `...; its certified value is not yet known):` | `...; its certified value is unknown unless it is listed under "Known so far"):` |
| Known-values line | `Known so far: ...` | `Known so far (established values, including certified results of computations already run): ...` |

"Variables, rules, known values, actions, costs, certified computations and oracle labels are identical; the generator asserts that no other line differs and re-solves every state with the oracle."

**Items.** The first 60 train families in sorted order: 436 states, 872 items. 256 are ALREADY_SUFFICIENT (60 sufficient from the start, 196 after one edit); 237 of the 256 are *exposed*, meaning "the state offers a computation whose results are all listed as known, which is where W0 is ambiguous". 60 COMPUTATION_ONLY, 60 BOTH and 60 NEITHER states are controls. "Items were chosen by these rules and oracle labels only. No model output was involved."

**Standing.** This is "a new wording intervention. It is not a replication of the held-out stopping test" (PREREG_FOLLOWUP §1). Tier: follow-up, registered after the held-out results were viewed. The frozen benchmark text itself was not changed.

## 13. Freezes and manifests

Generated data is not in git. Each dataset is rebuilt deterministically by a command and pinned by SHA-256 in a freeze record ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §1). The rule after the v3 freeze: "only objective bug fixes are allowed; each needs a new freeze record ... and an entry here. **No change may be made to raise or lower model scores**" ([BENCHMARK_CHANGELOG.md](../research/working_documents/BENCHMARK_CHANGELOG.md)). No entry was added after the freeze.

| Freeze record | What it pins | Date (UTC) | Documented verification status |
|---|---|---|---|
| [data/FREEZE_v3.json](../data/FREEZE_v3.json) | Benchmark v3.0: generator and oracle source hashes, dataset hashes (pool_v3, variants, the v2 subset), seed scheme, every family's split | 2026-11-04 | OK on 2026-11-14 |
| [data/FREEZE_T1.json](../data/FREEZE_T1.json) | T1 pairs, generator, oracle, analysis | 2026-11-13 | OK on 2026-11-14 |
| [data/FREEZE_T1B.json](../data/FREEZE_T1B.json) | T1B registration, analysis, prompts, data | 2026-11-13 23:53 | OK on 2026-11-14 |
| [data/FREEZE_EOP.json](../data/FREEZE_EOP.json), [FREEZE_EOP_A1.json](../data/FREEZE_EOP_A1.json), [FREEZE_EOP_A2.json](../data/FREEZE_EOP_A2.json) | EOP registration and its two amendments | 2026-11-13 23:58; 2026-11-14 11:36; 2026-11-14 13:32 | No longer verify, by design: later amendments changed files they pin. See [protocol_amendments.md](protocol_amendments.md) |
| [data/FREEZE_FINAL.json](../data/FREEZE_FINAL.json) | Held-out protocol: registrations, drivers, analysis, prompts, planner, data, model settings | 2026-11-14 20:04 | OK on 2026-11-14 |
| [data/FREEZE_ROBUST.json](../data/FREEZE_ROBUST.json) | Rewording generator, dataset, audit, driver, analysis | 2026-11-14 20:20 | OK on 2026-11-14 |
| [data/FREEZE_FOLLOWUP.json](../data/FREEZE_FOLLOWUP.json) | Studies 1 and 2: registration, generator, runner, prompt and scoring code, datasets, model settings | committed 2026-11-15 21:03 | Not recorded in the documents |
| [data/FREEZE_REPAIR.json](../data/FREEZE_REPAIR.json) | Study 3: registration, runner, reader, planner, rewording generator, dataset, model settings | committed 2026-11-16 00:13 | Not recorded in the documents |

Sources for the table: dates from the freeze files, [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §6 and the commit history; status from EXPERIMENT_INDEX §6 ("re-checked 2026-11-14"). Commands: `experiments/freeze_benchmark.py --verify`, `experiments/freeze_t1.py --verify`, `experiments/freeze_protocol.py --name NAME --verify`.

Manifests with counts and regeneration commands: [data/pool_v3_manifest.json](../data/pool_v3_manifest.json), [data/variants_v3_manifest.json](../data/variants_v3_manifest.json), [data/robust_v1_validation.json](../data/robust_v1_validation.json), [data/followup_v1_manifest.json](../data/followup_v1_manifest.json), [data/repair_v1_manifest.json](../data/repair_v1_manifest.json).

## 14. Known defects of the benchmark text

These are stated plainly because several results depend on them.

1. **The header of the computational facts contradicts the known-values line.** The header says the certified value "is not yet known"; the known-values line can list one; the action for it is usually still offered. This affects one headline stopping measure. Extent: 18 of 24 audited texts ([ROBUST_AUDIT.md](../experiments/preregistrations/ROBUST_AUDIT.md)); 214 of the 232 already-sufficient held-out states offer a computation for a known computational fact ([results/aggregate/final_test/recertification/recertification.json](../results/aggregate/final_test/recertification/recertification.json)); 237 of 256 already-sufficient states in Study 1. Measured effect (Study 1; follow-up tier): acting on already-sufficient states falls from 0.14 to 0.03 for qwen3.5-397b and from 0.73 to 0.59 for gemma-4-26b +schema under the clarified wording ([results/aggregate/followup/followup_report.md](../results/aggregate/followup/followup_report.md)). The frozen text was not corrected; "A corrected benchmark text, to re-measure stopping without the ambiguity" is listed as future work ([paper/extended_report.md](../paper/extended_report.md) §5).
2. **The wording is regular and machine-generated.** A parser written as the inverse of the renderer recovers every state, and the parser with an exact planner scores 1.00 on the benchmark's own wording ([results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md)). "A high score on it is not a certificate of good epistemic behaviour" ([paper/report.md](../paper/report.md), Appendix A).
3. **The closing paragraph is underspecified on entailed values.** It "says a computational fact enters the decision state 'only through its certified result', next to rules that link facts; whether a value entailed by the rules counts is not spelled out there (the decision rule sentence says it does ...)" ([ROBUST_AUDIT.md](../experiments/preregistrations/ROBUST_AUDIT.md)).
4. **Some labels carry no content.** In the abstract skin, "'is it true that Q holds (Q)?' and 'fact D holds' have no content beyond the label; one text uses 'fact H' beside a task description that mentions 'P(H \| …)'" (ROBUST_AUDIT). When a skin runs out of phrases, a fact is labelled "condition F6 is met" (`rendering.py`; visible in example 2 of [docs/EXAMPLES.md](../docs/EXAMPLES.md)).
5. **Awkward but unambiguous constructions.** "Double negations written out ('not (not F3)'), actions that reveal an already known value, a joint action costing the same as one of its parts, the same rule stated twice in contrapositive form" (ROBUST_AUDIT).
6. **Shallow heuristics still score well on part of the task.** h1pp gives a sufficient plan on 0.85 (dev) and 0.88 (held-out) of resolvable states, an optimal plan on about half of dev states, and defers on every NEITHER state (Section 8).
7. **Surface counts keep some signal.** "The residual is partly inherent" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F8).
8. **Narrow variety.** Four motifs, three skins, small worlds ("up to 16 variables for brute force", ASSUMPTIONS F7). "Linguistic shift" was tested only through the four template-made rewordings.
9. **The rewordings are template-made and were not read by people.** "It is one reader, a language model, on 24 texts. It does not show that every human would read every variant the same way" ([ROBUST_AUDIT.md](../experiments/preregistrations/ROBUST_AUDIT.md)). Defects 1, 3, 4 and 5 are "inherited from the canonical benchmark text" and were kept in the rewordings "because the variants must say what the canonical text says".

Limitations that concern the evaluation and the claims, not the text, are in [limitations.md](limitations.md).
