# Research gap and novelty boundary

This document answers three questions: what did prior work already cover, which combination does this project evaluate, and what does the project explicitly not claim? It also reproduces the statement of reuse of the author's earlier code. It is based on [`working_documents/NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) (positioning cutoff 2026-11-02, with source checks on 2026-11-03 and 2026-11-13), [`working_documents/PRIOR_WORK.md`](working_documents/PRIOR_WORK.md), [`working_documents/PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §15 and [`../paper/report.md`](../paper/report.md), which is the authoritative statement of the final claims. Reference numbers follow [`literature_timeline.md`](literature_timeline.md), Section 15.

## 1. What prior work already covers

The novelty map was written to prevent accidental over-claiming. For each area it names the prior work and concludes that the area is not a contribution of this project.

| Area | Prior work named in the repository | Conclusion recorded |
|---|---|---|
| Uncertainty, confidence, calibration | Work on whether LLM confidence tracks correctness and whether token-level or semantic uncertainty predicts errors [12]–[14] | Not our novelty |
| Abstention, selective prediction | Work on when models should answer or abstain [16] | Not our novelty |
| Adaptive retrieval, information seeking | Work on whether models know when to retrieve or ask [15], [17], [18], [22] | Not our novelty |
| Minimal sufficient information | MT-InfoSeek [1] formalises information seeking as a k-underspecified CSP and tests whether models find a minimal sufficient set of queries. QuestBench [36] covers the case of one missing value | "Minimal sufficient information" alone is not novel |
| Adaptive computation, value of computation | Rational Metareasoning [7]; DIAL [4] shows that compute need and compute suitability differ | "When should the model think more?" is not novel |
| Ask, act or repair with solver-grounded labels | "Ask, Relax, or Act?" [2], with matched pairs | Solver-grounded next-action evaluation is not novel by itself |
| Counterfactual action outcomes | SURE-Act [3] executes each legal action and trains a controller | Counterfactual action value with a learned controller is not novel by itself |
| Evidence-state diagnosis followed by an action policy | EPRAG [26]†, as the working documents describe it; its content was not read and the description is unconfirmed | "Diagnose the state, then choose an action" is not claimed as novel |
| Tool sufficiency | ToolChoiceConfusion [5], a filter that uses symbolic tool contracts | "A relevant tool is not a sufficient tool" is not a standalone claim |
| Querying versus simulating in a planner | Active Epistemic Control [6] | Partial overlap; cited. Epistemic control is not our contribution |
| Diagnosing the cause of uncertainty | ConfuseBench [19], with three causes, one of them limited capability | Diagnosis of the cause of uncertainty is not new |
| Retrieving versus thinking | EvoCtx [27]; Lacombe et al. [29] compare search with longer reasoning | The choice between retrieving and thinking is not new |
| Solver-backed pipelines from language | Logic-LM [R11], LINC [R12], grammar-constrained decoding [R13], roundtrip verification and repair [R15] | Solver-backed planning is not claimed as new |

Sources: novelty map §1 and §9; [`../paper/literature_review.md`](../paper/literature_review.md), Part B ("What we do not claim") and Part D, item 12; `paper/report.md` §2.

## 2. The combination this project evaluates

**The candidate gap as first written.** The novelty map states that the author did not find prior work that combines all of the following as one exact LLM evaluation problem (novelty map §2):

1. a single action space containing information-acquisition actions and computation or verification actions;
2. latent states that require information only, computation only, both, or neither;
3. an exact formal oracle for whether a candidate intervention is sufficient;
4. exact or provable minimal sufficient plans, not only relevant actions;
5. mixed plans that require both resource types;
6. explicit unresolvable (neither) cases;
7. evaluation that separates uncertainty detection, resource diagnosis and exact plan construction;
8. a mitigation based on explicit epistemic obligations, not only on scalar confidence or learned routing.

**How the final project realises each point.** The table states what was built and where it is limited.

