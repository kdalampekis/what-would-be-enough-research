# Future research

This document answers one question: which questions does the project leave open, and in what order of importance? It follows the Future Work paragraph of [`../paper/report.md`](../paper/report.md): first, faithful translation from natural language to a formal state; then sequential plans, sufficiency as a probability threshold, and tasks written by people. It ends with the experiments that were planned and not run, from [`working_documents/ROADMAP_MATRIX.md`](working_documents/ROADMAP_MATRIX.md) and [`../docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.14. Nothing here is a result. Where a direction is supported by one of the project's results, the result is cited with its evidence tier. Reference numbers follow [`literature_timeline.md`](literature_timeline.md) and [`literature_review.md`](literature_review.md).

## 1. Faithful translation from natural language to a formal state

**Why this comes first.** The mitigation of this project, the Epistemic Obligation Planner, has the model extract a formal state and lets an exact planner choose the actions. Given the right formal state, the planner solves the task and its stopping decisions are verified. The open part is the translation from language. The report states it as the step that limits the mitigation and as where the next work should go (`paper/report.md` §5, §6).

**What the results show about this step.**

- On the benchmark's own wording a parser with no model extracts every state (no-model baseline). On reworded text the parser scores 0.00 on three of four rewordings, and the model extractor holds for two models and breaks for two (rewording study, registered separately; [`../results/aggregate/robust_dev/robust_report.md`](../results/aggregate/robust_dev/robust_report.md)).
- Most extraction failures are visible, because the planner rejects a malformed extraction. The exception in the rewording study is gemma on the prose wording, where 24 of 137 extractions are well-formed and wrong (`paper/report.md` §4.3).
- One repair call recovers most rejected extractions and adds some silent errors (Study 3; exploratory follow-up, registered after the held-out results were viewed). With gemma's frozen prompt the exact-state rate rose from 0.21 to 0.78. Of 125 rejected first answers, 98 were recovered exactly, 12 stayed rejected and 15 became well-formed but wrong, so accepted-but-wrong extractions rose from 0.07 to 0.16 (rise +0.09 [+0.03, +0.15]). For deepseek the exact-state rate rose from 0.89 to 0.97 with no accepted-but-wrong extraction ([`../results/aggregate/repair/repair_report.md`](../results/aggregate/repair/repair_report.md); [`../results/aggregate/repair/repair_supplement.json`](../results/aggregate/repair/repair_supplement.json)).

A rejected extraction is an error the system can see. An accepted but wrong extraction is one it cannot see, and it yields a confident wrong plan (`paper/report.md` §5). Study 3 shows that a repair step driven by the reader's error messages can turn the first kind into the second. This is why checks of form are not enough.

**The directions the report names.**

| Direction (as named in the report) | What it would test (our gloss of the report's phrase) | Status in this project |
|---|---|---|
| Source-linked extraction | The model cites the source sentence of every rule it extracts, so each element of the formal state can be traced to the text | A source-grounded, typed extraction arm was planned for Study 3 and not run: the forced output schema of one model and the frozen runner accept only the existing layout ([`../PREREG_REPAIR.md`](../PREREG_REPAIR.md) §0) |
| Agreement between independent formalizations | Whether two extractions made independently agree, as a signal of a faithful state | Not run |
| Roundtrip checks [R15] | Whether a state, rendered back to text and re-read, returns the same state | Not run on model extractions. The benchmark's own rendering has a model-free round trip with 0 mismatches on all 2,282 states ([`../paper/extended_report.md`](../paper/extended_report.md), Appendix D) |
| Abstention on ambiguous text | Whether the extractor declines when the text has more than one reading | Not run. The benchmark text itself contained one such ambiguity, which Study 1 measured (`paper/report.md` §4.2) |

**The limit of consistency checks.** The report states that consistency alone cannot show that a formal state matches the text [R14]; a formalization can be well-formed and still unfaithful (`paper/report.md` §2, Future Work). Agreement between formalizations and roundtrip checks test consistency, so their value has to be measured against the true state (our reading of the report's sentence). The report's answer is that this benchmark supplies the exact references such an evaluation needs: for every text the true formal state is known, and for every state all cheapest sufficient plans. The effect of an extraction error can therefore be measured twice: on the exact state, and on the plan that an exact planner derives from it.

**Further points recorded in the repository.**

- Constrained decoding for the extraction step [R13] is listed as future work in the extended report and was not tested.
- A reading artifact should be removed before further comparisons: under the translating prompt, one model wrote its answers as plain text instead of the forced function call, and the rewording study counted them as empty. Read as text, that prompt gives the exact state on 0.67 of the Study 3 items, so the rewording figure understates that condition for that model (`paper/report.md` §4.4).
- The rewordings come from the project's own templates and were audited by a language model on 24 texts, not by people (`paper/report.md`, Appendix A). Text written or audited by people is needed before claims about natural language can be made.
- A deployed version should show the extracted state before acting on it (`paper/report.md`, Appendix A, dual-use considerations).

## 2. Sequential plans

Every result of this project is about static plans: a set of actions chosen once, before any result is seen, that must settle the answer whatever the results are. Conditional plans, in which the next action depends on an earlier result, and order-dependent actions were specified and not implemented (extended report, Appendix D).

- The problem specification defines this as Level 4 and fixes its objective in advance: expected cost or expected utility over outcome branches, with worst-case cost as a secondary measure ([`working_documents/PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §12).
- The challenge-tier design lists it as T4. It needs a new oracle for contingent policies (policy trees, expected cost, worst-case sufficiency) and new scoring, and must not be scored with the static-plan oracle. The design calls it a project of its own ([`working_documents/CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §3).
- MT-InfoSeek [1] studies the order of queries only observationally, in one domain ([`working_documents/LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md) §1). The design document's judgment is that a controlled version "would be new"; this rests on the project's candidate literature list, not on a systematic search.

