# Research decisions in chronological order

This document answers one question: at each turning point of the project, what was known, what evidence was on the table, what was decided, why, and what followed? Each decision has five labelled parts: research state, evidence, decision, rationale, consequence. Every milestone is linked to its protocol, result file or commit. Where the record gives no reason, the text says "Not recorded". Where a reason is reconstructed from the records, the sentence is marked "(retrospective interpretation)". The final claims are those of [`paper/report.md`](../paper/report.md).

Conventions. Times are UTC, taken from git commit timestamps and from the marker lines of the run logs in [`results/raw/`](../results/raw/). Commits are cited by short hash. Model order in lists of numbers: qwen3.5-397b / qwen3.8-27b / deepseek-v4-flash / gemma-4-26b +schema. Rates count a failed or unreadable answer as wrong unless stated. Intervals are 95% family-clustered bootstrap intervals.

Evidence tiers are named in each decision and are not mixed: registered held-out; registered development; prospective test of an amended method; rewording study; follow-up studies registered after the held-out results were viewed; exploratory; no-model baselines.

## Timeline

| Date (UTC) | Milestone | Record |
|---|---|---|
| 2026-11-03 | Specification, plan, formal model, exact oracle, oracle validation | commits `8ca8190` … `106a8c0` |
| 2026-11-04 | Benchmark audit, v2, adversarial audit, v3, protocol v0.2, freeze of v3.0 | commits `4e90cd2` … `0b7f846` |
| 2026-11-13 | First model calls; calibration; challenge design; T1 registered and run; T1B and EOP registered | commits `b09f07c` … `0dfee91` |
| 2026-11-14 | EOP Amendments 1 and 2; dev gate 2; held-out and rewording protocols frozen; runs start | commits `e1fb301` … `35b983b` |
| 2026-11-15 | Provider outage; first view of held-out results under a committed rule; complete results; Studies 1 and 2 registered | commits `c3aed44` … `fd8145c`, `2863f90` |
| 2026-11-16 | Study 3 registered; follow-up analyses run once; submission report | commits `2935522` … `de44402` |

## 1. Choosing the research direction (2026-11-03)

**Research state.** No code existed. The literature had been positioned up to 2026-11-02 ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md), header). The project was aimed at Track 1 of the sprint, model epistemics and decision-making evaluations.

**Evidence.** [`NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) §1 lists what prior work already covers: calibration, abstention, adaptive retrieval and information seeking, minimal sufficient information, adaptive computation, solver-grounded ask-or-act decisions, counterfactual action outcomes, evidence-state diagnosis before action selection, tool sufficiency. §2 lists eight properties that the author did not find combined in one evaluation: one action space with information and computation actions; states that need information only, computation only, both or neither; an exact oracle for sufficiency; exact minimal sufficient plans; mixed plans; unresolvable cases; separation of detection, diagnosis and plan construction; a mitigation based on explicit obligations. The reference check of 2026-11-03 could not open several sources directly and marked one paper as not found ([`NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) §9).

**Decision.** Study whether language models can identify minimal sufficient epistemic plans over two kinds of resource, information and computation, including mixed and unresolvable cases, with detection measured separately from diagnosis and planning. Produce a benchmark study and a mitigation ([`EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §1). Do not claim that uncertainty detection, abstention, adaptive retrieval, adaptive computation or minimal sufficient information are new ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §15).

**Rationale.** The stated reason is the gap of [`NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) §2 and the view that "ASK vs COMPUTE is only a controlled diagnostic slice" of a larger question ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §9). Which alternative directions were considered, and why this one was preferred to them: Not recorded.