| Point | As realised | Limit | Source |
|---|---|---|---|
| 1 | Priced information actions and certified computation actions in one menu | A computation is certified and never depends on hidden world facts | `paper/report.md` §3.1 |
| 2 | Five resource classes: ALREADY_SUFFICIENT, INFORMATION_ONLY, COMPUTATION_ONLY, BOTH, NEITHER | NEITHER is relative to the action menu; states whose cheapest plans tie across compositions are excluded | [`../paper/extended_report.md`](../paper/extended_report.md), Appendix D |
| 3 | Sufficiency decided by SAT and MaxSAT; every label re-verified by brute force: 228,199 checks, 0 failures | Deterministic logical sufficiency only; the posterior-threshold rule is not in the benchmark | [`../results/oracle_validation.md`](../results/oracle_validation.md); `paper/report.md` §3.1 |
| 4 | Every state is labelled with all its cheapest sufficient plans; any tied cheapest plan counts as optimal | Static plans: a set of actions chosen before any result is seen | `paper/report.md` §3.1, §3.3 |
| 5, 6 | BOTH and NEITHER siblings in each of 300 families (2,282 states) | Small synthetic propositional problems in generated language | `paper/report.md` §3.2 |
| 7 | Three modes: End-to-End, Detection-Controlled, Diagnosis-Controlled | ConfuseBench [19] already separates one kind of diagnosis | `paper/report.md` §3.3 |
| 8 | The Epistemic Obligation Planner: the model extracts the formal state and an exact planner returns a cheapest hitting set of the obligations | Compared with the native answer, a structured prompt, a verifier-only variant and a parser with no model. The confidence-based policy and the learned router named in the novelty map (§5) were not built; no ask-versus-think heuristic is recorded as built | `paper/report.md` §3.4; [`../docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §3, notes |

**The statement of the gap in the report.** "We did not find one that puts information and computation in one priced action space and scores, against an exact answer, whether a plan is *sufficient* and *minimal*." And: "Our contribution is a controlled evaluation of *minimal sufficient plans over two kinds of epistemic resource*, with states that need either, both or neither, an exact oracle, and a measured account of where a formal mitigation works." (`paper/report.md` §1, §2).

**Safe wording recorded in the novelty map (§3).** "We introduce a controlled benchmark for testing whether LLMs can identify minimal sufficient epistemic plans across heterogeneous information and computation resources, while separating insufficiency detection from resource diagnosis and plan construction." The novelty map adds: do not say "the first" until the final literature sweep.

## 3. How the boundary was checked

**Kill conditions.** The novelty map (§7) commits to re-scoping at once if a paper is found that already provides all of: an exact heterogeneous information and computation action space; minimal sufficient mixed plans; both and neither cases; an exact oracle; separate detection-controlled and diagnosis-controlled evaluation; and a mitigation through formal obligations or planning. Partial overlap is expected and is to be cited.

**Checks made.**

| Date | Check | Result | Source |
|---|---|---|---|
| 2026-11-03 | Reference check through search results and mirror pages (arxiv.org and sciencedirect.com were not reachable; only one page was opened directly) | One wording corrected (MT-InfoSeek); "Ask, Relax, or Act?" found only on an aggregator page; SURE-Act not found; one description of EPRAG not seen and its date questioned (possibly late August rather than 2026-10-25); Active Epistemic Control [6] and reference [8] newly found; no work meeting all kill conditions. The note asks for every source to be re-checked directly | Novelty map §9 |
| 2026-11-13 | Six papers opened on arxiv.org and read | All six exist at the cited ids. None meets all kill conditions: "none combines an exact heterogeneous information + computation action space with minimal sufficient mixed plans, BOTH/NEITHER cases and an exact oracle" | Novelty map §9a; [`working_documents/LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md) |
| 2026-11-14 | The author's 28-entry list checked reference by reference | 24 verified at the source at abstract level or better; 4 from Crossref records only († entries [10], [11], [25], [26]); two works found to touch the boundary ([19], [27]) and cited for it | `paper/literature_review.md`, Part D |
| 2026-11-15 | Final literature check | QuestBench [36] found and cited | `paper/report.md`, reference 5; git history, commit `a635ddd` |

**What remains open.** The novelty map (§8) lists eight search queries to repeat within 24 hours of submission. The review of 2026-11-14 states that this sweep was not run as part of that task (Part D, item 15). Whether the full list of queries was repeated in the final check of 2026-11-15 is not recorded. The candidate list is not a systematic literature search. For these reasons the wording is "we did not find", with a literature cutoff of 2026-11-02, and not "first".

## 4. What the project explicitly does not claim

**About the field.** The project does not claim that any of the following is new: uncertainty detection; calibration; abstention; adaptive retrieval; adaptive computation; retrieving versus thinking; diagnosis of the cause of uncertainty; minimal sufficient information; minimal sufficient computation or reasoning; the gap between relevance and sufficiency; counterfactual action utility; epistemic planning; information seeking; solver-backed planning (`working_documents/PROBLEM_SPEC.md` §15; `paper/literature_review.md`, Part B; `paper/report.md` §2).

**About other papers' findings.** The project does not claim as its own finding that models underestimate missing information [1], that uncertainty is a poor guide to compute need [4], that output format changes decisions [2], or epistemic control as such [6] ([`working_documents/CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §4).

**About priority.** The project does not claim to be first.

**About its own results.** The final report bounds its claims as follows (`paper/report.md` §5 and Appendix A).

