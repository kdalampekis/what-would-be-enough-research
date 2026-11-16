# PROBLEM_SPEC.md
# What Would Be Enough?
## Minimal Sufficient Epistemic Planning for LLM Agents

**Status:** research specification  
**Track:** Apart Research — AI x Epistemics Sprint, Track 1: Model Epistemics & Decision-Making Evals  
**Literature cutoff used for positioning:** 2026-11-02

---

## 1. Core research question

> **When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?**

The benchmark must evaluate this question without conflating it with the already-separate problem of whether the model recognizes its own uncertainty.

The project therefore separates:

1. **Detection** — does the model recognize that the current state is not sufficient?
2. **Diagnosis** — what class of epistemic resource is needed?
3. **Planning / targeting** — which exact information and/or computation is needed?
4. **Sufficiency** — would the proposed intervention actually be enough?
5. **Control / stopping** — should the model execute the plan, answer now, or defer?

The scientific target is primarily stages 2–5, while stage 1 is measured separately.

---

## 2. High-level epistemic classes

For an unresolved state, the latent resource class is one of:

- **INFORMATION_ONLY** — one or more external observations are required.
- **COMPUTATION_ONLY** — all necessary external information is already present, but one or more internal computations / verifications are required.
- **BOTH** — resolution requires at least one information action and at least one computation action.
- **NEITHER** — no available information/computation plan can make the decision sufficiently justified under the environment's action space.

For end-to-end evaluation, add:

- **ALREADY_SUFFICIENT** — the current state already justifies the decision.

These are not merely model labels. They are derived from the exact environment and oracle.

---

## 3. State definition

Represent a benchmark state as:

\[
S = (W, E, C, M, q, \mathcal{I}, \mathcal{K}, U)
\]

where:

- \(W\): latent external world.
- \(E\): currently observed evidence.
- \(C\): logical / structural constraints.
- \(M\): bounded computational state of the agent/environment.
- \(q\): target proposition or decision.
- \(\mathcal{I}\): available information-acquisition actions.
- \(\mathcal{K}\): available computation / verification actions.
- \(U\): utility / cost model.

The state must be machine-verifiable and independent of natural-language rendering.

---

## 4. Information actions

An information action \(i \in \mathcal{I}\) reveals new external-world evidence.

Examples:

- ASK whether \(A\) is true.
- Observe a hidden variable.
- Query a source for a missing fact.
- Request a user preference required to determine a decision.

An information action must not perform reasoning that was already possible from \(E\) and \(C\). Its defining property is that it changes what the agent knows about the external world.

For stochastic or multi-outcome information actions:

\[
i: S \rightarrow \{(o_1, S_1), \ldots, (o_n, S_n)\}
\]

with outcome probabilities where appropriate.

---

## 5. Computation actions

A computation action \(k \in \mathcal{K}\) transforms or verifies information already available.

Examples:

- run a SAT/SMT solver;
- verify a proof obligation;
- compute a posterior;
- perform a numerical calculation;
- run a bounded search;
- execute code over known data;
- evaluate a derived constraint.

A computation action must **not reveal a previously hidden external-world variable**.

This distinction is structural, not prompt-based.

### 5.1 Definition of COMPUTE (revised 2026-11-03)

**COMPUTE represents certified computation or verification whose result is not yet part of the agent's decision state.**

- A COMPUTE action is a procedure such as `RUN_SOLVER`, `VERIFY_PROOF`, `EXECUTE_CODE`, `RUN_PRIMALITY_TEST` or `COMPUTE_POSTERIOR`.
- Its inputs may already be known. What is missing is the certified result.
- Plans are evaluated **before** any action is executed.
- The resource distinction is therefore:

\[ \text{ASK} \Rightarrow \text{new external-world evidence} \qquad \text{COMPUTE} \Rightarrow \text{a new derived, verified consequence of existing evidence} \]

- Benchmark computation tasks are chosen so that doing them mentally while choosing actions is not the dominant shortcut: modular exponentiation with 10–12 digit numbers, primality of 13–14 digit numbers, satisfiability of random 3-CNF near the threshold, and exact naive-Bayes posteriors compared to a threshold within 0.04. Trivial tasks (such as two-digit divisibility) are not used in benchmark families.

---

## 6. Sufficiency

A state is decision-sufficient when the benchmark's decision criterion is satisfied.

For a deterministic logical target:

- **entailed** if \(UNSAT(C \land E \land \neg q)\);
- **contradicted** if \(UNSAT(C \land E \land q)\);
- **underdetermined** if both remain satisfiable.

**Scope (decided 2026-11-03):** the core benchmark uses deterministic logical sufficiency only. Probabilistic (posterior-threshold) sufficiency is a separate stress test in E11, because it is not monotone in information and the obligation-cover properties do not hold for it.

For probabilistic decisions, define an explicit decision threshold / utility rule. For example:

\[
ANSWER(q) \text{ is justified iff } EU(ANSWER(q)\mid S) \ge \tau
\]

The exact criterion must be declared in the instance metadata.

**Important:** high probability is not logical entailment.

---

## 7. Minimal Sufficient Epistemic Plan (MSEP)

A plan \(\pi\) is an ordered sequence or conditional policy over information and computation actions.

A plan is **sufficient** if every reachable terminal branch satisfies the benchmark's decision-sufficiency criterion, or reaches an allowed defer/abstain terminal state when resolution is impossible.

A plan is **minimal** if no strictly cheaper valid plan achieves the same sufficiency target under the defined cost model.