## 3. Probabilistic sufficiency

The benchmark uses deterministic logical sufficiency: a plan is sufficient only if it guarantees the answer. Sufficiency as a probability threshold was kept apart, because it is not monotone in information and the obligation properties used by the oracle do not hold for it (`working_documents/PROBLEM_SPEC.md` §6).

- The experiment planned for it is E11, risk sensitivity. Its variants are frozen and no model was run (`docs/EXPERIMENT_INDEX.md` §4.14).
- The extended report names the same-decision probability [32] as the natural tool: the probability that a threshold decision stays the same once hidden variables are observed. The posterior-threshold rule of this project is validated in the oracle and is not in the benchmark ([`../paper/ucla_related_work.md`](../paper/ucla_related_work.md) §1).
- A related open question is computation that can mislead. In this project a computation is certified and never lowers sufficiency. A test of "computation can hurt", as DIAL [4] reports for its setting, needs a separate setting with approximate or stochastic computation (failure map §4). Probabilities and noisy sources are outside this work (`paper/report.md`, Appendix A).

## 4. Tasks written by people

The tasks are small synthetic propositional problems in regular, machine-generated language, and the results are not evidence about open-ended decisions (`paper/report.md`, Appendix A).

- The planned experiment is E13, external validity. The plan names transformations of existing reasoning datasets ([`working_documents/EXPERIMENT_PLAN.md`](working_documents/EXPERIMENT_PLAN.md) §5). Only a converter exists; no external dataset was processed (`docs/EXPERIMENT_INDEX.md` §4.14).
- Section 1 applies here first: on text that people write, the formal state must be extracted before any plan can be scored, and there is no generator to supply the true state.

## 5. Experiments planned and not run

The table lists what the plan contained and what exists. The first two columns follow `working_documents/ROADMAP_MATRIX.md` (2026-11-14) and `docs/EXPERIMENT_INDEX.md` §4.14.

| Item | Purpose | What exists | Status |
|---|---|---|---|
| E11 risk sensitivity | Whether models change the plan or defer when the penalty or threshold changes | Frozen variants; analysis not wired into the driver | Not run |
| E12 structural shift | Generalisation to deeper or larger structures and unseen renderings | Variants with a theme shift only | Not run. The rewording study is not E12 |
| E13 external validity | Transfer to external tasks | Converter only | Not run |
| E14 computation-capability control | Whether a model that can do a computation in its head skips the certified action more often | Opt-in runner and analysis | Not run. Until it is run, how much the certified-computation convention matters is unmeasured (extended report, Appendix D; [`../PROTOCOL.md`](../PROTOCOL.md) §9) |
| T2 information-source switching | The same unknown reachable by information or by certified computation | Design text; a semantics decision is open | Not run (`CHALLENGE_V4_DESIGN.md` §3) |
| T3 necessity versus relevance | The model's own pruning at fixed action count and prompt length | Design text only | Not run |
| T4 conditional sequential planning | Section 2 | Design text only; needs a new oracle | Not run |
| T6 unseen structural families | A held-out rule motif | Not built | Not run (`CHALLENGE_V4_DESIGN.md` §3) |
| S4 hybrid planner | Action effects estimated by a model | Not built | Not run |
| S5 shift robustness against a learned router | The mitigation against a router under shift | Not built; no learned router exists | Not run |
| Confidence-based, ask-versus-think and routing baselines | Comparisons named for the mitigation in the plan | Not built | Not run (`docs/EXPERIMENT_INDEX.md` §3, notes) |
| Source-grounded extraction arm of Study 3 | Section 1 | Planned in the registration | Not run (`PREREG_REPAIR.md` §0) |
| 64 development counterfactual pairs of the 10 calibration families | — | Generated; in no item set | Not run |

**One item changed status.** E10, cost sensitivity, is listed as not run in the roadmap matrix and in the experiment index, both written on 2026-11-14. It was run afterwards as follow-up Study 2, by a decision of 2026-11-15 recorded in [`../PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md) §0. Its result is a follow-up result, registered after the held-out results were viewed.

## 6. Other open points from the limitations

- **More models and repeated runs.** Four open-weight models from one provider were run at temperature 0 with one answer per item. No closed frontier model was run, and there is no estimate of run-to-run variation (`paper/report.md`, Appendix A).
- **Stopping, re-measured.** Study 1 measured the effect of the ambiguous wording on fresh train families. The extended report lists a corrected benchmark text, to re-measure stopping without the ambiguity, as future work. Study 1 used train families only, and the held-out data, prompts and results were not changed ([`../PREREG_FOLLOWUP.md`](../PREREG_FOLLOWUP.md) §0).
- **Deferral.** With the ambiguity removed, what remains for the strong models is imperfect deferral when nothing available can settle the question: 0.89, 0.87 and 0.97 on the held-out split (descriptive, no registered test; [`../results/aggregate/final_test/RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md)). Why they act on the remaining states is not analysed. Not recorded.
- **The weak model's profile.** gemma's plans are usually sufficient and rarely the cheapest, ignore prices, and continue when nothing more is needed (`paper/report.md` §5). It was observed in one model. Whether other models share it was not tested.
- **Literature.** The candidate list is not a systematic search. Whether the full list of search queries in the novelty map was repeated before submission is not recorded ([`research_gap_and_novelty.md`](research_gap_and_novelty.md), Section 3).