- The tasks are small synthetic logic problems in generated language. The results are not evidence about open-ended decisions, and no transfer to natural tasks is claimed.
- The Epistemic Obligation Planner measures extraction, not planning: its planner is exact, and on the benchmark's own wording a parser with no model also scores 1.00 (no-model baseline; [`../results/aggregate/final_test/RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md)). A high score on the canonical benchmark is not a certificate of good epistemic behaviour.
- The version of the mitigation tested on held-out data was fixed after seeing development data. The held-out result is a prospective test of an amended method; it does not turn the registered development experiment, which failed for three of four models, into a success.
- The registered hypotheses were mostly not supported on the held-out split. The project does not claim that diagnosis is easier than planning, that relevance is generally confused with sufficiency, or that states needing both resources are harder (registered held-out; `paper/report.md` §4.1).
- The project does not claim that strong models have a general stopping failure. The registered held-out measurement of over-intervention stands as measured (qwen3.5-397b 0.20 [0.14, 0.27]); a follow-up study registered after the held-out results were viewed shows that most of it came from an ambiguity in the benchmark text (0.14 falls to 0.03 with clarified wording) ([`../results/aggregate/followup/followup_report.md`](../results/aggregate/followup/followup_report.md)).
- Four open-weight models from one provider were run at temperature 0 with one answer per item. No closed frontier model was run and there is no estimate of run-to-run variation.
- "Minimal" means the cheapest among sufficient plans. The work must not be cited to justify fewer checks without a sufficiency guarantee.
- The correspondence between the oracle and the logic of sufficient and necessary reasons [30, 31] is the project's reading; the cited papers do not state it, and the project is described as related to that work, not as building on it.

## 5. Reuse of the author's earlier code

`working_documents/PRIOR_WORK.md` separates existing infrastructure of the author from new work. Its rules: generic solver wrappers, exact logical semantics and similar utilities may be reused; old experiments must not be presented as new results; the earlier projects' research questions must not be used as this project's novelty; every reused module must be disclosed with its source, commit and changes (§1, §5). Findings of the earlier project STML (deeper logical problems can lower accuracy while confidence stays high; certificate-style checks can outperform raw confidence; thresholds may fail under structural shift) are background, not results of this project (§1).

**Reuse record (2026-11-03), as `PRIOR_WORK.md` §8 records it.** The earlier repositories were cloned read-only and inspected. Code was reused only after it was checked against an independent computation.

| New module | Source | Reuse type | What changed and how it was checked |
|---|---|---|---|
| `src/msep/world/compute_tasks.py` (`SyllogismFollows`) | STML `stml/logic.py`, commit `15646ecab33603a060bd97d9e13561e36781e67e` | Adapted (region semantics for the four categorical forms with existential import, about 30 lines) | Rewritten as plain functions over tuples. Used only as one simple computation-task kind in the random oracle-validation instances; since 2026-11-03 benchmark families use the certified tasks instead. Checked against independent brute-force model enumeration: 1,860 random consistent cases before reuse, and again in `tests/test_compute_tasks.py` |
| `src/msep/oracle/logic.py` | STML `stml/referee.py`, same commit | Conceptual only | Same style (pysat CaDiCaL, assumption literals on a persistent solver). No code copied. New two-copy distinguishing-pair encoding |
| Methodology | STML | Conceptual | An independent SAT referee that shares no reasoning code with the enumerator, with 100% agreement required |
| — | PathCompiler, commit `a7251b77bae01f9e0d560120246ffd73aaa547ad` | None | Inspected. Not reused: the project is Python and pysat covers the needs |
| — | epistemic-search, commit `3206cda687a738c181ea3508461c0975a7ad6fa4` | None; will not be reused | Out of scope. It was cloned and read once on 2026-11-03, before it was ruled out. Decided 2026-11-03: no code or design from it is used. The statistics code of this project was written independently, to avoid any ambiguity of provenance |

STML's own test suite passed at the inspected commit (24 tests). No STML or PathCompiler experiment results are used or reported. Everything else in `src/msep/` was written new for this project (`PRIOR_WORK.md` §8).

**The same statement in the report.** "About 30 lines of syllogism semantics from an earlier project, used only in random oracle-validation instances and checked against brute force. No results from earlier projects are reported." (`paper/report.md`, Appendix B).

**Before the sprint and during it.** The formal model, the exact oracle and its validation, the benchmark templates and shortcut audit, the planner code, the evaluation code and the evaluation protocol were built on 2026-11-03 and 2026-11-04, before the sprint; no language model had been called. The report gives the sprint as 2026-11-13 to 2026-11-15 and lists as built during it the provider integration, every model run, the counterfactual pairs, the mitigation comparison, the held-out evaluation, the rewording study and the three follow-up studies (`paper/report.md`, Appendix B). The report marks its first contribution, the formal task, oracle and benchmark, as "built before the sprint".
