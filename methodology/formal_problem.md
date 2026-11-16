# Formal problem: Minimal Sufficient Epistemic Planning (MSEP)

This document gives the formal definition of the task that the benchmark scores. It answers: what a state is, what the two kinds of unknown fact and the two kinds of action are, why neither kind of action may reveal the other kind of fact, what it means for a plan to be sufficient and cheapest, how the five resource classes are derived, what an obligation is and why a cheapest sufficient plan is a minimum-cost hitting set of obligations, and which decision rules are implemented, which are used in the reported experiments, and which are only specified. Every definition is quoted from a source in this repository, with the path next to it. The authoritative short statement is Section 3.1 of [paper/report.md](../paper/report.md); the working specification is [PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) and the implemented semantics are the "Phase 1 formal semantics" (F1 to F12) in [ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md).

## 1. The research question and its stages

The question, as specified ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §1):

> "When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?"

The specification separates five stages: detection, diagnosis, planning or targeting, sufficiency, and control or stopping (same section). "The scientific target is primarily stages 2–5, while stage 1 is measured separately." The three evaluation modes that implement this separation are described in [evaluation_protocol.md](evaluation_protocol.md).

## 2. States

The specification represents a benchmark state as a tuple ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §3):

> S = (W, E, C, M, q, I, K, U)

| Symbol | Meaning (PROBLEM_SPEC §3) | In the code ([src/msep/world/state.py](../src/msep/world/state.py)) |
|---|---|---|
| W | latent external world | `LatentWorld`, "kept outside FormalState so no oracle can read it by accident" |
| E | currently observed evidence | `FormalState.evidence`: observed world-variable values |
| C | logical / structural constraints | `FormalState.rules`: formula trees compiled to CNF |
| M | bounded computational state | `FormalState.computed`: computed-variable values already worked out |
| q | target proposition or decision | `FormalState.target` (rendered as Q) |
| I | available information-acquisition actions | `FormalState.info_actions` |
| K | available computation / verification actions | `FormalState.comp_actions` |
| U | utility / cost model | action costs and the declared decision rule |

"The state must be machine-verifiable and independent of natural-language rendering" (PROBLEM_SPEC §3). The formal state is generated first and the text is produced from it afterwards ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A11).

The agent's epistemic state is "the set of full assignments (world variables and computed variables) consistent with C, E and M" (module docstring of `state.py`). In the notation of the extended report, 𝒜(S) is the set of "assignments consistent with the rules and the known values of state S" ([paper/extended_report.md](../paper/extended_report.md), Appendix D).

## 3. World facts and computational facts

There are two kinds of unknown ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F1):

- **World variables** "are contingent external facts. Only information actions (ASK) reveal them, by reading the latent world."
- **Computed variables** "are the results of **certified computations or verifications** on inputs the agent already has." "The inputs are known; the certified result is not." "Until its certified result exists, a computed variable is unknown in the decision state, although it has a fixed true value (logical uncertainty)."

The certified tasks used in benchmark families are: modular exponentiation with a 10–12 digit prime modulus; primality of 13–14 digit numbers; satisfiability of random 3-CNF near the threshold (20 variables, 85 clauses); and a naive-Bayes posterior over sixteen observations against a close threshold ([paper/extended_report.md](../paper/extended_report.md), Appendix D). They "were chosen to be impractical to do mentally" (same place). The first version of the tasks and the later revision are described in [benchmark_design.md](benchmark_design.md).

The convention that follows from this definition is stated in [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §9: "A model that settles a computational fact internally has not run the certified procedure. Under the declared rule its decision is not justified, even if correct." The same section names the risk: "The benchmark could then measure tool-policy compliance, not epistemic planning." The control experiment designed to measure this (E14) was not run ([paper/extended_report.md](../paper/extended_report.md), Appendix D).

## 4. Information actions and computation actions

An action "reveals the values of a fixed set of variables at a positive cost" ([src/msep/actions/base.py](../src/msep/actions/base.py)).

- An **information action** "reveals new external-world evidence" ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §4). "An information action must not perform reasoning that was already possible from E and C. Its defining property is that it changes what the agent knows about the external world."
- A **computation action** "transforms or verifies information already available" (PROBLEM_SPEC §5). "A computation action must **not reveal a previously hidden external-world variable**. This distinction is structural, not prompt-based."

