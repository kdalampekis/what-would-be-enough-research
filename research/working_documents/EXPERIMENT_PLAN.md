# EXPERIMENT_PLAN.md
# Experimental Plan — What Would Be Enough?

**Primary object:** Minimal Sufficient Epistemic Plan (MSEP)  
**Primary mode:** Detection-Controlled  
**Secondary modes:** End-to-End and Diagnosis-Controlled

---

## 1. Goals

The experiments should answer four questions:

1. Do LLMs recognize when a state is insufficient?
2. Given that insufficiency is known, can they diagnose the required resource class?
3. Can they construct the minimal sufficient plan?
4. Can an explicit Epistemic Obligation Planner reduce failure and resource waste?

The project should produce both:

- a **benchmark / study**;
- a **mitigation / controller**.

---

## 2. Main hypotheses

### H1 — Detection is not the whole problem
Models will perform better in Detection-Controlled mode than End-to-End mode, but substantial planning error will remain.

### H2 — Resource diagnosis is easier than exact planning
Models may correctly identify `INFORMATION_ONLY`, `COMPUTATION_ONLY`, `BOTH`, or `NEITHER` while still selecting an insufficient or wasteful plan.

### H3 — Sufficiency is harder than relevance
Models will often choose interventions that are semantically relevant but do not actually make the decision sufficient.

### H4 — BOTH is a major failure regime
Models will perform disproportionately worse on instances requiring mixed information + computation than on single-resource instances.

### H5 — Minimality and stopping are distinct
Even when models find a sufficient plan, they may over-consume resources or continue acting after sufficiency is achieved.

### H6 — Explicit epistemic obligations help
An obligation-guided planner will reduce insufficient actions, premature stopping, and excess resource cost relative to confidence-based and generic routing baselines.

---

## 3. Experimental modes

### A. End-to-End
Prompt does not reveal whether the state is sufficient.

Measures the full chain:

`Detection -> Diagnosis -> Planning -> Control`

### B. Detection-Controlled
Prompt explicitly states that the current state is insufficient.

Measures:

`Diagnosis -> Planning -> Control`

This is the **primary confirmatory mode**.

### C. Diagnosis-Controlled
Prompt explicitly provides the correct resource class.

Measures:

`Planning -> Sufficiency -> Control`

This is the cleanest test of the novel capability.

---

## 4. Benchmark families

Each base scenario should generate matched siblings that differ minimally.

At minimum:

1. `ALREADY_SUFFICIENT`
2. `INFORMATION_ONLY`
3. `COMPUTATION_ONLY`
4. `BOTH`
5. `NEITHER`
6. relevant-but-insufficient information action
7. relevant-but-insufficient computation action
8. sufficient but expensive plan
9. cheaper sufficient alternative
10. plan where action order matters
11. state where one extra action is unnecessary
12. state where early stopping is premature

All siblings from a base scenario must stay in the same train/dev/test split.

---

## 5. Core experiments

### E0 — Oracle validation
No LLMs.

Validate:
- SAT/SMT vs brute-force enumeration;
- posterior normalization;
- action effects;
- sufficiency;
- minimality;
- plan cost;
- resource class.

**Blocker:** do not proceed unless exact small-world agreement is 100%.

### E1 — Base decision competence
Give models already-sufficient instances.

Measure whether they can answer the underlying task.

Purpose: distinguish task incompetence from epistemic-planning failure.

### E2 — Uncertainty / insufficiency detection
End-to-End only.

Measure:
- sufficient vs insufficient classification;
- over-answering;
- unnecessary intervention.

### E3 — Resource-class diagnosis
Detection-Controlled.

Classes:
- INFORMATION_ONLY
- COMPUTATION_ONLY
- BOTH
- NEITHER

Primary metric: macro-F1 and balanced accuracy.

### E4 — Exact intervention targeting
Given a known resource class, can the model identify the correct specific action(s)?

Examples:
- which variable to ask;
- which proof obligation to verify;
- which posterior to compute.

### E5 — Sufficiency discrimination
Matched pairs where an intervention is:
- relevant + sufficient;
- relevant + insufficient.

Measure whether models distinguish them.

This is one of the highest-priority experiments.

### E6 — Minimality
Give multiple sufficient plans with different costs / sizes.

Measure whether the model selects a minimal sufficient plan.

### E7 — BOTH cases
Require at least one information and one computation action.

Subconditions:
- set sufficient, order irrelevant;
- order matters;
- one action reveals which computation is needed;
- computation reveals which information question is decisive.

### E8 — NEITHER cases
No available plan can make the decision sufficient.

Measure:
- inappropriate persistence;
- hallucinated actions;
- premature answer;
- correct defer/abstain.

### E9 — Stopping
Evaluate whether models stop:
- too early;
- exactly at sufficiency;
- too late.

Primary metric: excess actions after first sufficient state.

### E10 — Cost sensitivity
Keep epistemic structure fixed while varying action costs.

Test whether selected plan changes at the correct boundary.

### E11 — Risk sensitivity
Vary wrong-answer penalty / decision threshold.

