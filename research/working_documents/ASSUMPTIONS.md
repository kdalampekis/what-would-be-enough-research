# ASSUMPTIONS.md
# Assumptions, Guardrails, and Failure-Interpretation Rules

This file exists to prevent invalid conclusions.

---

## A1. Uncertainty detection is a separate capability

The project must never infer:

> “The model cannot construct a sufficient plan”

solely from an End-to-End failure.

A model may answer immediately because it failed to recognize that the state is insufficient.

Therefore all central claims must be supported by:

- Detection-Controlled evaluation;
- and, where relevant, Diagnosis-Controlled evaluation.

---

## A2. Detection, diagnosis, planning, and control are different

A failure can occur at different levels:

1. **Detection failure**  
   Model does not recognize insufficiency.

2. **Diagnosis failure**  
   Model recognizes insufficiency but predicts wrong resource class.

3. **Targeting failure**  
   Correct resource class, wrong specific action.

4. **Sufficiency failure**  
   Selected action is relevant but not enough.

5. **Minimality failure**  
   Plan is sufficient but unnecessarily expensive/long.

6. **Ordering failure**  
   Correct actions, wrong sequence.

7. **Stopping failure**  
   Stops before sufficiency or continues after sufficiency.

Do not collapse these into one “action accuracy” number.

---

## A3. More computation does not guarantee correctness

Even when all external facts are available, a model may still fail due to capability limits.

Therefore distinguish:

- **normative resolvability** — a valid computation exists in the environment;
- **agent capability** — the evaluated model can successfully perform that computation.

The benchmark oracle defines the former.

---

## A4. More information does not guarantee correctness

Additional external facts can be:

- irrelevant;
- redundant;
- noisy;
- insufficient;
- misleading under poor reasoning.

Therefore ASK is not equivalent to improvement.

---

## A5. Information and computation are not mutually exclusive

The benchmark must include:
- INFORMATION_ONLY;
- COMPUTATION_ONLY;
- BOTH;
- NEITHER.

Do not frame the problem as a binary ASK-vs-COMPUTE classification.

---

## A6. “Neither” means unavailable under the action space

`NEITHER` does not mean the question is metaphysically impossible.

It means:

> no plan over the benchmark's currently available information and computation actions can make the decision sufficient under the stated criterion.

The action space must be explicit.

---

## A7. Relevance is not sufficiency

An intervention can be topically relevant but fail to resolve the blocking uncertainty.

The benchmark must include matched relevant/sufficient vs relevant/insufficient cases.

---

## A8. Sufficiency depends on the decision rule

Logical entailment and probabilistic decision sufficiency are different.

The benchmark must explicitly declare whether sufficiency means:
- logical entailment;
- logical contradiction;
- posterior threshold;
- expected-utility threshold;
- another formal rule.

Never infer sufficiency from model confidence.

---

## A9. High probability is not entailment

A proposition may have:

\[
P(q \mid E)=0.99
\]

while both \(q\) and \(\neg q\) remain logically possible.

Do not treat probability near 1 as proof.

---

## A10. Computation actions cannot reveal hidden external facts

This must be enforced by environment design.

If a “compute” action can reveal a hidden world variable, the information/computation distinction is invalid.

---

## A11. Natural language is not ground truth

Formal state is generated first.

Language rendering is downstream.

Paraphrasing must not change:
- latent world;
- constraints;
- action effects;
- oracle plan;
- sufficiency label.

---

## A12. Exact oracle before LLM evaluation

For small worlds:
- brute-force enumeration;
- solver-based oracle.

They must agree exactly.

Any mismatch is a blocker.

---

## A13. Family-level splitting

All counterfactual siblings from the same base scenario stay in the same split.

Random row splitting is prohibited.

---

## A14. Avoid circular evaluation

Do not use the same LLM:
- to generate labels;
- to judge labels;
- and to be evaluated on those labels.

Where LLM-based rendering or judging is unavoidable, keep the exact formal oracle authoritative.

---

## A15. Cost model must be explicit

Minimality has no meaning without cost.

Possible costs:
- number of actions;
- normalized resource cost;
- token cost;
- API/tool calls;
- wall-clock;
- task-specific interruption cost.

Primary experiments should use a simple normalized cost model; realistic cost analyses can be secondary.

---

## A16. Static sets and sequential plans are different

A minimum action set is not always enough.

If outcomes affect the next action, use a conditional plan/policy.

Do not pretend a static MaxSAT formulation solves a sequential stochastic planning problem.

---

## A17. MaxSAT/SMT is an implementation option, not the contribution

