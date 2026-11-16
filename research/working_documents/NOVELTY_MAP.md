# NOVELTY_MAP.md
# Literature Boundary and Candidate Contribution

**Positioning cutoff:** 2026-11-02  
**Purpose:** prevent accidental novelty overclaiming.

---

## 1. What is already heavily studied

### Uncertainty / confidence / calibration
Prior work evaluates whether LLM confidence tracks correctness, whether uncertainty can be elicited, and whether semantic/token-level uncertainty predicts errors.

**Not our novelty.**

### Abstention / selective prediction
Prior work studies when models should answer vs abstain.

**Not our novelty.**

### Adaptive retrieval / information seeking
Prior work studies whether models know when to retrieve or ask questions.

**Not our novelty.**

### Minimal sufficient information
MT-InfoSeek (2026) formalizes multi-turn information seeking as a k-underspecified CSP and evaluates whether models identify a minimal sufficient set of queries.

Reference:
https://www.microsoft.com/en-us/research/publication/do-llms-know-what-to-ask-and-when-evaluating-multi-turn-information-seeking/

**Therefore “minimal sufficient information” alone is not novel.**

### Adaptive computation / Value of Computation
Rational Metareasoning for LLMs (2024) studies selective reasoning with a value-of-computation framing.

Reference:
https://arxiv.org/abs/2410.05563

DIAL / Same Signal, Opposite Meaning (2026) shows that compute need and compute suitability are distinct.

Reference:
https://arxiv.org/abs/2605.06908

**Therefore “when should the model think more?” is not novel.**

### Ask / act / repair with solver-grounded labels
Ask, Relax, or Act? (2026) evaluates actionable indeterminacy with solver-grounded decisions and matched pairs.

Reference:
https://arxiv.org/abs/2610.03102

**Therefore “solver-grounded next-action evaluation” is not novel by itself.**

### Counterfactual action outcomes
Agents' Last Doubt / SURE-Act (2026) executes each legal action at a decision point and trains a controller from counterfactual outcomes.

Reference:
https://arxiv.org/abs/2610.24194

**Therefore “counterfactual action value + learned controller” is not novel by itself.**

> **Verified at the source (2026-11-13):** arXiv 2610.24194 v1 (2026-10-16) exists with this title; read in full. See section 9a and `LITERATURE_FAILURE_MAP.md` §3. (The 2026-11-03 check could not find it.)

### Evidence-state diagnosis + action policy
EPRAG (2026) separates epistemic evidence-state diagnosis from response selection and uses counterfactual answerability for clarify-vs-abstain decisions.

Reference:
https://www.sciencedirect.com/science/article/abs/pii/S0950705126016552

**Therefore “diagnose state then choose action” is not novel by itself.**

### Tool sufficiency / causal tool frontiers
Recent tool-selection work studies causal sufficiency rather than semantic relevance.

Reference:
https://arxiv.org/abs/2606.06284 (ToolChoiceConfusion: Causal Minimal Tool Filtering, 2026; a filtering method using symbolic tool contracts, not an evaluation of the model's own pruning)

**Therefore “relevant tool != sufficient tool” is not a standalone novelty claim.**

---

## 2. What remains a candidate gap

We did not find prior work that combines all of the following as one exact LLM evaluation problem:

1. a single action space containing **information-acquisition and computation/verification actions**;
2. latent states requiring **information only, computation only, both, or neither**;
3. an exact formal oracle for whether a candidate intervention is sufficient;
4. exact or provable **minimal sufficient plans** rather than only relevant actions;
5. mixed plans requiring both resource types;
6. explicit unresolvable / neither cases;
7. evaluation that separates:
   - uncertainty detection,
   - resource diagnosis,
   - exact plan construction;
8. a mitigation based on explicit **epistemic obligations** rather than only scalar confidence or learned routing.

This is the candidate contribution.

---

## 3. Candidate benchmark claim

Safe wording:

> We introduce a controlled benchmark for testing whether LLMs can identify minimal sufficient epistemic plans across heterogeneous information and computation resources, while separating insufficiency detection from resource diagnosis and plan construction.

Do not say “the first” until the final literature sweep.

---

## 4. Candidate scientific question

> **When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?**

---

## 5. Candidate mitigation claim

> An explicit epistemic-obligation representation may improve action selection by checking which unresolved obligations candidate interventions actually discharge before the agent spends the resource.

The mitigation should be evaluated against:
- native LLM;
- confidence policy;
- ask-vs-think heuristic;
- learned router;
- oracle.

---

## 6. Why the three evaluation modes matter

Existing uncertainty-detection failures can contaminate the new question.

Therefore:

- **End-to-End** measures real behavior.
- **Detection-Controlled** isolates diagnosis + planning.
- **Diagnosis-Controlled** isolates plan construction / sufficiency.

If a model fails End-to-End but succeeds Diagnosis-Controlled, the problem may be detection rather than planning.

If it fails all three, the deeper planning capability is genuinely weak.