For static deterministic cases:

\[
\pi^*(S) = \arg\min_{\pi \in \Pi(S)} Cost(\pi)
\]

subject to:

\[
S \xrightarrow{\pi} S' \quad \land \quad S' \text{ is decision-sufficient}.
\]

For conditional plans, use expected cost / expected utility over branches.

The oracle should expose:

- resource class;
- one or more optimal MSEPs;
- all minimal sufficient plans where tractable;
- plan cost;
- why each selected action is necessary;
- which candidate actions are irrelevant, insufficient, dominated, or unnecessary.

---

## 8. Epistemic obligation representation

The benchmark should represent unresolved requirements as **epistemic obligations**.

Examples:

- `O1: truth(A) unresolved`
- `O2: entailment(B -> C) unverified`
- `O3: posterior(q) relative to threshold unknown`

Candidate actions can discharge obligations:

- `ASK(A)` discharges `O1`;
- `VERIFY(B -> C)` discharges `O2`;
- `COMPUTE_POSTERIOR(q)` discharges `O3`.

The proposed mitigation will use this representation explicitly.

---

## 9. Why ASK vs COMPUTE is not the final research question

`ASK vs COMPUTE` is only a controlled diagnostic slice.

The full benchmark must support:

- information only;
- computation only;
- both;
- neither;
- already sufficient.

It must also distinguish:

- correct resource class but wrong concrete action;
- relevant action but insufficient action;
- sufficient but non-minimal plan;
- correct plan but wrong order;
- correct plan with premature stopping;
- unnecessary extra actions after sufficiency is achieved.

---

## 10. Three evaluation modes

### Mode A — End-to-End

The model receives the state and must decide whether to:

- answer now;
- acquire information;
- compute/verify;
- use a mixed plan;
- defer.

This measures realistic behavior but mixes uncertainty detection with later abilities.

### Mode B — Detection-Controlled

The model is explicitly told:

> The current state is not yet sufficient to justify a reliable decision.

This removes the uncertainty-detection confound.

The model must determine:

- information only;
- computation only;
- both;
- neither;
- and construct the plan.

This is the **primary benchmark mode**.

### Mode C — Diagnosis-Controlled

The model is additionally given the correct high-level resource class.

Example:

> Resolving this state requires both additional information and additional computation.

The model must identify the **minimal sufficient plan**.

This isolates planning / targeting / sufficiency ability from detection and diagnosis.

---

## 11. Exact oracle requirements

The benchmark oracle must be independent of the evaluated LLM.

For small formal worlds:

- use exhaustive enumeration as a gold validation path;
- use SAT/SMT or equivalent solver for scalable exact reasoning;
- compare both wherever feasible.

The oracle must compute:

- current epistemic status;
- posterior where applicable;
- available information outcomes;
- available computation effects;
- sufficiency of each candidate action;
- sufficiency of candidate sets/sequences;
- minimal plans;
- cost / utility;
- unresolvable states.

No LLM may be used as the authoritative oracle.

---

## 12. Static and sequential difficulty levels

### Level 0 — Already sufficient
No intervention required.

### Level 1 — Single intervention
Exactly one information or one computation action is sufficient.

### Level 2 — Mixed minimal set
At least one information and one computation action are jointly required.

### Level 3 — Neither
No available plan can resolve the decision.

### Level 4 — Conditional sequence
The optimal next step depends on the outcome of a prior action.

The first implementation should solve Levels 0–3 exactly before Level 4.

**Level 4 oracle (decided 2026-11-03):** the primary objective for conditional plans is **expected cost / expected utility** over outcome branches, continuing VOI/VOC and decision-theoretic metareasoning. Worst-case cost is reported as a secondary robustness metric, so that a rare expensive branch cannot turn the benchmark into a robust-planning problem.

---

## 13. Solver choice

The research contribution is **not** a particular solver.

Potential exact implementations include:

- brute-force enumeration;
- SAT;
- Weighted MaxSAT;
- SMT Optimize;
- shortest-path / dynamic programming;
- contingent planning.

Weighted MaxSAT / SMT may be useful for minimum-cost static plans, but should only be adopted if the formalization fits cleanly.

Do not force the benchmark around MaxSAT merely because it is convenient.

---

## 14. Proposed mitigation

### Epistemic Obligation Planner

Pipeline:

1. model or parser constructs the current formal state;
2. unresolved epistemic obligations are identified;
3. candidate information/computation actions are generated;
4. the formal layer checks which obligations each action can discharge;
5. a planner searches for a minimum-cost sufficient plan;
6. the agent executes only the selected plan;
7. after each step, sufficiency is re-evaluated;
8. execution stops immediately when sufficient;
9. if no plan exists, defer/abstain.

The intervention should be compared against:

- native LLM;
- confidence thresholding;
- ask-vs-think heuristic;
- generic learned router;
- information-only planner;
- compute-only planner;
- oracle.

---

## 15. Primary scientific claim boundary

Do **not** claim:

- uncertainty detection is new;
- abstention is new;
- adaptive retrieval is new;
- adaptive compute is new;
- retrieve-vs-think is new;
- minimal sufficient information is new;
- minimal sufficient computation is new;
- counterfactual action utility is new;
- epistemic planning is new.

Candidate contribution:

> A controlled benchmark for whether LLMs can identify **minimal sufficient epistemic plans across heterogeneous information and computation resources**, including mixed and unresolvable cases, while separating uncertainty detection from diagnosis and planning.

This is the claim to stress-test continuously against new literature.
