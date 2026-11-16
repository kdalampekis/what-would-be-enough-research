# Original roadmap, and the plan against its execution

This document answers two questions. First: what did the project plan to do before any model was run (hypotheses, experiments, evaluation modes, baselines, statistical safeguards, success criteria)? Second: for each planned experiment, what was built, what was run, on which data, with what result, and why the work continued, changed or stopped? The plan is restated from the original documents without change of substance. Results come from the result files named beside each number. The final claims are those of [`paper/report.md`](../paper/report.md).

Contents: 1. Sources · 2. The plan as written · 3. Items added to the plan later · 4. Plan against execution · 5. Planned elements that were not delivered

## 1. Sources and what "original" means

| Document | Date | Role |
|---|---|---|
| [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) | 2026-11-03 (commit `8ca8190`) | The plan: H1–H6, E0–E13, S1–S5, baselines, statistics, success criteria. The file has one commit in the history and was not edited afterwards (`git log -- EXPERIMENT_PLAN.md`). |
| [`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) | 2026-11-03, revised the same day | Research question, formal task, the three modes, oracle requirements, claim boundary. |
| [`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) | 2026-11-03, extended 2026-11-04 | Interpretation rules A1–A20 and the implemented semantics F1–F12. |
| [`PROTOCOL.md`](../PROTOCOL.md) | v0.2, 2026-11-04; models amendment 2026-11-14 | Turns the plan into a protocol. Adds experiment E14. Fixes the confirmatory tests for the test split. |
| [`ROADMAP_MATRIX.md`](working_documents/ROADMAP_MATRIX.md) | 2026-11-14 00:05 UTC | Status of the plan part-way through the sprint, with priorities. It is out of date for results; it is used here for priorities and for which items were added. |

The sprint ran from 2026-11-13 to 2026-11-15. The plan, the protocol and the benchmark predate it. No model had been called before 2026-11-13 ([`paper/report.md`](../paper/report.md), Appendix B).

Model order in every list of numbers below: qwen3.5-397b / qwen3.8-27b / deepseek-v4-flash / gemma-4-26b +schema. Modes: E2E (End-to-End), DC (Detection-Controlled), DxC (Diagnosis-Controlled). Rates count an unreadable or failed answer as wrong ("all attempted") unless stated.

## 2. The plan as written

### 2.1 Research question and goals

The research question ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §1):

> When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?

The plan names four questions for the experiments ([`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §1):

1. Do LLMs recognize when a state is insufficient?
2. Given that insufficiency is known, can they diagnose the required resource class?
3. Can they construct the minimal sufficient plan?
4. Can an explicit Epistemic Obligation Planner reduce failure and resource waste?

The project was to produce a benchmark study and a mitigation.

### 2.2 Hypotheses H1–H6

Quoted from [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §2.

| ID | Title | Statement |
|---|---|---|
| H1 | Detection is not the whole problem | "Models will perform better in Detection-Controlled mode than End-to-End mode, but substantial planning error will remain." |
| H2 | Resource diagnosis is easier than exact planning | "Models may correctly identify `INFORMATION_ONLY`, `COMPUTATION_ONLY`, `BOTH`, or `NEITHER` while still selecting an insufficient or wasteful plan." |
| H3 | Sufficiency is harder than relevance | "Models will often choose interventions that are semantically relevant but do not actually make the decision sufficient." |
| H4 | BOTH is a major failure regime | "Models will perform disproportionately worse on instances requiring mixed information + computation than on single-resource instances." |
| H5 | Minimality and stopping are distinct | "Even when models find a sufficient plan, they may over-consume resources or continue acting after sufficiency is achieved." |
| H6 | Explicit epistemic obligations help | "An obligation-guided planner will reduce insufficient actions, premature stopping, and excess resource cost relative to confidence-based and generic routing baselines." |

### 2.3 Three evaluation modes

From [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §3 and [`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §10.

| Mode | What the prompt reveals | What it measures | Role in the plan |
|---|---|---|---|
| End-to-End | Nothing about sufficiency | Detection → Diagnosis → Planning → Control | Realistic behaviour. Mixes detection with later abilities. |
| Detection-Controlled | States that the current state is insufficient | Diagnosis → Planning → Control | "The primary confirmatory mode." |
| Diagnosis-Controlled | Also gives the correct resource class | Planning → Sufficiency → Control | "The cleanest test of the novel capability." |

Interpretation rule fixed with the plan: an End-to-End failure alone is never read as a planning failure ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) A1, A20).