---

## 7. Novelty kill conditions

Re-scope immediately if a new paper is found that already provides all of:

- exact heterogeneous information+computation action space;
- minimal sufficient mixed plans;
- both/neither cases;
- exact oracle;
- separate detection-controlled and diagnosis-controlled evaluation;
- mitigation via formal obligations/planning.

Partial overlap is expected and should be cited.

---

## 8. Literature search checklist before submission

Search:
- “minimal sufficient epistemic plan LLM”
- “information computation joint planning LLM uncertainty”
- “epistemic resource allocation LLM benchmark”
- “ask compute both neither benchmark”
- “counterfactual answerability computation information”
- “epistemic obligations LLM agent”
- “sufficient intervention LLM agent”
- “minimal sufficient action plan uncertainty LLM”

Repeat search within 24 hours of final submission.

---

## 9. Reference check (2026-11-03)

arxiv.org and sciencedirect.com were blocked from the checking session, so only the Microsoft page was opened directly. The rest was checked through search results and mirror pages. Re-check every source directly before submission.

| Reference | Result |
|---|---|
| MT-InfoSeek (Microsoft Research, Aug 2026; arXiv 2608.14808) | Page opened. Confirmed: k-underspecified CSP, 5,251 problems, "fail to identify a minimal sufficient set of queries", models underestimate how much is missing and stop early. **Not in the abstract:** "ask the wrong variables". It says an incorrect *query order* reduces accuracy. |
| Rational Metareasoning for LLMs (arXiv 2410.05563) | Exists (De Sabbata, Sumers, Griffiths). Uses Value of Computation. Matches. |
| Same Signal, Opposite Meaning / DIAL (arXiv 2605.06908) | Exists (May 2026; NeurIPS 2026 poster). Compute need vs compute suitability. Matches. |
| Ask, Relax, or Act? (arXiv 2610.03102) | Found only on an aggregator page. Claim matches the snippet. Not confirmed at the source. |
| Agents' Last Doubt / SURE-Act (arXiv 2610.24194) | **Not found.** Treat as unverified. |
| EPRAG (Knowledge-Based Systems, S0950705126016552) | Exists; RAG-specific; counterfactual answerability; LLM/NLI approximation. "Separates evidence-state diagnosis from response selection" was not seen in the snippets. The date may be late August rather than 2026-10-25. |

### Newly found related work (add to the related-work section)
- **Active Epistemic Control for Query-Efficient Verified Planning** (2026, arXiv 2602.03974): the planner chooses between querying the environment to ground an unresolved predicate and simulating it. It mixes information and computation choices, but it is a planning method, not a benchmark with exact minimal sufficient plans or BOTH/NEITHER cases. **Partial overlap; cite.**
- When Planning Fails Despite Correct Execution (ICML 2026, arXiv 2605.23414): feasibility judgments under partial information. Information side only.

The searches in section 8 found no work that meets all the kill conditions in section 7.

## 9a. Direct source check (2026-11-13)

Each paper below was opened on arxiv.org (abstract and full HTML) and read; details, exact metrics and
limitations are in `LITERATURE_FAILURE_MAP.md`. This supersedes the "not confirmed" and "not found"
entries above.

| Reference | Result |
|---|---|
| MT-InfoSeek (arXiv 2608.14808, v1 2026-08-14) | Exists. 5,251 problems / 9,006 task instances (the project page says 8,912). Information-only, equal-cost queries; question order studied only in ClinGuide-MT, observationally. |
| Ask, Relax, or Act? (arXiv 2610.03102, v1 2026-10-02) | Exists. Matched pairs that flip whether intervention is necessary; IFC metric (GPT-6-Astra 92.57% accuracy vs 85.56% IFC). Output specification changes decisions (§5.3). |
| Agents' Last Doubt / SURE-Act (arXiv 2610.24194, v1 2026-10-16) | Exists. Ask vs search vs act in ToolSandbox; source-shift test 0/24 (App. D.1). "No generalisation to unseen families" holds offline only; end-to-end unseen gains are positive (Table 3). |
| Same Signal, Opposite Meaning / DIAL (arXiv 2605.06908, v2) | Exists. ρ(entropy, benefit) changes sign (FEVER Phi-3.5 −0.156 vs Llama-3.1 +0.428, Spearman). |
| ToolChoiceConfusion (arXiv 2606.06284, v1 2026-06-04) | Exists. Relevance ≠ executability ≠ causal sufficiency; CMTF 0.99 vs all tools 0.83 (Table 4), possibly partly circular. |
| Active Epistemic Control (arXiv 2602.03974, v1 2026-02-03) | Exists. Planner method; no evaluation of minimal or optimal epistemic action sets; ALFWorld 98.7% vs 98.3%. |

None of the six meets all the kill conditions in section 7: none combines an exact heterogeneous
information + computation action space with minimal sufficient mixed plans, BOTH/NEITHER cases and an
exact oracle.