**Consequence.** Hypotheses H1–H6 and experiments E0–E13 were written the same day ([original roadmap](original_roadmap.md)). The novelty wording was bounded ("we did not find prior work…") and tied to a final literature check. The source check was repeated on 2026-11-13 at the papers themselves and found all six closest papers ([`LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md)). A further check on 2026-11-15 added one related benchmark to the report (commit `a635ddd`).

## 2. A formal benchmark with an exact oracle, and the separation of information from computation (2026-11-03)

**Research state.** The question needed labels for "sufficient" and "minimal" that do not depend on a model's judgment.

**Evidence.** No empirical evidence yet. The design rules were written before any code: the oracle "must be independent of the evaluated LLM" and "no LLM may be used as the authoritative oracle" ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §11); the same model must not generate labels, judge labels and be evaluated on them ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) A14); brute force and a solver must agree exactly, and "any mismatch is a blocker" (A12); a computation action must never reveal a hidden external fact, or "the information/computation distinction is invalid" (A10). A review on the same day found that the first computation tasks were trivial and could be done mentally ([`BENCHMARK_CHANGELOG.md`](working_documents/BENCHMARK_CHANGELOG.md), v1).

**Decision.**
- States are small propositional problems. An exact oracle (SAT and MaxSAT, checked against brute force) labels the resource class and every cheapest sufficient plan.
- Information actions reveal contingent world facts. Computation actions run a certified procedure on inputs the agent already has; the result is fixed but not part of the decision state until the procedure is run ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §5.1, revised 2026-11-03; commit `443af53`).
- Computation tasks are chosen to be impractical to do mentally.
- Scope: logical sufficiency only; static plans chosen before any result is seen ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F2, F3). Probabilistic sufficiency and conditional plans were left for later.

**Rationale.** Exactness removes circular evaluation and makes minimality checkable. Under the logical rule a plan is sufficient exactly when it resolves every obligation, so the cheapest plan is a minimum-cost hitting set, which is what the mitigation would later use ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F5). The probabilistic rule was excluded from the core benchmark because it is not monotone in information and the obligation-cover property does not hold for it ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §6).

**Consequence.** Oracle validation (E0) passed: 228,199 checks, 0 failures ([`results/oracle_validation.md`](../results/oracle_validation.md); no-model evidence). The certified-computation convention created a known risk: a model that computes a value internally is scored as not having run the procedure. A control experiment (E14) was prepared for it on 2026-11-04 and was never run ([`PROTOCOL.md`](../PROTOCOL.md) §9). The scope choices are limitations of every later result: no sequential plans, no probabilities, synthetic tasks ([`paper/report.md`](../paper/report.md) Appendix A).

## 3. The shortcut discovered in benchmark v2 (2026-11-04)

**Research state.** The first family template had been built and labelled. No model had been run.

**Evidence.**
- The author's own audit: a lookup probe on surface counts in the prompt predicted the resource class at 86–90% on the first pool, against a 50% baseline ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F8; [`results/audit_v2/benchmark_audit.md`](../results/audit_v2/benchmark_audit.md)). Template v2 randomised redundant actions and distractors; the probe fell to 56–69%.
- An independent adversarial audit then showed that v2 is solved 100% by reading only the rule that defines the target. Rule order, rule signs and costs leaked roles and hidden values. Mental shortcuts solved the computation tasks at 100% (posterior), 90% (modular exponentiation) and 70% (primality) ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F12; [`RISKS.md`](working_documents/RISKS.md), "Already fixed").
- A text-only heuristic (h1pp) reached class accuracy 1.00 and optimal plans on 0.909 of v2 dev items (n = 671) ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.2).

**Decision.** Treat v2 as a benchmark that "does not measure sufficiency reasoning" ([`CLAIMS.md`](../research/working_documents/CLAIMS.md)). Keep it only as a shallow subset for comparison. Build a new template (commit `9dbc968`).

**Rationale.** A benchmark that surface reading solves cannot test the hypotheses. The changelog fixes a rule for all such changes: "No change may be made to raise or lower model scores"; no model had been run when the change was made ([`BENCHMARK_CHANGELOG.md`](working_documents/BENCHMARK_CHANGELOG.md)).

**Consequence.** Template v3 (decision 4). The audit became a reported validation result: the first validated benchmark measured a surface shortcut, and this was found before any model was run ([`RESEARCH_READINESS.md`](working_documents/RESEARCH_READINESS.md) §7).

## 4. The v3 redesign and freeze (2026-11-04)

**Research state.** v2 was known to be shallow. A calibration pilot was planned.

**Evidence.** Template v3 draws random theories from four motifs with optional indirection, bridges, mixed routes and bulk actions. Sibling states are drawn from one class-independent distribution and binned by the oracle. Implication signs, rule order and costs are randomised. Computation tasks were replaced by a second version on which the audit's mental shortcuts score at chance ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F12; [`results/audit_v3/benchmark_audit.md`](../results/audit_v3/benchmark_audit.md)). All 2,282 labels were re-verified by brute force with 0 mismatches. The h1pp heuristic falls to class accuracy 0.747 and optimal plans 0.506 on v3 dev (n = 545, all states); on resolvable dev states in Detection-Controlled mode it gives sufficient plans on 0.845 and optimal plans on 0.586 ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.2; no-model evidence).

**Decision.**
- Make v3 the main benchmark and freeze it as v3.0: 300 families, 2,282 states, 165 train / 72 dev / 63 test families ([`data/FREEZE_v3.json`](../data/FREEZE_v3.json); commit `0b7f846`).
- Accept the residual: a heuristic still gets about half of the plans. Report the heuristics beside every model result and pre-register a stress subset (`heuristic_hard`) of items the heuristic fails ([`PROTOCOL.md`](../PROTOCOL.md) §6).
- Write the evaluation protocol with the confirmatory tests for the test split ([`PROTOCOL.md`](../PROTOCOL.md) §8, v0.2).

**Rationale.** After the freeze, risks are "handled in analysis and reporting, not by further redesign" ([`RISKS.md`](working_documents/RISKS.md), header). Only objective bug fixes are allowed, each with a new freeze record.

**Consequence.** The freeze record still verified on 2026-11-14, so benchmark content did not change during the sprint ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §7). Two known weaknesses stayed with the benchmark. First, NEITHER states are solved by the heuristic, so deferral results are read only against it ([`RISKS.md`](working_documents/RISKS.md) 2b). Second, a wording in the frozen text, found later, turned out to matter (decision 11). The analyses on `heuristic_hard` that were registered for H2–H4 are absent from the result files ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §5).

## 5. First model calibration and the near-ceiling result (2026-11-13)

**Research state.** The sprint began. The protocol named proprietary models for the pilot ([`PROTOCOL.md`](../PROTOCOL.md) §3). The models actually run were open-weight models hosted by one provider ([`PROTOCOL.md`](../PROTOCOL.md), amendment of 2026-11-14). Why the model set changed: Not recorded.

**Evidence** (exploratory; 10 dev families, 74 states, 54 resolvable; [`FINDINGS.md`](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md)).
- Optimal plans, Detection-Controlled: 0.96 / 0.96 / 0.98 for qwen3.5-397b, qwen3.8-27b and deepseek-v4-flash. All three are at a ceiling for sufficiency and optimality in every mode.
- gemma-4-26b: 34% of its plain answers did not parse. With a forced output schema the parse-error rate fell to 1%, and the optimal-plan rate was 0.33. The schema condition also changed behaviour: on items parsed in both conditions it was lower by 0.14.
- glm-5.3-flash: 0.56, with 26% of answers truncated; at a 32,000-token cap 39 of 278 jobs still gave no answer, mostly on BOTH and NEITHER states.
- gemma's lost optimality was redundancy: sufficient plans padded with unnecessary actions.

**Decision.**
- Carry four conditions forward: the three strong models and gemma with the forced schema, documented as a separate condition that is not comparable to plain gemma.
- Do not run the planned cost-sensitivity experiment (E10) next. Design a separate challenge tier instead ([`FINDINGS.md`](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md) §5).

**Rationale.** For E10: only 120 of 527 dev cost variants change the cheapest plan, a cost-blind policy scores about 0.77 pooled over all 527 (0.00 on the 120), and the observed failures were redundancy and non-termination, not cost choice; a ceiling was expected for the strong models. For the challenge tier: new difficulty should be fixed from the generator's formal structure and not tuned on these models' outputs. Why glm-5.3-flash was not carried forward: Not recorded; its non-answers are the documented difference (retrospective interpretation).

**Consequence.** The literature-driven challenge design (decision 6). The decision on E10 was reversed two days later (decision 11), and the expectation of a ceiling for the strong models was then confirmed for the two that were tested.

## 6. The literature-driven challenge design (2026-11-13)

**Research state.** Three of four models were at ceiling on v3 after ten families. The time left in the sprint was not recorded ([`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §6).

**Evidence.**
- Six related papers were read at the source, with the measured failure modes of each and what they imply for this project ([`LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md); commit `b547434`). Two findings shaped the design: matched-pair correctness can be well below item accuracy, and most errors in one solver-labelled benchmark were needless interventions.
- From the calibration data: v3 sibling states are counterfactual but differ in several items, not one; pair correctness on v3 was close to what independent errors predict ([`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §2).

**Decision.** Rank six candidate tests ([`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §3, §6).

| Test | Decision | Reason given |
|---|---|---|
| T1, single-edit counterfactual pairs | Priority 1; build now | Feasible with the existing oracle |
| T5, stopping after an edit | Folded into T1 | No separate generator needed |
| T3, relevance against necessity at fixed size | Priority 2; "possibly, after T1" | Needs generator work; targets the redundancy seen for gemma |
| T2, switching the information source | Not recommended for the sprint | In this formalism the answer could be read from the action menu |
| T4, conditional sequential planning | Separate extension | Needs a new oracle; must not be scored with the static-plan oracle |
| T6, unseen structural families | Later | Needs a new template |

Cost edits were excluded from T1 because they are E10. v3 stays frozen and primary, and every confirmatory claim stays on v3.

**Rationale.** Difficulty should come from structure, not size, and no item may be selected by a tested model's behaviour ([`CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §1). The design draft discloses that it was written after seeing which models were at ceiling.

**Consequence.** T1 was registered and frozen at 21:22 ([`PREREG_T1.md`](../PREREG_T1.md); commit `314469d`). Two things differ from the design draft. The draft speaks of a new v4 pool; the registered T1 edits states of the frozen v3 pool. The draft lists three edit kinds; the registered generator has two (a world fact becomes observed; a computed fact gets its certified value), and the "action becomes unavailable" edit is absent. The reasons for both changes: Not recorded. T3 was never run. The literature map also suggested a grounded-verification controller as a baseline for the mitigation. No registration names such a condition; the closest registered condition is the verifier ablation D ([`PREREG_EOP.md`](../PREREG_EOP.md)).

## 7. The T1 result (2026-11-13)

**Research state.** T1 was registered for a dev pilot with decision rules fixed in advance, on 20 dev families that the calibration had not used.

**Evidence** (registered development; 133 pairs, 85 direct and 48 indirect; three models; [`T1_PILOT_FINDINGS.md`](../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md), [`t1_summary.json`](../results/aggregate/t1_pilot_dev/t1_summary.json)).
- Joint accuracy on the indirect pairs: qwen3.5-397b 0.792 [0.667, 0.902]; qwen3.8-27b 0.938 [0.870, 1.000]; gemma +schema 0.146 [0.048, 0.278].
- Rule "ceiling" (lower bound ≥ 0.90): met by no model.
- Rule "additional capability gap" (upper bound < 0.90 for a model at ceiling on v3): not met. For qwen3.5-397b the upper bound is 0.902, above the threshold by 0.002.
- Rule "edit-tracking failure": formally met by all three models. Near ceiling the rule is met by construction, so it carries no information.
- Exploratory: qwen3.5-397b still proposed an action on 10 of 55 states that the edit had made sufficient; gemma on 30 of 55. The findings note gives an example: a computation planned after its certified result had been added to the known values.

**Decision.** Report T1 as inconclusive for both qwen models under the registered rules. Report the flaw of the third rule and do not change it. Make no claim from the over-intervention pattern; register a test of it on fresh families.

**Rationale.** "This is one pilot on 20 families and was not a registered hypothesis; it needs a registered test on fresh families before any claim" ([`T1_PILOT_FINDINGS.md`](../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md)).

**Consequence.** T1B (decision 8). The counterfactual pairs became the instrument for the stopping tests on the held-out split.

## 8. The over-intervention follow-up T1B (registered 2026-11-13, 23:53)

**Research state.** An exploratory pattern existed for two models on 55 states.

**Evidence** (registered development; 42 dev families not used by the calibration or the T1 pilot; 122 states that one edit made sufficient; four models; [`t1b_summary.json`](../results/aggregate/t1b_dev/t1b_summary.json), [`GATE2_DEV_REPORT.md`](../results/aggregate/GATE2_DEV_REPORT.md) §2).
- Hypothesis H-OI: after a single intervention makes a state sufficient, models continue to propose actions that are no longer needed ([`PREREG_T1B.md`](../PREREG_T1B.md)).
- T-OI-1 (the rate exceeds 0.05): rate 0.172 [0.099, 0.256] / 0.000 / 0.016 [0.000, 0.041] / 0.680 [0.561, 0.780]. Supported for qwen3.5-397b (Holm p 0.0012) and gemma +schema (Holm p < 0.001). Not supported for the other two.
- T-OI-2 (the rate is higher than on states that were sufficient from the start): difference +0.053 [−0.050, 0.153] for qwen3.5-397b and +0.037 [−0.122, 0.197] for gemma. Supported for no model.
- Descriptive: qwen3.5-397b's extra actions were mostly computations (0.172 of states against 0.016 for information actions), and it never said "sufficient" and then acted.

**Decision.** At the dev gate, carry T-OI-1 to the held-out split as a confirmatory test (family F2). Report T-OI-2 on held-out data descriptively, because it was not supported on dev ([`PREREG_FINAL.md`](../PREREG_FINAL.md) §5).

**Rationale.** Over-intervention was shown for two models. It was not shown to be specific to the edit. The registration states that non-significant results are not evidence of absence.

**Consequence.** F2 on the held-out split (decision 10). The extra actions of qwen3.5-397b were mostly computations here, and the example given for the T1 pilot is a computation. This is consistent with the wording problem that Study 1 later isolated (decision 11); nobody drew that link at the time (retrospective interpretation).

## 9. The EOP mitigation: obligations, the failure of the registered condition, and two amendments (2026-11-13 to 2026-11-14)

**Research state.** The planner and a state-extraction interface had been built before the sprint. With a rule-based parser the planner was exact on this benchmark, because the rendering is regular; the open question was the planner behind an LLM extractor ([`ASSUMPTIONS.md`](working_documents/ASSUMPTIONS.md) F10).

**Why obligations.** The mitigation was part of the original design: unresolved requirements are represented as obligations, actions discharge them, and a planner finds a minimum-cost plan that discharges all ([`PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §8, §14; hypothesis H6). Under the logical rule this is exact (decision 2). The originally planned comparators, confidence-based and routing baselines, were not built; the registration restates H6 "relative to native planning and a structured prompt" ([`PREREG_EOP.md`](../PREREG_EOP.md)).

**Decision A: the registered comparison (23:58 on 2026-11-13, before any B, C or D response).** Conditions: A native answer; B structured obligation prompt; C extraction by the model (prompt v1) followed by the exact planner; D verifier ablation. One confirmatory test: C minus A on plan optimality, v3 dev, Detection-Controlled, Holm across four models. Strict scoring: an invalid extraction counts as a failure, with no fallback ([`PREREG_EOP.md`](../PREREG_EOP.md); commit `0dfee91`).

**Evidence for the registered condition** (registered development; 72 dev families, 401 resolvable states; [`eop_summary.json`](../results/aggregate/eop_dev/eop_summary.json)).
- C minus A: −0.264 [−0.328, −0.200] / −0.329 [−0.379, −0.285] / −0.935 [−0.957, −0.911] / +0.546 [0.485, 0.606]. Holm p 1 / 1 / 1 / < 0.001. The registered test is supported for gemma +schema only.
- Invalid v1 extractions: 171 / 191 / 533 / 3 of 545.
- Cause: the v1 prompt described its output fields in prose and never showed the layout the reader requires. Models without schema enforcement returned the right content in other layouts. gemma received the layout through its forced schema.

**Decision B: Amendment 1 (2026-11-14, 11:36).** Add condition C′ (and D′): the v1 prompt plus the exact JSON template. Nothing else changes. Run it for the three models without schema enforcement. Report C and D exactly as registered. The confirmatory test stays C minus A ([`PREREG_EOP.md`](../PREREG_EOP.md), Amendment 1; commits `e1fb301`, `6ff8d16`).

**Rationale for Amendment 1.** "Under strict scoring, condition C therefore mostly measured whether a model guesses our layout." The amendment was decided after a pipeline check of extraction validity and before any C or D outcome was scored. It was still made after seeing dev data, and the documents say so.

**Evidence for the amended condition** (exploratory, development-informed). C′ gives an optimal plan on all 401 resolvable dev states; 0 of 545 extractions are invalid. C′ minus A: +0.045 [0.025, 0.069] / +0.025 [0.010, 0.040] / +0.037 [0.020, 0.058].

**Decision C: Amendment 2 (2026-11-14, 13:32; analysis only).** Under the structured prompt, gemma +schema answered as message text with no function call in all 1,018 responses, so registered B and D have no parsed answer for it. A sensitivity condition Bt reads the JSON from the message text; Dt is its verifier variant. Registered B and D are reported unchanged ([`PREREG_EOP.md`](../PREREG_EOP.md), Amendment 2; commit `58315e7`). Bt gives optimal plans on 0.394 of states (Detection-Controlled) against gemma's native 0.446; the difference is −0.052 [−0.131, 0.030].

**Further evidence at the dev gate.**
- The structured prompt alone helps no model. For qwen3.5-397b it loses 252 of 1,018 answers to parsing ([`GATE2_DEV_REPORT.md`](../results/aggregate/GATE2_DEV_REPORT.md) §1 and "Corrections").
- The rule-based parser with the same planner, and no model, scores 1.000 on every dev item set (no-model baseline).

**Consequence.**
- The registered experiment failed for three of four models, and that result stands ([`paper/report.md`](../paper/report.md) Appendix B, Table B1).
- The amended method is development-informed. A held-out result for it can only be a prospective test of the amended method ([`PREREG_FINAL.md`](../PREREG_FINAL.md) §1).
- The parser was promoted from an upper bound to a reported baseline after an audit found that it reads only the prompt text ([`PREREG_FINAL.md`](../PREREG_FINAL.md) §3). Because it matched EOP, a rewording study was registered (decision 10).
- The freeze records of the registration and of both amendments no longer verify, because each later step added to the same files; the held-out freeze pins the final versions ([`docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §6).
- The gate report was re-read independently on 2026-11-14 and corrected in place, with a log of the earlier wording.

## 10. The held-out evaluation, the parser comparison and the rewording study (2026-11-14 to 2026-11-15)

**Research state.** The report of dev gate 2 is dated 2026-11-14, 16:45 ([`GATE2_DEV_REPORT.md`](../results/aggregate/GATE2_DEV_REPORT.md); commit `cfb87bd`). The test split had not been touched. A draft held-out plan existed ([`HELDOUT_PLAN.md`](working_documents/HELDOUT_PLAN.md)).

**Evidence at the gate.** Dev results for E1–E9, T1B and the EOP comparison (decisions 8 and 9). Dev pointed against H2 and H4 and showed a ceiling on H3 for the strong models. EOP extraction matched the visible state in 545 of 545 dev cases for the three models with prompt v2, and so did the parser.

**Decision A: the held-out protocol** ([`PREREG_FINAL.md`](../PREREG_FINAL.md); frozen 20:04 on 2026-11-14, commit `d00ada4`; first call logged 20:05).
- One run on 63 test families (468 states, 402 counterfactual pairs), four models, unchanged settings.
- Three families of confirmatory tests, Holm within each: F0 (H2, H3, H4a, H4b, as registered on 2026-11-04); F1 (EOP minus native, plan optimality); F2 (T-OI-1).
- EOP on the test split is the amended C′ for three models and the registered C for gemma. The registered C is not run on test for the other three: "it is a known instrument defect, and its dev results are the registered outcome."
- The parser condition P is reported as a baseline.
- This differs from the draft plan. The draft had the EOP comparison "exactly as in PREREG_EOP.md" (registered C for all models), listed both T-OI tests as candidates, and had no parser baseline.

**Rationale.** The protocol says what the run is and is not: for EOP it is "a prospective test of the amended method" and does "not turn the original registered experiment into a success". F0 was kept as registered although dev pointed against it. No correction is applied across the three families, and the protocol states this so that it can be judged.

**Decision B: the rewording study** ([`PREREG_ROBUST.md`](../PREREG_ROBUST.md); frozen 20:20, commit `35b983b`). 18 dev families, 137 states, four rewordings that keep the formal state (lexical, syntax, reorder, prose), 548 items. Conditions: native, structured prompt, EOP in its frozen configuration, EOP with a translating prompt (EOP-N), parser. One registered test: EOP minus native, pooled over wordings. Nothing found there may change EOP or cause a re-run on the test split.

**Rationale.** The benchmark's wording is regular and machine-generated, and a parser with no model matched EOP on it. The study asks whether the result survives rewording and whether a model extractor gives anything a parser does not. One fact was known in advance from the generator alone: the parser reads the reorder variants and none of the others. An independent reading of 24 sampled variants by a language model, not a person, recovered the true state in 24 of 24 and led to one wording fix before the freeze ([`ROBUST_AUDIT.md`](../ROBUST_AUDIT.md)).

**The outage and the first view.**
- From 19:57 on 2026-11-15 the provider answered every deepseek-v4-flash call with an error. The run was paused by hand at 20:22 so that calls that could not succeed would not use up their three attempts ([`network_guard.log`](../results/raw/network_guard.log)).
- At that point 30,009 of 31,036 calls had an answer; seven of eight chains had finished; deepseek's held-out chain was on its last step with its retry pass still to come ([`INTERIM_NOTE.md`](../results/aggregate/final_test/INTERIM_NOTE.md)).
- The project owner decided to look at the results then. This departs from the protocol, which says the results are analysed once, after every chain has finished.
- Before any summary was produced, a note was committed (commit `c3aed44`, 20:23:06) with a rule for the missing calls: resume with the same commands when the provider answers; if the calls finish by 00:00 on 2026-11-16, re-run the frozen analysis on the complete data and report that; otherwise apply the registered rule for running out of time; change no prompt, method, analysis or reporting choice because of the interim numbers; say in the report that the first view was incomplete. The first analysis started at 20:23:26 ([`final_finalize.log`](../results/raw/final_finalize.log)).
- The provider answered again at 20:55. The chain finished at 22:26, before the cut-off. The frozen analysis was run again at 22:36. Every reported held-out number is from this second run.
- Between the two runs only deepseek-v4-flash rows changed: native optimal-plan rate 0.73 with 108 unanswered items, then 0.98 ([`paper/report.md`](../paper/report.md) Appendix B).
- Seven calls, all of gemma +schema, failed all three attempts and count as wrong: four native planning calls and one decision call on the held-out split, one counterfactual-pair item and one rewording item ([`paper/report.md`](../paper/report.md) Appendix B; breakdown in [`paper/extended_report.md`](../paper/extended_report.md) Appendix C).
- Why the owner chose to look before the run had finished: Not recorded.

**Evidence: held-out results** ([`RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md); [`pilot_test/report.md`](../results/aggregate/final_test/v3/pilot_test/report.md)).
- Registered held-out, F0. H2 is supported for no model; for qwen3.5-397b and gemma the difference is significant in the opposite direction (Holm p 0.0001 and 0.0002). H3 is supported for qwen3.8-27b only (1.00 against 0.97, Holm p 0.008); for qwen3.5-397b and gemma the difference is significant in the opposite direction (Holm p 0.023 and 2.5e-13). H4a and H4b are supported for no model.
- Registered held-out, F2. Rate of acting on 169 newly sufficient states: 0.20 [0.14, 0.27] / 0.00 / 0.00 / 0.72 [0.64, 0.79]. Supported for qwen3.5-397b and gemma (Holm p < 0.001), not for the others (Holm p 1.0).
- Prospective test of the amended method, F1. EOP minus native: +0.07 [+0.04, +0.10] / +0.02 [+0.01, +0.04] / +0.02 [+0.01, +0.04] / +0.57 [+0.51, +0.62]; Holm p < 0.001 / 0.005 / 0.004 / < 0.001. EOP: 1.00 / 1.00 / 1.00 / 0.99.
- No-model baseline. Parser followed by the planner: 1.00.
- Descriptive. Native optimal-plan rate 0.93 / 0.98 / 0.98 / 0.42 (dev: 0.96 / 0.98 / 0.96 / 0.45). Structured prompt 0.62 / 0.96 / 0.94 / 0.40.

**Evidence: rewording study** ([`robust_report.md`](../results/aggregate/robust_dev/robust_report.md)).
- The parser scores 0.00 on three of four rewordings and 1.00 on the reorder wording.
- Registered test, EOP minus native pooled over wordings: +0.01 [−0.00, +0.03], Holm p 0.154 / +0.03 [+0.01, +0.06], Holm p 0.014 / −0.03 [−0.06, +0.00], Holm p 0.984 / +0.36 [+0.29, +0.43], Holm p < 0.001. Supported for qwen3.8-27b and gemma.
- On the syntax wording, deepseek's EOP falls to 0.81 while its native answer stays at 0.98; gemma's EOP falls to 0.05, below its native 0.35.

**Consequence.** Native planning replicated near ceiling for three models. The original planning hypotheses were mostly not supported. The EOP result on the benchmark's own wording was deflated by the parser. Under rewording the bottleneck moved to state extraction. The stopping result for qwen3.5-397b looked like the main remaining weakness of a strong model. The report written at that stage carried the claim "What remains is stopping", which the note at the top of [`paper/extended_report.md`](../paper/extended_report.md) marks as superseded. That reading was then tested (decision 11).

## 11. Three follow-up studies and what they changed (2026-11-15 to 2026-11-16)

**Research state.** The held-out results had been viewed at 20:23 on 2026-11-15. Two observations were open. First, the benchmark text says of every computational fact that "its certified value is not yet known", while the known-values line can list such a value; the independent reader of the rewording audit had noted this on 2026-11-14 in 18 of 24 texts ([`ROBUST_AUDIT.md`](../ROBUST_AUDIT.md)). Second, EOP failed under rewording mostly because the reader rejected the model's extraction.

**Evidence that motivated the studies** (exploratory). An analysis specified while the held-out run was in progress and before its analysis (commit `8efd1db`, 2026-11-14 22:12) splits unnecessary plans by whether they only re-obtain values the text lists as known. On the held-out split, 21 of the 34 unnecessary plans of qwen3.5-397b on newly sufficient states are of this kind ([`recertification.json`](../results/aggregate/final_test/recertification/recertification.json)).

**Decision.** Register and run three new studies on train-split families that no model had seen. They are new evidence and cannot become part of the held-out confirmation.

| Study | Registered | Question | Design |
|---|---|---|---|
| 1, wording clarity | 21:03 on 2026-11-15 ([`PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md); commit `fd8145c`) | Whether an unambiguous wording removes the stopping errors | 60 families, 436 states, each rendered in the benchmark wording and in a wording that differs in two lines only; three models |
| 2, cost sensitivity (the planned E10) | Same registration | Whether models follow the cheapest plan when one price crosses the point where it changes | 60 other families, 209 price sweeps, 780 items; three models |
| 3, extraction repair | 00:13 on 2026-11-16 ([`PREREG_REPAIR.md`](../PREREG_REPAIR.md); commit `2935522`) | Whether one repair call recovers extractions the reader rejects | 12 other families, 174 reworded items; gemma and deepseek; exploratory by its own registration, no test |

**Rationale.** Study 1: "The stopping errors may come from the wording, from the model, or from both." Study 2 replaces the decision of decision 5 by "the project owner's instruction of 2026-11-15 to run it"; the reason for the instruction: Not recorded. Study 3 follows from the rewording failures; a planned third arm with source-grounded extraction was not run because it would have required changes to frozen code. deepseek-v4-flash was left out of Study 1 because its capacity was reserved for finishing the held-out run; Study 2 lists the same three models without restating a reason.

**Evidence: results** (follow-up studies registered after the held-out results were viewed; each analysed once; [`followup_report.md`](../results/aggregate/followup/followup_report.md), [`repair_report.md`](../results/aggregate/repair/repair_report.md)).
- Study 1. Rate of acting on 256 already-sufficient states, benchmark wording → clarified wording: qwen3.5-397b 0.14 [0.09, 0.19] → 0.03 [0.01, 0.05], Holm p < 0.001; qwen3.8-27b 0.00 → 0.00, Holm p 0.368; gemma 0.73 [0.67, 0.79] → 0.59 [0.51, 0.66], Holm p < 0.001. With the clarified wording qwen3.5-397b no longer re-runs any computation whose result is given (0.10 → 0.00). The registration fixed two readings in advance. Applied to these intervals, the wording contributes for qwen3.5-397b and gemma (Holm p < 0.05), and the error persists without the ambiguity for gemma only (lower end of the clarified-wording interval above 0.05). The result file prints the numbers, not these verdicts.
- Study 2. Cheapest plan just above / just below the price boundary: qwen3.5-397b 0.95 / 0.97; qwen3.8-27b 0.95 / 0.98; gemma 0.31 / 0.16. Cost insensitivity is supported for gemma only (Holm p 0.0003; 1.0 for both qwen models).
- Study 3. gemma with its frozen prompt: exact state 0.21 → 0.78 with one repair call; accepted-but-wrong extractions 0.07 → 0.16. deepseek: 0.89 → 0.97, with no accepted-but-wrong extraction. The paired interval of the rise in accepted-but-wrong extractions, which the registration names, was not printed by the frozen analysis; it was computed afterwards by a separate script: +0.09 [0.03, 0.15] for gemma ([`repair_supplement.json`](../results/aggregate/repair/repair_supplement.json); commit `1b6af3b`).
- Study 3 also showed a reader artifact: gemma's "empty" answers under the translating prompt in the rewording study were answers written as plain text. The rewording figure therefore understates EOP-N for gemma ([`paper/report.md`](../paper/report.md) §4.4).

**What changed.**
- The stopping claim was narrowed. For qwen3.5-397b, most of the over-intervention first measured came from the ambiguity in the benchmark's own text. The registered held-out result (F2) stands as measured; its interpretation changed ([`paper/report.md`](../paper/report.md) §4.2, §5; [`paper/extended_report.md`](../paper/extended_report.md), note at the top).
- gemma's stopping failure remains under either wording, and its cost insensitivity was added as a finding.
- The expectation of decision 5 that strong models would be at ceiling on cost changes was confirmed for the two qwen models.
- The submission report was restructured around these findings (commit `de44402`); the earlier long report is kept as [`paper/extended_report.md`](../paper/extended_report.md).

**Consequence.** A limitation was added to the benchmark itself: a text that states what is known inconsistently measures how a model resolves the inconsistency. The frozen benchmark text was not changed. Study 1 used the two wordings side by side on new items.

## 12. Final conclusions (2026-11-16)

**Research state.** All registered runs and the three follow-up studies were complete and analysed.

**Evidence.** The result files cited in decisions 7–11 and the summary in the [hypothesis tracker](hypothesis_tracker.md).

**Decision.** State the conclusions of [`paper/report.md`](../paper/report.md) Sections 4–6 and keep every negative result, amendment and deviation visible.

| Hypothesis or claim | Verdict | Tier of the deciding evidence |
|---|---|---|
| H1: substantial planning error remains once detection is controlled | Did not survive for the three stronger models: none of their items fails in all three modes. Remains for gemma (0.07 of items). No test. | Exploratory |
| H2: diagnosis is easier than planning | Did not survive. Reversed for two models. | Registered held-out |
| H3: relevance is confused with sufficiency | Survived for one model with a small effect. Reversed for two models. | Registered held-out |
| H4: states needing both resources are harder | Did not survive. | Registered held-out |
| H5: minimality and stopping are distinct weaknesses | Survived for the weakest model: its plans are usually sufficient, rarely cheapest, and it keeps acting when nothing is needed. For the strong models the plans are near-minimal; deferral on unresolvable states is imperfect (0.87–0.97). | Exploratory; stopping also registered held-out (F2) and follow-up Study 1 |
| H-OI: models keep acting after a state becomes sufficient | Supported as registered for qwen3.5-397b and gemma. For qwen3.5-397b most of the effect is an artifact of the benchmark wording. Not shown to be specific to the edit. | Registered held-out; follow-up Study 1 |
| H6 as planned (against confidence-based and routing baselines) | Never tested. | — |
| H6 as registered (EOP with prompt v1 against native) | Did not survive for three of four models. | Registered development |
| Amended EOP against native | Supported for all four models; large only for gemma; matched by a parser with no model on the benchmark's wording. | Prospective test of an amended method; no-model baseline |
| EOP under rewording | Holds for the two qwen models, breaks for deepseek and gemma. | Rewording study |

**Rationale.** [`paper/report.md`](../paper/report.md) is the authoritative statement. Its summary: planning on a correct formal state is reliable; obtaining that state from language is the open problem.

**Consequence: what remains open.**
- Faithful translation from language to a formal state, including abstention when a text has more than one reading. Repair recovers most rejected extractions and adds some well-formed wrong ones.
- The computation-capability control (E14), risk sensitivity (E11), structural shift (E12), external validity (E13), relevance against necessity (T3), the hybrid planner (S4) and the comparison with a learned router (S5) were not run.
- Sequential plans, probabilistic sufficiency, closed frontier models, repeated sampling and rewordings written or audited by people are outside the evidence.
- Cost sensitivity and the clarity study were not run for deepseek-v4-flash.
- The benchmark text keeps the ambiguity that Study 1 measured.