The benchmark's novelty cannot depend on the choice of solver.

Use brute force / SAT / MaxSAT / SMT / DP according to the environment structure.

---

## A18. No “first ever” claim without a final literature check

The 2026 literature is moving quickly.

Before submission:
- repeat literature search;
- check new October/November arXiv papers;
- update NOVELTY_MAP.md.

Use bounded wording such as:
> “We did not find prior work that evaluates this exact combination…”

unless stronger evidence exists.

---

## A19. Prior work is not “solved”

Do not say calibration, abstention, retrieval, compute allocation, or uncertainty diagnosis are solved problems.

Say:
> prior work has made substantial progress on these components, motivating a deeper integrated evaluation.

---

## A20. Primary interpretation rule

The core scientific statement should be based on controlled conditions:

> Given that the state is known to be insufficient, can the model identify and construct a minimal sufficient epistemic plan?

End-to-End results are important for ecological validity, but they are not the sole basis for the central claim.

---

# Phase 1 formal semantics (implementation decisions, 2026-11-03)

These are the exact definitions the Phase 1 code implements. They make the
assumptions above concrete; where a choice was needed, it is stated here.

## F1. Two kinds of unknowns (revised 2026-11-03)
- **World variables** are contingent external facts. Only information actions (ASK) reveal them, by reading the latent world.
- **Computed variables** are the results of **certified computations or verifications** on inputs the agent already has. COMPUTE means running a certified procedure such as code execution, a primality test, a SAT solver or an exact posterior calculation. Before that, the certified result is not part of the decision state. The inputs are known; the certified result is not.
- A computation action reads only task data, never the world (A10). Its result is a fixed function of visible inputs.
- Benchmark families use only tasks that are impractical to do mentally (`world/certified_tasks.py`), so "the model could just calculate it" is not the dominant shortcut.
  - Simple kinds (two-digit divisibility, short sums, tiny syllogisms) remain only in the random oracle-validation instances, where task difficulty plays no role.
- Until its certified result exists, a computed variable is unknown in the decision state, although it has a fixed true value (logical uncertainty).

## F2. Sufficiency is ex ante (static plans)
- A static plan is a set of actions chosen before any result is seen.
- It is **sufficient** if, for every assignment consistent with the rules and the known values, the knowledge after revealing the plan's variables satisfies the decision rule. Equivalently: no q-true assignment and q-false assignment agree on everything known plus everything the plan reveals.
- "Sufficient in the actual world" (ex post) is recorded separately, for stopping analyses.

## F3. Decision rules
- **Logical entailment** (all benchmark families): the knowledge entails q or entails not-q.
- **Posterior threshold** τ ∈ (1/2, 1]. **Not part of the core benchmark** (decided 2026-11-03). It is validated in E0 and will be introduced only as a separate stress test in E11:
  - World variables have independent priors, conditioned on the rules.
  - Uncomputed computed variables are handled in the worst case: an answer d is justified iff P(q = d | knowledge, c) ≥ τ for every consistent completion c.
  - With τ = 1 and uniform priors this reproduces the logical rule exactly; E0 checks this on every logical instance.
  - This rule is **not monotone**: more information can make a justified decision unjustified. Plan search for it is exhaustive.

## F4. Cost, minimality, class
- Each action has a positive integer cost; a plan's cost is the sum. MSEP = a minimum-cost sufficient plan. With positive costs, every MSEP is inclusion-minimal.
- **Resource class:**
  - ALREADY_SUFFICIENT if the empty plan is sufficient.
  - NEITHER if no plan over the available actions is sufficient (A6).
  - Otherwise, the shared composition of the optimal plans.
  - AMBIGUOUS if optimal plans of different compositions tie on cost. These are excluded from the benchmark families.
- `class_cost_invariant` records whether the class would survive any change of costs, meaning all inclusion-minimal plans have the same composition. The INFORMATION_ONLY, COMPUTATION_ONLY and BOTH family siblings are required to be cost-invariant. BOTH siblings also require both resources to be necessary.

## F5. Obligations and relevance
- Under the logical rule, an **obligation** is a minimal set of unknown variables on which some q-true and q-false consistent assignments differ. Revealing any of its variables, or q itself, discharges it.
- A plan is sufficient iff it discharges every obligation, so the MSEP is a minimum-cost hitting set.
- An action is **relevant** if some possible outcome of it pins down a variable that appears in an obligation (or q). An action can be relevant yet in no sufficient plan; that is the A7 case.