### 2.4 Benchmark families

Each base scenario was to generate matched sibling states that differ minimally. The minimum list ([`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §4): ALREADY_SUFFICIENT; INFORMATION_ONLY; COMPUTATION_ONLY; BOTH; NEITHER; a relevant-but-insufficient information action; a relevant-but-insufficient computation action; a sufficient but expensive plan; a cheaper sufficient alternative; a plan where action order matters; a state where one extra action is unnecessary; a state where early stopping is premature. All siblings of a scenario stay in one split.

### 2.5 Core experiments

Condensed from [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §5. E0–E13 are in the first plan (2026-11-03). E14 is not; see Section 3.

| ID | Name | Planned content | In the first plan |
|---|---|---|---|
| E0 | Oracle validation | No LLMs. Validate SAT/SMT against brute-force enumeration; posterior normalization; action effects; sufficiency; minimality; plan cost; resource class. Blocker: exact small-world agreement must be 100%. | Yes |
| E1 | Base decision competence | Already-sufficient instances. Measures whether the model can answer the underlying task, to separate task incompetence from epistemic-planning failure. | Yes |
| E2 | Insufficiency detection | End-to-End only. Sufficient vs insufficient classification; over-answering; unnecessary intervention. | Yes |
| E3 | Resource-class diagnosis | Detection-Controlled. Four classes. Primary metric: macro-F1 and balanced accuracy. | Yes |
| E4 | Exact intervention targeting | Given the resource class, identify the correct specific actions. | Yes |
| E5 | Sufficiency discrimination | Matched pairs: relevant and sufficient against relevant and insufficient. "One of the highest-priority experiments." | Yes |
| E6 | Minimality | Several sufficient plans of different cost or size. Does the model select a minimal one. | Yes |
| E7 | BOTH cases | At least one information and one computation action required. Subconditions: order irrelevant; order matters; one action reveals which computation is needed; computation reveals which question is decisive. | Yes |
| E8 | NEITHER cases | No available plan suffices. Inappropriate persistence; hallucinated actions; premature answer; correct defer or abstain. | Yes |
| E9 | Stopping | Too early, exactly at sufficiency, too late. Primary metric: excess actions after the first sufficient state. | Yes |
| E10 | Cost sensitivity | Fixed epistemic structure, varied action costs. Does the selected plan change at the correct boundary. | Yes |
| E11 | Risk sensitivity | Vary the wrong-answer penalty or decision threshold. Does the model change plan or defer when justified. | Yes |
| E12 | Structural distribution shift | Train/dev: shallow logic, small graphs, known templates. Test: deeper chains, larger graphs, branching, unseen linguistic skins. | Yes |
| E13 | External validation | After the synthetic benchmark is stable: ProofWriter and FOLIO transformations; probability or uncertainty transfer tasks. The synthetic exact benchmark remains primary. | Yes |

### 2.6 Solution experiments S1–S5

From [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §12.

| ID | Name | Planned content |
|---|---|---|
| S1 | Structured prompt only | The model reports unresolved obligations, candidate resources, why each is sufficient or insufficient, and a plan. |
| S2 | Obligation extraction + deterministic checker | The LLM proposes obligations; an exact checker verifies candidate actions. |
| S3 | Epistemic Obligation Planner | A formal planner finds a minimal sufficient plan from verified obligations and action effects. |
| S4 | Hybrid planner | The LLM estimates uncertain action effects where the formal environment does not know them; the planner optimises cost. |
| S5 | Shift robustness | Learned router against obligation planner under new costs, deeper graphs, new templates, new domains. |

The main mitigation claim was to rest on reductions in plan insufficiency, premature stopping, excess resource cost and decision regret.

### 2.7 Planned baselines

"At minimum" ([`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §6): 1. Always ANSWER; 2. Always ASK; 3. Always COMPUTE; 4. Always DEFER; 5. Random resource class; 6. Confidence-threshold policy; 7. Self-consistency gate; 8. Ask-vs-think heuristic; 9. Information-only planner; 10. Computation-only planner; 11. Generic learned router; 12. Native LLM structured prompt; 13. Epistemic Obligation Planner; 14. Oracle.

### 2.8 Output schema and metrics

- Structured outputs with fields for sufficiency, resource class, plan, stopping, confidence and a short justification. The benchmark scores fields, not prose, and does not require hidden chain-of-thought (§7).
- Primary metrics (§8): resource-class accuracy; plan exact match; plan sufficiency rate; minimality rate; premature stop rate; excess action rate; final decision accuracy; net utility or cost; epistemic action regret.
- Hierarchical metrics reported separately: detection accuracy, diagnosis accuracy given known insufficiency, plan accuracy given correct diagnosis, sufficiency accuracy, end-to-end optimal behaviour.
- Plan regret: value of the oracle plan minus value of the selected plan.

### 2.9 Statistical safeguards

From [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §9:

- split by scenario family, never by row;
- deterministic seeds;
- preregister primary hypotheses and metrics before the final run;
- cluster bootstrap confidence intervals by family;
- paired permutation or McNemar tests for matched-pair comparisons;
- Holm correction across confirmatory hypotheses;
- report effect sizes, not only p-values;
- separate exploratory from confirmatory analyses.

[`PROTOCOL.md`](../PROTOCOL.md) §8 (2026-11-04) made this concrete. Confirmatory tests are on the test split only, per model, in Detection-Controlled mode: H2, H3, H4a, H4b, exact two-sided McNemar on matched pairs, Holm across the four, α = 0.05. H1, H5, E10–E12, E14 and everything in the pilot are exploratory.

### 2.10 Model protocol and sample sizes

- Models (§10): three or four model families (frontier reasoning, frontier general, strong mid-size, cheaper or smaller). Primary run at temperature 0 or a deterministic equivalent, with pinned versions. A robustness subset of 100–200 scenarios with five stochastic runs per model.
- Pilot (§11): 100 base families, 5–8 siblings each, about 500–800 instances, two models.
- Main (§11): 400–600 base families, about 2,000–3,500 instances, three or four model families. "Strong design > many models."

### 2.11 Success criteria

From [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §13. A strong result is any one of:

1. models detect insufficiency but fail to identify sufficient plans;
2. models classify resource type correctly but fail at targeting;
3. models confuse relevance with sufficiency;
4. BOTH cases expose a large systematic failure;
5. models stop too early or continue too long;
6. obligation-guided planning materially reduces regret or cost.

A null result can still be publishable if the benchmark is exact and hard; frontier models succeed robustly; failures emerge only under shift, cost or sequential conditions; capability boundaries are carefully mapped.

### 2.12 Planned execution order

From [`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §14: 1. formal environment; 2. exact oracle; 3. oracle validation; 4. E1, E3, E5, E7 pilot; 5. End-to-End E2; 6. E6, E8, E9; 7. cost, risk and shift experiments; 8. solutions S1–S4; 9. external validation; 10. frozen held-out final evaluation; 11. write-up. "Do not begin expensive model experiments before oracle validation passes."

## 3. Items added to the plan later

| Item | Added | Source | Why it was added |
|---|---|---|---|
| E14, computation-capability control | 2026-11-04. First appears in commit `1d14793`. | [`PROTOCOL.md`](../PROTOCOL.md) §9 | A model may settle a computational fact internally. The benchmark could then measure compliance with a tool policy, not epistemic planning. E14 was prepared as a control. |
| T1, single-edit counterfactual pairs | 2026-11-13 | [`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md); [`PREREG_T1.md`](../PREREG_T1.md) | Three models were at ceiling in the calibration. The design was grounded in a reading of six related papers ([`LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md)). |
| T1B, over-intervention follow-up (H-OI) | 2026-11-13 | [`PREREG_T1B.md`](../PREREG_T1B.md) | An exploratory finding of the T1 pilot. |
| T3, relevance against necessity | 2026-11-13, design only | [`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §3 | Redundant plans of the weakest model in the calibration. Not run. |
| Rewording study | 2026-11-14 | [`PREREG_ROBUST.md`](../PREREG_ROBUST.md) | A parser with no model matched EOP on the benchmark's own wording. |
| Follow-up Studies 1–3 | 2026-11-15 and 2026-11-16 (UTC) | [`PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md), [`PREREG_REPAIR.md`](../PREREG_REPAIR.md) | Registered after the held-out results had been viewed. Study 2 is the planned E10. |

[`ROADMAP_MATRIX.md`](working_documents/ROADMAP_MATRIX.md) states that T1, T1B and T3 "do not replace E0–E14" and that H1–H6 are unchanged. Each added study has its own record in the [experiment registry](../experiments/experiment_registry.md).

## 4. Plan against execution

One row per planned experiment. The status words are used with fixed meanings:

- **planned but not executed**: no model run exists.
- **executed on development data**: run on the dev split (72 families), descriptive unless a registration says otherwise.
- **prospectively registered**: protocol and analysis fixed and hashed before any response for that study existed.
- **executed on held-out test data**: run once on the test split (63 families) under [`PREREG_FINAL.md`](../PREREG_FINAL.md).
- **exploratory only**: no registered test applies.
- **superseded or affected by an amendment**: the registered form was changed by a dated amendment; both forms are reported.

Evidence tiers stay separate. A held-out number for H2–H4 is registered held-out evidence. A held-out number for EOP is a prospective test of an amended method. E10 was run as a follow-up study registered after the held-out results had been viewed.

Result files: DEV = [`results/aggregate/v3dev/pilot_dev/report.md`](../results/aggregate/v3dev/pilot_dev/report.md); GATE = [`results/aggregate/GATE2_DEV_REPORT.md`](../results/aggregate/GATE2_DEV_REPORT.md); TEST = [`results/aggregate/final_test/v3/pilot_test/report.md`](../results/aggregate/final_test/v3/pilot_test/report.md) and `summary.json` beside it; TABLES = [`results/aggregate/final_test/RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md); EOPDEV = [`results/aggregate/eop_dev/eop_summary.json`](../results/aggregate/eop_dev/eop_summary.json); EOPTEST = [`results/aggregate/final_test/eop/eop_tables.md`](../results/aggregate/final_test/eop/eop_tables.md); FOLLOWUP = [`results/aggregate/followup/followup_report.md`](../results/aggregate/followup/followup_report.md); INDEX = [`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md).

Data and models for E1–E9, unless a row says otherwise: benchmark v3.0; dev split 72 families, 545 states (401 resolvable); test split 63 families, 468 states (342 resolvable); the four models named in Section 1; one answer per item at temperature 0.

| Planned experiment | Original purpose | Implemented | Executed (status) | Data and models | Main result | Hypothesis supported | Why continued, changed or stopped | Evidence |
|---|---|---|---|---|---|---|---|---|
| E0 Oracle validation | Exactness of labels before any model run. A blocker. | Yes | Executed before the sprint. No model, no split. | 10,000 small and 2,000 medium random instances; 200 families; 100 template-v3 families | 228,199 checks, 0 failed. | Not a hypothesis test. The blocker was passed. | Continued: the plan allowed model experiments only after exact agreement. | [`results/oracle_validation.md`](../results/oracle_validation.md); INDEX §4.1 |
| E1 Base decision competence | Separate task incompetence from planning failure. | Yes | Executed on development data; executed on held-out test data. Exploratory only. | As above; ALREADY_SUFFICIENT states and direct questions | Held-out base decision accuracy 1.00 / 1.00 / 0.98 / 0.61. Dev: 1.00 for the three stronger models, 0.57 for gemma (GATE §3). | Not a hypothesis test. | Continued through calibration, dev and held-out as planned. | TEST "E1, E2, E4, E6, E8, E9"; GATE §3 |
| E2 Insufficiency detection | Detection, End-to-End. Feeds H1. | Yes | Executed on development data; executed on held-out test data. Exploratory only. | As above, End-to-End | Held-out detection accuracy 0.97 / 0.97 / 0.97 / 0.90; over-answering 0.00 for all. H1: plan optimal E2E → DC on held-out 0.95→0.93 / 0.98→0.98 / 0.97→0.98 / 0.39→0.42. Share of items failing in all three modes 0.00 / 0.00 / 0.00 / 0.07. | H1 not supported for the three stronger models: no planning error remains in all modes. For gemma a share of 0.07 fails in every mode. Descriptive, no test. | Continued. H1 was registered as exploratory, so no test was added. | TEST "E1, E2…", "Mode decomposition"; TABLES "Conditions, held-out" |
| E3 Resource-class diagnosis | Diagnosis, Detection-Controlled. Feeds H2. | Yes | Executed on development data (exploratory only); prospectively registered ([`PROTOCOL.md`](../PROTOCOL.md) §8, [`PREREG_FINAL.md`](../PREREG_FINAL.md) F0); executed on held-out test data. | As above, DC | Held-out class accuracy 0.94 / 0.97 / 0.98 / 0.65. H2, class correct minus plan sufficient on resolvable states: −0.047 (Holm p 0.0001) / −0.003 (1) / −0.006 (1) / −0.111 (0.0002). | H2 not supported for any model. Significant in the opposite direction for qwen3.5-397b and gemma. | Continued to the held-out test although dev already pointed the other way (GATE §3). The test was registered before the dev data existed and was run as registered. | TEST "Diagnosis vs planning (H2)", "Confirmatory tests"; `summary.json` key `E3.detection_controlled.h2_paired_class_minus_sufficient` |
| E4 Exact intervention targeting | Correct actions given the class. | Yes | Executed on development data; executed on held-out test data. Exploratory only. | As above, DxC | Held-out exact match 0.97 / 0.99 / 0.99 / 0.44. Dev: 0.98 for the stronger models, 0.44 for gemma. | Not a hypothesis test. | Continued. | TEST "E1, E2, E4…"; GATE §3 |
| E5 Sufficiency discrimination | Relevant and sufficient against relevant and insufficient. Feeds H3. | Yes. Two decoy metrics are invalid on v3 and are not reported (INDEX §5). | Executed on development data (exploratory only); prospectively registered (F0); executed on held-out test data. | As above; 536 judgment items per model on held-out (349 pairs) | Held-out accuracy on sufficient plans 0.97 / 1.00 / 0.99 / 0.60; on relevant-insufficient plans 1.00 / 0.97 / 0.98 / 0.91. H3 difference: −0.023 (Holm p 0.023) / +0.029 (0.008) / +0.014 (0.5) / −0.255 (2.5e-13). | H3 supported for qwen3.8-27b only, with a small effect. For qwen3.5-397b and gemma the difference is significant in the opposite direction: they misjudge sufficient plans more often. | Continued. | TEST "E5 Relevance vs sufficiency", "Confirmatory tests"; `summary.json` key `E5.a_judgment` |
| E6 Minimality | Minimal plan among sufficient plans. Feeds H5. | Yes | Executed on development data; executed on held-out test data. Exploratory only. | As above, DC | Optimal given sufficient, held-out: 0.94 / 0.99 / 0.99 / 0.48. Dev: 0.955 / 0.985 / 0.982 / 0.514. | H5, descriptive: minimality near ceiling for the stronger models; gemma's plans are usually sufficient and rarely minimal. | Continued. The redundancy of gemma's plans motivated the T3 design, which was not run. | TEST "E1, E2, E4, E6…"; INDEX §3 |
| E7 BOTH cases | Mixed plans. Feeds H4. | Partly. BOTH siblings exist. The planned subconditions on action order were not built: plans are static sets ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F2, F6). | Executed on development data (exploratory only); prospectively registered (F0, H4a and H4b); executed on held-out test data. | As above, DC; 63 sibling pairs per test (62 for gemma, H4b) | Held-out plan sufficiency on BOTH 1.00 / 0.97 / 0.98 / 0.86. H4a (INFORMATION_ONLY minus BOTH): −0.016 / +0.032 / 0.000 / +0.111, Holm p 1 / 1 / 1 / 0.078. H4b (COMPUTATION_ONLY minus BOTH): 0.000 / +0.032 / +0.016 / +0.097, Holm p 1 / 1 / 1 / 0.146. | H4a and H4b not supported for any model. | Continued. | TEST "E7 BOTH vs single-resource", "Confirmatory tests" |
| E8 NEITHER cases | Recognising that no plan suffices. | Yes | Executed on development data; executed on held-out test data. Exploratory only. | As above, DC | Correct deferral, held-out: 0.89 / 0.87 / 0.97 / 0.00. Dev: 0.81 / 0.88 / 0.93 / 0.00. A text-only heuristic (h1pp) defers on every NEITHER state. | Feeds H5, descriptive. | Continued. Read only against the heuristic: NEITHER is solvable from surface text ([`RISKS.md`](working_documents/RISKS.md) 2b). | TEST "E1…E8…"; TABLES "Stopping" |
| E9 Stopping | Too early, at sufficiency, too late. | Yes, for static plans ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F9). | Executed on development data; executed on held-out test data. Exploratory only. The stopping question was later tested by T1B and F2 (prospectively registered) and by follow-up Study 1. | As above | Held-out premature stop (DC) 0.00 / 0.00 / 0.00 / 0.07. Acts on a state that is sufficient from the start (E2E) 0.13 / 0.00 / 0.00 / 0.67. | H5, descriptive: partly. See T1B, F2 and Study 1 in the [hypothesis tracker](hypothesis_tracker.md) for the tests and for the wording artifact. | Changed: stopping became the focus after the T1 pilot. Its interpretation changed after Study 1. | TEST "E1…E9"; TABLES "Stopping" |
| E10 Cost sensitivity | Plan changes at the correct price boundary. | Yes (variants frozen 2026-11-04; runner prepared 2026-11-13). | Not run during the dev and held-out phases. Then prospectively registered after the held-out results had been viewed ([`PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md), Study 2) and executed on train-split families. | 60 train families, 209 price sweeps, 780 items; qwen3.5-397b, qwen3.8-27b, gemma +schema; DC. deepseek-v4-flash not included. | Cheapest plan just above / just below the boundary: qwen3.5-397b 0.95 / 0.97; qwen3.8-27b 0.95 / 0.98; gemma 0.31 / 0.16. Registered test of cost insensitivity: Holm p 1.0, 1.0, 0.0003. | Not one of H1–H6. Cost insensitivity supported for gemma only. | Not started, by a decision of 2026-11-14 ([`PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md) §0). The diagnostics of 2026-11-13 had found that only 120 of 527 dev variants change the cheapest plan and expected a ceiling for the stronger models ([`FINDINGS.md`](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md) §5). Run after the project owner's instruction of 2026-11-15 (same section). The reason for the instruction: Not recorded. | FOLLOWUP "Cost (E10)" |
| E11 Risk sensitivity | Plan or deferral under a changed threshold. | Partly: variants frozen; analysis not wired into the driver. | Planned but not executed. | — | None. | Not tested. | Kept apart from the core benchmark on 2026-11-03: the core benchmark uses logical sufficiency only, and probabilistic sufficiency is a separate stress test in E11 ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §6). Priority P2 in [`ROADMAP_MATRIX.md`](working_documents/ROADMAP_MATRIX.md). | INDEX §4.14 |
| E12 Structural distribution shift | Generalisation to deeper, larger or differently worded problems. | Partly: v3 has a theme shift only; width and depth variants exist for v2. | Planned but not executed. | — | None. | Not tested. | Priority P1; no v3 shift set was defined. Why it was not reached: Not recorded. The rewording study is a separate study on dev families and is not E12 (INDEX §2). | INDEX §4.14 |
| E13 External validation | Transfer to external tasks. | Converter only (information actions only). | Planned but not executed. | — | None. No external dataset was processed. | Not tested. | Priority P2. | [`CLAIMS.md`](../research/working_documents/CLAIMS.md); INDEX §4.14 |
| E14 Computation-capability control (added 2026-11-04) | Whether models skip computation they can do internally. | Opt-in runner and analysis. | Planned but not executed. | — | None. | Not tested. | Priority P2. Why it was not run: Not recorded. The risk it controls for remains open. | [`PROTOCOL.md`](../PROTOCOL.md) §9; INDEX §4.14 |
| S1 Structured prompt | Prompt-only mitigation. | Yes, as condition B. | Prospectively registered ([`PREREG_EOP.md`](../PREREG_EOP.md)); executed on development data; affected by Amendment 2 (gemma's answers read from message text); executed on held-out test data. | v3 dev and test, E2E and DC; counterfactual-pair items; four models | Held-out plan optimal (DC): 0.62 / 0.96 / 0.94 / 0.40 (gemma read from text), against native 0.93 / 0.98 / 0.98 / 0.42. For qwen3.5-397b 119 of 405 answers no longer parse. | Does not help any model. Registered as descriptive. | Continued as a comparison condition. | TABLES "Conditions, held-out"; EOPTEST |
| S2 Obligation extraction + checker | Verification without full planning. | Yes, as the verifier ablation D (D′, Dt): the structured-prompt plan pruned against the extracted state, with no search. Labels differ between documents (INDEX §5). | Prospectively registered; executed on development data; superseded or affected by an amendment (D′ and Dt come from Amendments 1 and 2); executed on held-out test data. | As S1. No calls of its own. | Held-out plan optimal (DC), verifier only: 0.69 / 0.98 / 0.95 / 0.41. EOP minus verifier: +0.31 / +0.02 / +0.05 / +0.58. | Verification alone helps less than full planning. Descriptive. It inherits the unparsed answers of S1. | Continued as an ablation. | TABLES; EOPTEST |
| S3 Epistemic Obligation Planner | Extraction by the model, then an exact planner. Tests H6. | Yes, as conditions C (registered prompt v1) and C′ (amended prompt v2). | Prospectively registered; executed on development data; superseded or affected by an amendment (Amendment 1); then a prospective test of the amended method, executed on held-out test data (F1). | As S1 | Registered dev test, C minus native (DC): −0.264 / −0.329 / −0.935 / +0.546; supported for gemma only. Amended C′ on dev: 1.000 on all 401 resolvable states (development-informed). Held-out EOP: 1.00 / 1.00 / 1.00 / 0.99; EOP minus native +0.07 / +0.02 / +0.02 / +0.57, Holm p ≤ 0.005. A parser with no model also scores 1.00. | H6 as registered on dev: supported for gemma only. Amended method on held-out: supported for all four models, with a large gain only for gemma. H6 against confidence-based and routing baselines was never tested. | Changed by Amendment 1 after a pipeline check showed that the registered prompt never displayed the required layout. The registered result stands. | EOPDEV; TABLES; [`PREREG_EOP.md`](../PREREG_EOP.md); [`paper/report.md`](../paper/report.md) Appendix B |
| S4 Hybrid planner | LLM-estimated action effects. | No | Planned but not executed. | — | None. | Not tested. | "Out of scope this sprint" ([`ROADMAP_MATRIX.md`](working_documents/ROADMAP_MATRIX.md)). | INDEX §4.14 |
| S5 Shift robustness | Obligation planner against a learned router under shift. | No. No learned router was built. | Planned but not executed. | — | None. | Not tested. | Depended on E12 ("only if E12 runs"). | INDEX §4.14 |

Notes on the table.

- The Holm p-values for H2–H4 are from the per-model family of four tests registered in [`PROTOCOL.md`](../PROTOCOL.md) §8. The directions are read from the paired differences in `summary.json`.
- gemma +schema has 341 resolvable Detection-Controlled items in the H2 test, not 342. TEST leaves an item with no response out of the denominator ("Plan sufficiency by mode": 341, 341 and 340 items in the three modes). The EOP analysis of the same run counts such an item as wrong (342 items in EOPTEST's summary file). At two decimals the native optimal-plan rate is 0.42 on either basis. The same difference in handling was recorded for the dev split (INDEX §5).
- The dev values for H2–H4 are descriptive. One dev report prints them under "Confirmatory tests"; that heading is wrong for the dev split (INDEX §5).

## 5. Planned elements that were not delivered, or were delivered differently

| Planned | What happened | Source |
|---|---|---|
| Models: frontier reasoning, frontier general, mid-size, smaller; [`PROTOCOL.md`](../PROTOCOL.md) §3 named GPT-5.6 Sol, Claude Sonnet 5.5, Claude Opus 5.5 and Gemini 4 Argon | Four open-weight models from one provider were run. The planned proprietary models were not. Why the model set changed: Not recorded. | [`PROTOCOL.md`](../PROTOCOL.md) amendment of 2026-11-14 |
| Robustness subset with five stochastic runs per model | Not run. One answer per item at temperature 0. No estimate of run-to-run variation. | [`paper/report.md`](../paper/report.md) Appendix A |
| Main sample of 400–600 families | 300 families, 2,282 states (165 train / 72 dev / 63 test). Why 300: Not recorded. | [`data/FREEZE_v3.json`](../data/FREEZE_v3.json); INDEX §1 |
| Pilot of 100 families with two models | Calibration on 10 dev families with six model conditions, then all 72 dev families with four. | INDEX §4.3, §4.4 |
| Baselines 1–4 (always answer, ask, compute, defer) | Reported as fixed policies in the dev and held-out reports. | TEST (`policy-*` rows) |
| Baseline 5 (random resource class) | A random agent exists as a synthetic test fixture (`src/msep/agents/mock.py`). It is not in the result tables read for this document. | — |
| Baselines 6–11 (confidence threshold, self-consistency gate, ask-vs-think heuristic, information-only planner, computation-only planner, learned router) | Not built. H6 was therefore tested against native planning and a structured prompt only. | INDEX §3 notes; [`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F11 |
| Baselines not in the plan | Three text-only heuristics (h1, h1p, h1pp) and a rule-based parser followed by the exact planner were added and are reported beside the models. | [`PROTOCOL.md`](../PROTOCOL.md) §6; [`PREREG_FINAL.md`](../PREREG_FINAL.md) §3 |
| Sibling type "plan where action order matters"; conditional plans | Not implemented. Plans are static sets chosen before any result is seen. | [`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F2, F6 |
| Effect size Cohen's h; H2–H4 on the `heuristic_hard` subset; paired DC minus E2E difference | Registered as analyses, absent from the result files. | INDEX §5 |
| "Frozen held-out final evaluation" run once | Run once. The results were first analysed during a provider outage, before one model's run had finished, under a rule committed beforehand; the reported numbers are from the complete data. | [`INTERIM_NOTE.md`](../results/aggregate/final_test/INTERIM_NOTE.md); [`paper/report.md`](../paper/report.md) Appendix B |

Measured against the success criteria of Section 2.11: criteria 1, 2 and 4 were not met (H2 and H4 were not supported). Criterion 3 was met for one model with a small effect. Criterion 5 was met for the weakest model; for one strong model most of the measured over-intervention came from an ambiguity in the benchmark text (follow-up Study 1). Criterion 6 was met only for the amended method, and a parser with no model matches it on the benchmark's own wording. The outcome is closest to the plan's description of a publishable null result: an exact benchmark on which three of four models succeed, with failures that appear for the weakest model and under rewording of the state description. This reading follows [`paper/report.md`](../paper/report.md) Sections 4–6; the mapping to the numbered criteria is ours (retrospective interpretation).