Test whether models change plan or defer when justified.

### E12 — Structural distribution shift
Train/dev:
- shallow logic;
- small graphs;
- known templates.

Test:
- deeper chains;
- larger graphs;
- branching;
- unseen linguistic skins.

### E13 — External validation
After the synthetic benchmark is stable:
- ProofWriter transformations;
- FOLIO transformations;
- probability / uncertainty transfer tasks where appropriate.

Synthetic exact benchmark remains primary.

---

## 6. Baselines

At minimum:

1. Always ANSWER
2. Always ASK
3. Always COMPUTE
4. Always DEFER
5. Random resource class
6. Confidence-threshold policy
7. Self-consistency gate
8. Ask-vs-think heuristic
9. Information-only planner
10. Computation-only planner
11. Generic learned router
12. Native LLM structured prompt
13. Epistemic Obligation Planner
14. Oracle

---

## 7. Output schema

Do not require hidden chain-of-thought.

Use structured outputs such as:

```json
{
  "state_sufficient": false,
  "resource_class": "BOTH",
  "plan": [
    {"type": "ASK", "target": "A"},
    {"type": "COMPUTE", "target": "VERIFY_P2"}
  ],
  "stop_after_plan": true,
  "confidence": 0.74,
  "short_justification": "A is unknown; after observing it, P2 must be verified."
}
```

The benchmark should score fields, not prose quality.

---

## 8. Metrics

### Primary metrics
- Resource-Class Accuracy
- Plan Exact Match
- Plan Sufficiency Rate
- Minimality Rate
- Premature Stop Rate
- Excess Action Rate
- Final Decision Accuracy
- Net Utility / Cost
- Epistemic Action Regret

### Hierarchical metrics
Let:
- \(A_D\): detection accuracy
- \(A_G\): diagnosis accuracy conditional on known insufficiency
- \(A_P\): plan accuracy conditional on correct diagnosis
- \(A_S\): sufficiency accuracy
- \(A_{E2E}\): end-to-end optimal behavior

Report these separately.

### Plan regret
For selected plan \(\pi_m\):

\[
Regret = V(\pi^*) - V(\pi_m)
\]

where \(\pi^*\) is the oracle plan.

---

## 9. Statistical design

- split by scenario family, never by row;
- use deterministic seeds;
- preregister primary hypotheses and metrics before final run;
- cluster bootstrap confidence intervals by family;
- paired permutation or McNemar tests for matched-pair comparisons;
- Holm correction across confirmatory hypotheses;
- report effect sizes, not only p-values;
- separate exploratory from confirmatory analyses.

---

## 10. Model protocol

Use 3–4 model families, not one model.

Recommended categories:
- frontier reasoning model;
- frontier general model;
- strong mid-size model;
- cheaper/smaller model.

Primary run:
- temperature 0 or deterministic equivalent;
- pinned model versions.

Robustness subset:
- 100–200 scenarios;
- 5 stochastic runs per model;
- compute-budget matched where relevant.

---

## 11. Sample sizes

### Pilot
- 100 base families
- 5–8 siblings each
- ~500–800 instances
- 2 models

Goal:
- validate signal direction;
- find broken generator assumptions;
- identify ceiling/floor effects.

### Main
- 400–600 base families
- ~2,000–3,500 instances
- 3–4 model families

Priority:
strong design > many models.

---

## 12. Solution experiments

### S1 — Structured prompt only
Ask the model to explicitly report:
- unresolved obligations;
- candidate resources;
- why each is sufficient/insufficient;
- proposed plan.

### S2 — Obligation extraction + deterministic checker
LLM proposes obligations; exact checker verifies candidate actions.

### S3 — Epistemic Obligation Planner
Formal planner finds minimal sufficient plan from verified obligations/action effects.

### S4 — Hybrid planner
LLM estimates uncertain action effects where the formal environment does not know them; planner performs cost-aware optimization.

### S5 — Shift robustness
Compare learned router vs obligation planner under:
- new costs;
- deeper graphs;
- new templates;
- new domains.

Main mitigation claim should be based on reduction in:
- plan insufficiency;
- premature stopping;
- excess resource cost;
- decision regret.

---

## 13. Success criteria

A strong result is any one of:

1. models detect insufficiency but fail to identify sufficient plans;
2. models classify resource type correctly but fail at targeting;
3. models confuse relevance with sufficiency;
4. BOTH cases expose a large systematic failure;
5. models stop too early or continue too long;
6. obligation-guided planning materially reduces regret/cost.

A null result can still be publishable if:
- benchmark is exact and hard;
- frontier models succeed robustly;
- failures emerge only under shift, cost, or sequential conditions;
- capability boundaries are carefully mapped.

---

## 14. Execution order

1. Formal environment
2. Exact oracle
3. Oracle validation
4. E1, E3, E5, E7 pilot
5. End-to-End E2
6. E6, E8, E9
7. Cost/risk/shift experiments
8. Solution S1–S4
9. External validation
10. Frozen held-out final evaluation
11. Write-up

Do not begin expensive model experiments before oracle validation passes.