## F6. Levels
- Level 0 = ALREADY_SUFFICIENT; Level 1 = a single resource type (one or more actions); Level 2 = BOTH; Level 3 = NEITHER.
- Level 4 (conditional plans) and the order-matters family are not implemented yet (A16).

## F6a. Level 4 objective (decided 2026-11-03)
- For conditional plans, the primary oracle minimises **expected cost** (expected utility) over outcome branches, under the declared world prior.
- **Worst-case cost** is reported as a secondary robustness metric.

## F7. Known limitations of Phase 1
- Worlds are small (up to 16 variables for brute force), so exactness is cheap and scaling claims are not yet tested.
- (Revised 2026-11-03.) COMPUTE is defined as certified computation (F1), and benchmark tasks are hard to do mentally. A model can still guess a computed value and answer directly. End-to-End scoring shows this as a detection error, and the decision is then correct only by chance on computed facts.
- The family template has one fixed structure (two world requirements, one or two computed requirements, one alias, two one-way decoys, two distractors). Structural shift (E12) needs further templates.
- Rendering uses three simple skins. Linguistic shift is untested.

## F8. Family template v2 and the shortcut residual (2026-11-04)
- **The problem.** A lookup probe on prompt surface counts predicted the resource class at 86–90% on pool_v1 (baseline 50%). That pool is superseded.
- **Template v2** randomises, independently of the sibling type:
  - which redundant actions are offered;
  - six distractor variables (three of each kind) with rules of the same shape as the decoys, each known with probability 1/2 and offered with probability 1/2;
  - whether an uninformative decoy is shown as known.
- **Result.** The probe drops to 56–69%.
- **The residual is partly inherent.** The class is defined by which *relevant* variables are unknown, so counts by kind carry some signal. The probe is reported as a baseline beside every diagnosis result.
- **Not done:** exactly balanced counts across classes.

## F9. Stopping semantics for static plans (E9)
- **Premature stop:** the plan, executed in the actual world, leaves the decision unjustified while the agent says it will stop after the plan. Abstaining (no plan, NEITHER, defer) is not a premature stop.
- **Continuing after ex-post sufficiency:** an earlier prefix of the plan already settled q in the actual world. This is not an error for a static plan, which is chosen before outcomes are seen; it measures the saving that only an adaptive agent can take. Read it against the oracle agent's own value.

## F10. Oracle planner vs realistic planner
- **(A) `controllers/obligation_planner.py`** receives the exact formal state and the instance. It is a validation path of the oracle, never a mitigation.
- **(B) `controllers/realistic_planner.py`** receives only the prompt text and an environment whose `execute()` returns observations. Tests check:
  - its module imports no oracle or hidden-state code;
  - it runs against an environment that exposes nothing else.
- **With the rule-based parser, (B) is exact on this benchmark, because the rendering is regular** (round-trip verified). That condition is a tool-use upper bound. The mitigation question is (B) with an LLM extractor, not yet evaluated.
- **(B) supports only the logical rule.** Posterior-rule (E11) states are reported as unsupported.

## F11. Additional limitations (2026-11-04)
- E13 converts only to information actions; certified computation over external theories is not defined.
- The structural-shift axes are limited to width (a third requirement), depth (one level of indirection) and one held-out skin.
- Learned-router and confidence-threshold baselines need model outputs, so they are not implemented yet.

## F12. Template v3 and the adversarial audit (2026-11-04)
- **What the independent audit found.** Template v2 is solved 100% by reading only the rule that defines q. Rule order, rule signs and costs also leaked roles, and decoy rules copied hidden and certified values.
- **v2's role now.** It is a shallow subset, used only for the v2 → v3 structural-shift comparison.
- **v3 theories** are random, from four motifs (and/or, parity, threshold, case split), with optional indirection, bridges, mixed routes and bulk actions.
- **Unbiased sibling sampling.** States are drawn from one class-independent distribution and binned by the oracle. Nothing is selected by any agent's behaviour.
- **Leak fixes:**
  - implication signs are random, made true through the antecedent;
  - rule order is shuffled per family with a stored seed;
  - costs are random.
- **Certified tasks version 2:**
  - modpow with a prime modulus;
  - primes and semiprimes from the same size distribution;
  - posterior with sixteen observations at a 0.0002–0.0015 margin.

  The audit's mental shortcuts score at chance on them.
- **Residual.** A heuristic that resolves every unknown input of q's definition (one level of expansion) still gets about 50% optimal plans. Hence the `heuristic_hard` stratum (PROTOCOL §4).
- **Agent-side states hold opaque tasks.** They cannot be evaluated, so a planner obtains certified results only by running computation actions.