The resource distinction, as revised on 2026-11-03 (PROBLEM_SPEC §5.1): ASK yields "new external-world evidence"; COMPUTE yields "a new derived, verified consequence of existing evidence".

**Why neither kind may reveal the other kind of fact.** The sources give the reason for one direction explicitly: "If a 'compute' action can reveal a hidden world variable, the information/computation distinction is invalid" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A10). For the other direction, the specification requires that an information action perform no reasoning (PROBLEM_SPEC §4, quoted above). If either rule failed, the resource class of a state (Section 7) would no longer say which kind of resource is needed (retrospective interpretation).

**How the separation is enforced.**

| Mechanism | What it guarantees | Source |
|---|---|---|
| Type check when a state is built | "information actions reveal only world variables, computation actions reveal only computed variables"; a violation raises an error | [src/msep/actions/base.py](../src/msep/actions/base.py); `FormalState.__post_init__` in [src/msep/world/state.py](../src/msep/world/state.py) |
| Signature of `execute` | A computation action "receives only the computation tasks (visible instance data). It has no access to the latent world" | [src/msep/actions/computation.py](../src/msep/actions/computation.py) |
| Information actions do no inference | `execute` "returns only the values of the variables the action reveals and performs no inference" | [src/msep/actions/information.py](../src/msep/actions/information.py) |
| Behavioural check | "Computation outcomes are identical in every consistent world (no leakage)": 24,256 checks, 0 failed | [results/oracle_validation.md](../results/oracle_validation.md), check `computation_outcome_world_invariant`; [tests/test_leakage.py](../tests/test_leakage.py) |

The specification also describes stochastic or multi-outcome information actions (PROBLEM_SPEC §4). In the implemented benchmark every action reveals the true values of a fixed set of variables. Noisy sources are outside this work ([paper/report.md](../paper/report.md), Appendix A).

## 5. Plans are chosen before any result is seen

"A static plan is a set of actions chosen before any result is seen" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F2). The benchmark text says the same to the model: "You are choosing a plan before running anything: actions are chosen together, before any result is seen" ([src/msep/benchmark/rendering.py](../src/msep/benchmark/rendering.py)).

Two consequences are recorded in the sources:

- Sufficiency is an ex-ante notion (Section 6). "'Sufficient in the actual world' (ex post) is recorded separately, for stopping analyses" (F2).
- If a prefix of a static plan already settles q in the actual world, continuing is "not an error for a static plan, which is chosen before outcomes are seen; it measures the saving that only an adaptive agent can take" (ASSUMPTIONS F9).

## 6. Guaranteed sufficiency

The definition used throughout ([paper/extended_report.md](../paper/extended_report.md), Appendix D):

> "Let 𝒜(S) be the assignments consistent with the rules and the known values of state S, and R(π) the variables that plan π reveals. π is *sufficient* iff there are no a, b ∈ 𝒜(S) with a(Q) ≠ b(Q) and a|R(π) = b|R(π). This is an ex-ante notion: the plan is fixed before any result is seen and must work for every outcome."

The same definition in words ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F2): a plan is sufficient "if, for every assignment consistent with the rules and the known values, the knowledge after revealing the plan's variables satisfies the decision rule. Equivalently: no q-true assignment and q-false assignment agree on everything known plus everything the plan reveals."

For the logical rule, the status of a state is defined by satisfiability ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §6): q is **entailed** if UNSAT(C ∧ E ∧ ¬q), **contradicted** if UNSAT(C ∧ E ∧ q), and **underdetermined** if both remain satisfiable. "High probability is not logical entailment" (same section; ASSUMPTIONS A9).

## 7. Cost, cheapest sufficient plans and the five resource classes

**Cost.** "Each action has a positive integer cost; a plan's cost is the sum. MSEP = a minimum-cost sufficient plan. With positive costs, every MSEP is inclusion-minimal" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F4). Costs are abstract units, "not time or money" ([paper/report.md](../paper/report.md), Appendix A).

**Three plan notions** ([src/msep/oracle/sufficiency.py](../src/msep/oracle/sufficiency.py)):

- *sufficient*: defined in Section 6;
- *inclusion-minimal*: sufficient, and "no proper subset is sufficient";
- *optimal* (the MSEP): sufficient, and "no sufficient plan is cheaper".

A state can have several optimal plans. On the benchmark, the number of optimal plans per resolvable instance is 1 for 1,952 instances, 2 for 26 and 4 for 4 ([results/audit_v3/benchmark_audit.md](../results/audit_v3/benchmark_audit.md) §4). Scoring accepts "any sufficient plan at optimal cost" ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §7).

**Resource classes** (ASSUMPTIONS F4; [paper/extended_report.md](../paper/extended_report.md), Appendix D):

| Class | Definition |
|---|---|
| ALREADY_SUFFICIENT | "the empty plan is sufficient" |
| NEITHER | "no plan over the available actions is sufficient" |
| INFORMATION_ONLY | otherwise, the optimal plans contain information actions only |
| COMPUTATION_ONLY | otherwise, the optimal plans contain computation actions only |
| BOTH | otherwise, the optimal plans contain at least one action of each kind |

Three qualifications are part of the definition:

- **NEITHER is relative to the action menu.** It "does not mean the question is metaphysically impossible. It means: no plan over the benchmark's currently available information and computation actions can make the decision sufficient under the stated criterion" (ASSUMPTIONS A6).
- **Ties across compositions are excluded.** A sixth label, AMBIGUOUS, is given "if optimal plans of different compositions tie on cost. These are excluded from the benchmark families" (F4).
- **Classes are required to survive a change of costs.** `class_cost_invariant` "records whether the class would survive any change of costs, meaning all inclusion-minimal plans have the same composition. The INFORMATION_ONLY, COMPUTATION_ONLY and BOTH family siblings are required to be cost-invariant. BOTH siblings also require both resources to be necessary" (F4).

"These are not merely model labels. They are derived from the exact environment and oracle" ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §2).

**Levels** (ASSUMPTIONS F6): Level 0 = ALREADY_SUFFICIENT; Level 1 = a single resource type (one or more actions); Level 2 = BOTH; Level 3 = NEITHER. Level 4 (conditional plans) is not implemented (Section 9).

## 8. Obligations and the hitting-set characterisation

**Definitions** ([paper/extended_report.md](../paper/extended_report.md), Appendix D):

> "A *distinguishing pair* is a, b ∈ 𝒜(S) with a(Q) ≠ b(Q). Its *difference set* is the set of unknown non-target variables on which they differ. An *obligation* is an inclusion-minimal difference set. An action *discharges* an obligation if it reveals one of its variables, or Q."

**Proposition and proof**, as given in the same appendix:

> "**Proposition.** Under logical entailment, π is sufficient iff it discharges every obligation. So an MSEP is a minimum-cost hitting set of the obligations, and a state is sufficient iff it has no obligations.
>
> *Proof.* If π misses an obligation D, the pair that D came from agrees on R(π) and disagrees on Q, so π is not sufficient. Conversely, if π is not sufficient, some distinguishing pair agrees on R(π); its difference set is disjoint from R(π) and contains a minimal difference set, which is an obligation that π misses. ∎"

The three facts the proposition states are also checked numerically, against exhaustive enumeration ([results/oracle_validation.md](../results/oracle_validation.md); details in [oracle_validation.md](oracle_validation.md)):

| Fact | Check | Passed / failed |
|---|---|---|
| "The current state is sufficient iff there are no obligations" | `no_obligations_iff_sufficient` | 12,034 / 0 |
| Obligation sets agree between SAT and enumeration | `obligations_sat_vs_brute` | 12,034 / 0 |
| A minimum-cost hitting set of the obligations is an optimal plan | `planner_optimal_cost` | 9,135 / 0 |
| No hitting set exists exactly on NEITHER | `planner_neither` | 2,899 / 0 |

**Obligation kinds** ([src/msep/obligations/model.py](../src/msep/obligations/model.py)), "by the variables that can discharge them": TRUTH (only world variables), COMPUTE (only computed variables), EITHER (either kind), TARGET ("no other variable can: only observing q itself helps").

**Relevance is weaker than sufficiency.** "An action is **relevant** if some possible outcome of it pins down a variable that appears in an obligation (or q). An action can be relevant yet in no sufficient plan" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F5; A7). In the code this means in no inclusion-minimal sufficient plan; adding an action to a sufficient plan keeps it sufficient. The oracle labels each action as `optimal`, `dominated` (in some inclusion-minimal sufficient plan, in no optimal one), `relevant_insufficient` or `irrelevant` ([src/msep/oracle/minimal_plan.py](../src/msep/oracle/minimal_plan.py)).

**Scope of the characterisation.** It holds for the logical rule only. Probabilistic sufficiency "is not monotone in information and the obligation-cover properties do not hold for it" ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §6).

The oracle is related to the logic of sufficient and necessary reasons for decisions; the report states that "that correspondence is our reading" ([paper/report.md](../paper/report.md), Section 2).

## 9. Decision rules: implemented, used, and only specified

"Sufficiency depends on the decision rule" and the rule must be declared for every instance ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) A8).

| Rule or plan type | Definition | Implemented | Used in the reported experiments | Source |
|---|---|---|---|---|
| **Logical entailment** | "the knowledge entails q or entails not-q" | Yes: SAT/MaxSAT oracle, brute force, obligation planner | Yes. "All benchmark families"; "Every result is about static plans under logical entailment" | ASSUMPTIONS F3; [paper/extended_report.md](../paper/extended_report.md), Appendix D |
| **Posterior threshold** τ ∈ (1/2, 1] | World variables have independent priors, conditioned on the rules. Uncomputed computed variables are handled in the worst case: "an answer d is justified iff P(q = d \| knowledge, c) ≥ τ for every consistent completion c" | Yes, in the oracle only: weighted model counting ([src/msep/oracle/probability.py](../src/msep/oracle/probability.py)) and enumeration. Validated in E0 (2,931 posterior instances; with τ = 1 it reproduces the logical rule on 12,034 instances, 0 failures). The planner used by EOP reports posterior-rule states as unsupported (ASSUMPTIONS F10) | No. "Not part of the core benchmark (decided 2026-11-03)". Risk variants exist (6,000 in [data/variants_v3_manifest.json](../data/variants_v3_manifest.json)); experiment E11 had no model run | ASSUMPTIONS F3; [results/oracle_validation.md](../results/oracle_validation.md); [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.14 |
| **Expected-utility threshold** | Given as an example: "ANSWER(q) is justified iff EU(ANSWER(q)\|S) ≥ τ" | No. `state.py` defines two rules only, `LogicalEntailment` and `PosteriorThreshold` | No | [PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §6; [src/msep/world/state.py](../src/msep/world/state.py) |
| **Conditional plans** (Level 4) | The next action depends on an earlier result. Primary objective "expected cost / expected utility over outcome branches"; worst-case cost "as a secondary robustness metric" (decided 2026-11-03) | No | No | PROBLEM_SPEC §12; ASSUMPTIONS F6, F6a |
| **Order-dependent actions** | "correct plan but wrong order" is listed among the distinctions the full benchmark must support | No. "The order-matters family is deferred to Level 4" | No | PROBLEM_SPEC §9; [src/msep/benchmark/families.py](../src/msep/benchmark/families.py) |

Two properties of the posterior rule are recorded and tested: "With τ = 1 and uniform priors this reproduces the logical rule exactly", and the rule "is **not monotone**: more information can make a justified decision unjustified. Plan search for it is exhaustive" (ASSUMPTIONS F3; [tests/test_sufficiency.py](../tests/test_sufficiency.py)).

The planner used by EOP also contains an execution loop that runs one action, adds the observation and re-plans ([src/msep/controllers/realistic_planner.py](../src/msep/controllers/realistic_planner.py), `run`). The reported experiments score its static plan only; see [eop_architecture.md](eop_architecture.md).

## 10. Worked example

The state is `G0a5c7e47d1-S04` from the train split. It is the example state of [paper/extended_report.md](../paper/extended_report.md), Appendix F. The obligations and action roles below are read from the stored oracle record of that state in `data/generated/pool_v3/instances.jsonl` (generated data, not in git; rebuilt by the command in [data/pool_v3_manifest.json](../data/pool_v3_manifest.json) and pinned by hash in [data/FREEZE_v3.json](../data/FREEZE_v3.json)).

```text
Decision: is it true that the experiment run is approved (Q)?

Facts about the world (each is true or false):
  F1: the waste bin was emptied
  F2: the freezer log was checked
  F3: the visitor list is closed
  F4: the protocol version is current
  F5: the safety officer signed off
Computational facts (each is fully determined by inputs shown here; its certified value is not yet known):
  K1: pow(92622104126, 48156954060, 236700561991) equals 49760859217

Rules (all of these are true):
  1. if F4 then not F3
  2. if F5 then F1
  3. Q if and only if not ((not F2 if and only if not K1) and not F3)

Known so far: nothing

Available actions:
  ASK_F1 (information, cost 4): find out the value of F1
  ASK_F2 (information, cost 1): find out the value of F2
  ASK_F3 (information, cost 3): find out the value of F3
  ASK_F4 (information, cost 4): find out the value of F4
  ASK_F5 (information, cost 4): find out the value of F5
  EXECUTE_CODE_K1 (computation, cost 3): run the certified procedure and record the value of K1
```

**Reading of rule 3.** Rule 3 is equivalent to "Q holds exactly when F3 is true or F2 and K1 have different values". This simplification was made for this document and is not in the sources.

**Obligations** (stored oracle record, field `obligations`):

| Obligation | Kind | Variables | Why it is an obligation (our gloss) | Actions that discharge it (field `obligation_discharge`) |
|---|---|---|---|---|
| O1 | truth | {F2} | With F3 false and K1 fixed, changing F2 alone changes Q | ASK_F2 |
| O2 | compute | {K1} | With F3 false and F2 fixed, changing K1 alone changes Q | EXECUTE_CODE_K1 |
| O3 | truth | {F3} | With F2 and K1 equal, changing F3 alone changes Q (with F4 false, rule 1 allows both values of F3) | ASK_F3 |

**Cheapest sufficient plan.** Each obligation has exactly one action that discharges it, so the only hitting set is {ASK_F2, ASK_F3, EXECUTE_CODE_K1}, with cost 1 + 3 + 3 = 7. The stored record gives the same: one optimal plan, optimal cost 7, and one inclusion-minimal sufficient plan. The class is **BOTH**. The record's `necessity` field says that information is necessary, computation is necessary, and the class is cost-invariant.

**Roles of the other actions** (field `actions`):

| Action | Category | Reason |
|---|---|---|
| ASK_F4 (cost 4) | `relevant_insufficient` | By rule 1, the outcome "F4 is true" pins F3 to false, so the action is relevant. It is in no inclusion-minimal sufficient plan (`in_minimal_plan` is false), and it is not sufficient alone |
| ASK_F1, ASK_F5 (cost 4 each) | `irrelevant` | F1 and F5 occur only in rule 2, which is not connected to Q |

This state shows the three distinctions the task draws: an action can be relevant and still not sufficient (ASK_F4); a sufficient plan must hit every obligation, here with both kinds of resource; and among sufficient plans only the cheapest counts as optimal.

A shorter example with the same structure opens [paper/report.md](../paper/report.md), Section 1 and Section 3.1: knowing nothing gives BOTH with plan {ask, checksum} at cost 4, "not {audit, checksum} at cost 6". More scored examples, with model answers, are in [docs/EXAMPLES.md](../docs/EXAMPLES.md).

## 11. What the formal model does not cover

Stated limits, from [ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F7 and F11 and [paper/extended_report.md](../paper/extended_report.md), Appendix D:

- "Worlds are small (up to 16 variables for brute force), so exactness is cheap and scaling claims are not yet tested."
- "Not implemented. Conditional plans (the next action depends on an earlier result), order-dependent actions, and the posterior-threshold decision rule in the benchmark."
- "A model can still guess a computed value and answer directly. End-to-End scoring shows this as a detection error, and the decision is then correct only by chance on computed facts."
- Normative resolvability is not agent capability: the oracle defines whether "a valid computation exists in the environment", not whether "the evaluated model can successfully perform that computation" (ASSUMPTIONS A3).

The full list of limitations is in [limitations.md](limitations.md).
