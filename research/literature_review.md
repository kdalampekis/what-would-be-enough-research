# Literature review: the closest related work, paper by paper

This document answers one question: for each of the papers closest to this project, what did it ask, do and find, where does it stop, and how does this project differ from it? It gives the detailed analysis behind the short Related Work section of [`../paper/report.md`](../paper/report.md). It covers MT-InfoSeek, QuestBench, "Ask, Relax, or Act?", SURE-Act, DIAL, ToolChoiceConfusion, Active Epistemic Control, EPRAG and the language-to-logic papers cited in the report, then gives one comparison matrix and a table of which experiments each paper motivated. The chronological view of the whole field is in [`literature_timeline.md`](literature_timeline.md). Everything here is taken from repository documents. Where those documents do not record something, the text says "not stated in our notes" or "Not recorded".

## 1. Basis and conventions

**Sources.** Six papers were opened on arxiv.org and read on 2026-11-13; the notes, with the location of each number and the parts not read, are in [`working_documents/LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md) ("failure map"). On 2026-11-14 the author's 28-entry candidate list was checked reference by reference; the log is Part D of [`../paper/literature_review.md`](../paper/literature_review.md) ("review"). Work related to the oracle's logic and to behavioural motivation was checked the same day in [`../paper/ucla_related_work.md`](../paper/ucla_related_work.md). The list is a candidate list with a cutoff of 2026-11-02; it is not a systematic search.

**Reference numbers** follow [`../paper/extended_report.md`](../paper/extended_report.md): [1]–[36]. [R11]–[R15] are references 11–15 of `paper/report.md`.

**Whose statement is it.** "The authors report" marks numbers and claims read in the paper. "Our note" marks an observation of this project about the paper (the failure map marks these "mine"). A paper's results are never restated as findings of this project.

**Our own results** are mentioned only to show a relation, each with its evidence tier: registered held-out; registered development; prospective test of an amended method; rewording study; follow-up studies registered after the held-out results were viewed; exploratory or diagnostic; no-model baselines.

## 2. MT-InfoSeek [1]

Huang et al. (2026). "Do LLMs Know What to Ask and When? Evaluating Multi-Turn Information Seeking." arXiv:2608.14808, v1 2026-08-14. Links: https://arxiv.org/abs/2608.14808 ; Microsoft Research page as cited in the working timeline: https://www.microsoft.com/en-us/research/publication/do-llms-know-what-to-ask-and-when-evaluating-multi-turn-information-seeking/

- **What was read.** Abstract, introduction, §4, §5, Appendices A, B, C.1–C.6, D.1–D.3 and the project page. Not read verbatim: §3.2–3.3, Appendices E–G, figures (failure map §1).
- **Research question.** Whether models can tell which variables they must learn so that the answer becomes uniquely determined, and when to ask for them.
- **Method.** Information seeking as a k-underspecified constraint satisfaction problem. The target is known when all feasible assignments agree. A minimal k-sufficient set is a sufficient set of k variables with no smaller sufficient set. Tasks: predict k; identify the minimal sufficient set with or without k; solve sequentially (up to 10 turns; 20 in a twenty-questions setting).
- **Models and settings.** 5,251 problems and 9,006 task instances. GPT-5, GPT-5-mini, Gemini-3-Flash, Qwen3-4B-Thinking, Qwen3-30B-A3B-Thinking-FP8, gpt-oss-20B; a subset adds Gemini-3.1-Pro, gpt-oss-120B, Qwen3-Next-80B-A3B-Thinking-FP8 and the Qwen3.5 family. LLM oracles answer the questions in two domains.
- **Main findings as the authors report them.** Models almost never predict k=0 ("0.6±0.8%"). Accuracy in predicting k is "below 0.50 for k≥2", with under-prediction more than four times as common as over-prediction at k=2. With free choice of queries, "no model exceeds 0.4 accuracy at k=2 or 0.2 at k=3"; giving the true k helps "only modestly". With one query per turn in one setting, models "stop too early and directly guess".
- **Failure modes.** Underestimating how much is missing; failing to find the exact set even when k is given; early stopping under forced one-per-turn querying; lower accuracy with a poor query order.
- **Limitations.** Stated by the authors: no noisy users, all queries cost the same, LLM oracles, missing variables are the only kind of underspecification, and every problem admits a sufficient set by construction. Our notes: model lists differ across settings; the twenty-questions setting is one problem; correlations are over 6–14 models; question order is studied in one domain only, observationally, and no experiment forces a wrong order. One table may show a model near ceiling on one logic set (not read verbatim), so "models fail" should not be stated without qualification.
- **Relation to this project.** It is the closest work on the information side. It already formalises minimal sufficient query sets, so "minimal sufficient information" is not a contribution of this project ([`working_documents/NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) §1).
- **What this project does differently.** Plans mix information with certified computation; actions have unequal costs; an exact oracle scores every plan; the state classes include BOTH, NEITHER and ALREADY_SUFFICIENT. MT-InfoSeek's starting states always need at least one query, although it offers k=0 as an answer and reports an over-questioning rate (review, Part D, item 2).
- **Experiments it motivated.** The failure map derives no new test from its underestimation finding ("none new"). Its observational order finding is the anchor for T4, a controlled test of conditional sequential plans, which needs a new oracle and was not run ([`working_documents/CHALLENGE_V4_DESIGN.md`](working_documents/CHALLENGE_V4_DESIGN.md) §3).
- **Would be redundant.** Reporting only information-only minimal sets, equal costs or prediction of k, or claiming "models underestimate missing information" as our finding (failure map §1, item 6).

## 3. QuestBench [36]

Li, Kim and Wang (2025). "QuestBench: Can LLMs ask the right question to acquire information in reasoning tasks?" NeurIPS 2025, Datasets and Benchmarks Track; arXiv:2503.22674. Link: https://arxiv.org/abs/2503.22674

- **What was read.** The reference was confirmed on the arXiv page on 2026-11-15 (`paper/report.md`, reference 5). It was found in the final literature check and is not in the failure map or in the review's verification log.
- **Research question and method.** It gives problems with exactly one missing value and asks for the one question that settles them (`paper/extended_report.md` §2).
- **Models and settings.** Not stated in our notes.
- **Main findings as the authors report them.** 40–50% accuracy on its logic and planning sets.
- **Failure modes.** Not stated in our notes beyond the accuracy above.
- **Limitations.** Our note, shared with MT-InfoSeek: queries cost the same, a sufficient set always exists, and no computation is on offer (`paper/report.md` §2).
- **Relation and difference.** It is the one-missing-value case of the question "what to ask". This project asks for a cheapest set of actions over two kinds of resource, including states that need nothing and states that nothing can settle.
- **Experiments it motivated.** None. Not recorded as a motivation for any experiment; it was found on 2026-11-15, after the held-out evaluation and the rewording study were designed (git history, commit `a635ddd`), and no later registration names it.

## 4. "Ask, Relax, or Act?" [2]

Li et al. (2026). "Ask, Relax, or Act? Evaluating Actionable Indeterminacy in LLM Preference Reasoning." arXiv:2610.03102, v1 2026-10-02. Link: https://arxiv.org/abs/2610.03102

- **What was read.** Abstract, §1–6, Appendices B.3–I.1, most tables. Not read verbatim: Appendices A, B.1–B.2, I.2–P. The table of contents has no limitations section (failure map §2).
- **Research question.** Whether a model can tell if it can act on the available information, must ask, or must relax a constraint.
- **Method.** Four task structures (object allocation, meeting scheduling, apartment choice, stable matching) at three sizes and three seeds. One information source varies per task (preferences, objectives, constraints). Exact solvers label each task Act, Ask-Preference, Ask-Objective or Relax. Matched pairs: each pair "changes whether intervention is necessary". The measure IFC counts a pair as correct only if both members are right.
- **Models and settings.** 4,320 prompts in the common subset (720 pairs per source). GPT-6-Astra, Claude-5-Sonnet, Gemini-3.1-Pro, gpt-oss-120b; single turn, no tools.
- **Main findings as the authors report them.** Pair correctness is well below item accuracy: GPT-6-Astra 92.57% accuracy against 85.56% IFC; Claude-5-Sonnet IFC 76.39; gpt-oss-120b 83.54 / 70.37 (our notes give this pair without labels; by the pattern of the sentence, accuracy then IFC). Errors are mostly needless interventions: 303 of 321 errors of GPT-6-Astra and 468 of 551 of Claude-5-Sonnet are on tasks where acting was right. All 720 Relax labels are correct, yet no response passes the repair-and-act check. Output specification changes decisions: on 2,160 tasks, GPT-6-Astra's accuracy goes 92.59 → 94.58 → 97.59 and IFC 85.74 → 89.17 → 95.19 from the original prompt to explicit JSON to JSON with evidence. Counter-evidence in the paper: in an earlier gpt-oss setting accuracy fell (77.2, 74.7, 71.1).
- **Failure modes.** Over-intervention when the available information already suffices; a correct high-level label with an unusable concrete repair; sensitivity of decisions to the output format.
- **Limitations.** Stated by the authors: within-model comparisons only; truncations for one model; quota gaps for another; one response per prompt. Our notes: no confidence intervals for gaps of a few points; the explicit-output condition also defines the label strings, so clearer labels and better reasoning are confounded; label correctness depends on the accepted-set rule.
- **Relation to this project.** It already provides solver-grounded next-action evaluation with matched pairs, so that is not a contribution of this project (novelty map §1). Our counterfactual pairs follow its matched-pair design (`paper/extended_report.md`, Appendix G).
- **What this project does differently.** The edit changes the minimal sufficient plan over mixed information and computation actions, not only whether to intervene. Scoring is of a plan against all cheapest plans, not of a decision label.
- **Experiments it motivated.** The counterfactual single-edit pairs (T1), including edits that make a state already sufficient (`working_documents/CHALLENGE_V4_DESIGN.md` §3; [`../PREREG_T1.md`](../experiments/preregistrations/PREREG_T1.md), disclosure). The T1 development pilot was inconclusive under its registered rules; an exploratory observation in it (over-intervention on states that one edit made sufficient) "mirrors the dominant error in Ask, Relax, or Act?" and led to a registered follow-up, T1B ([`../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md`](../results/aggregate/t1_pilot_dev/T1_PILOT_FINDINGS.md); [`../PREREG_T1B.md`](../experiments/preregistrations/PREREG_T1B.md)). The same test was then registered for the held-out split (`paper/report.md` §4.2). Its §5 also supports a design rule: output format is a treatment, so one output protocol per model is fixed before freezing (design document §5, risk 4). In our own diagnostic data (10 development families, not confirmatory), the forced-schema condition for gemma changed plans and not only format: −0.14 optimal on items parsed in both conditions ([`../results/aggregate/diagnostics_2026-11-13/FINDINGS.md`](../results/aggregate/diagnostics_2026-11-13/FINDINGS.md)).
- **Would be redundant.** A flip that only toggles intervene or act, or a metric that is only pair correctness of a decision label; claiming that output format changes decisions.

## 5. Agents' Last Doubt / SURE-Act [3]

Liu et al. (2026). "Agents' Last Doubt: Knowing When to Act and When to Step Back in Tool-Using Agents." arXiv:2610.24194, v1 2026-10-16. Link: https://arxiv.org/abs/2610.24194

- **What was read.** The full HTML v1 (failure map §3). The reference check of 2026-11-03 could not find this paper; the check of 2026-11-13 found it at the cited id and supersedes the earlier entry (novelty map §9a).
- **Research question.** When a tool-using agent should ask, look up, act or commit, judged by what each action leads to.
- **Method.** One benchmark (ToolSandbox). Action categories: Ask (user), Search (read-only lookup), Act-Reversible, Commit-Irreversible. Counterfactuals: clone the state, force one action category for one turn, let the backbone finish; one temperature-0 rollout per action. A controller (Qwen3-1.7B with LoRA) predicts success, cost and critical error. Families are split 60/20/20. A stopping rule hands back after three identical proposals.
- **Models and settings.** 1,036 checkpoints, 378 tasks, 82 families. Labels from Qwen3-8B and 14B continuations. End-to-end runs with Qwen3-4B, 8B and 14B on the development pool and on 89 unseen families.
- **Main findings as the authors report them.** Offline on unseen families the gain is "-0.0000 (SE 0.0003)". End-to-end gains on unseen families are positive (+0.0216 for 8B, +0.0575 for 4B, +0.0252 for 14B). Ask is chosen on 0.36% of natural decisions. Where lookup was best, the controller chose a reversible change "on 53 of 53 occasions". In a source-shift test, "0 of 24 pairs" are correct in both conditions. The best action changed on 345 of 725 checkpoints (label instability). Captured headroom is 8.3%. Critical errors rise (+0.0220 on development).
- **Failure modes.** Ignoring where the missing fact comes from; almost never asking; preferring a reversible action over a lookup; unstable labels.
- **Limitations.** Stated by the authors: one benchmark, one rollout per label, one-turn interventions. Our notes: the source-shift test is one paragraph, without construction details or per-condition numbers; Ask is almost never learned, so ask versus lookup is barely tested; many contrasts without correction for multiple comparisons; the intervals of the 4B and 8B end-to-end gains include zero (this last point was not re-checked; review, Part D, item 14).
- **Relation to this project.** It already compares the counterfactual value of several actions and trains a controller, so that is not a contribution of this project (novelty map §1).
- **What this project does differently.** Its source shift is between asking and looking up; both are information. This project's two resources are information and certified computation. Labels here come from an exact oracle, not from rollouts. The mitigation here is symbolic, not learned.
- **Experiments it motivated.** T2, information-source switching between information and certified computation. It was not run. In the present formal model a computation action exists only when its result is derivable from visible inputs, so a naive pair is readable from the action menu; the design document records that a semantics decision is needed and does not recommend T2 for the sprint (`working_documents/CHALLENGE_V4_DESIGN.md` §3).
- **Would be redundant.** A switch between two information channels, or between "ask" and "act".
- **Caution in describing it.** "No generalisation to unseen families" holds offline only (failure map §3).

## 6. Same Signal, Opposite Meaning / DIAL [4], with Rational Metareasoning [7]

Li et al. (2026). "Same Signal, Opposite Meaning: Direction-Informed Adaptive Learning for LLM Agents." arXiv:2605.06908 (v2). Link: https://arxiv.org/abs/2605.06908

- **What was read.** Abstract, §1–7, Tables 1–5, Appendices D.1–D.6, E, F.1–F.4, part of G.1. Not read: B.2, C, G.2–G.6, H (failure map §4).
- **Research question.** Whether an uncertainty signal tells an agent when extra computation helps.
- **Method.** "Additional computation" is an optimizer invoked at a step (five candidates, five truncated rollouts, horizon three). Its benefit is the expected return with the optimizer minus the expected return of the base policy. The signal is token entropy, with other features in DIAL's gate.
- **Models and settings.** HotpotQA, APPS, WebShop, FEVER, TWExpress, Plancraft. Qwen3-4B-Instruct, Phi-3.5-mini-Instruct, Llama-3.1-8B-Instruct; three seeds.
- **Main findings as the authors report them.** The Spearman correlation between entropy and benefit changes sign across models and environments, for example FEVER −0.156 for Phi-3.5 against +0.428 for Llama-3.1, and HotpotQA −0.327 for Qwen against +0.184 for Phi. Reversing the gate weights costs up to 37 success-rate points. Extra computation can fall below no computation (one FEVER setting: 32.2% against a 37.0% baseline).
- **Failure modes.** An uncertainty signal with the wrong sign for a given model and task; computation that lowers success.
- **Limitations.** The authors call their two-regime account "a regime-level abstraction", "not a mechanistic claim". Our notes: two tables give conflicting numbers for one FEVER setting (99.8% and 59.8%); most ablations are on one model; cost excludes the exploration phase; no significance tests were found.
- **Relation to this project.** It establishes that compute need and compute suitability differ, so "when should the model think more?" is not a contribution of this project (novelty map §1).
- **What this project does differently.** Here a computation is certified: it adds knowledge and never lowers sufficiency. DIAL's "computation can hurt" does not transfer. What transfers is that a computation can be unnecessary or not worth its cost, which this project measures as redundancy and excess cost. A "computation can hurt" test would need a separate setting with approximate or stochastic computation (failure map §4, item 5).
- **Experiments it motivated.** None in the challenge tier ("none in v4"; failure map, cross-paper summary).
- **Would be redundant.** Claiming that uncertainty is a poor proxy for compute need.

**Rational Metareasoning [7]** (De Sabbata et al., 2024; arXiv:2410.05563; https://arxiv.org/abs/2410.05563) trains an LLM with a value-of-computation reward to reason only where it pays. The abstract page reports 20–37% fewer generated tokens across three models; the v3 full text says 23–45%. Stated limitation: not tested on agents, where tool costs would enter the reward (review B.3). It is the reason "adaptive computation" is not claimed as new. The pages fetched do not say that extra reasoning lowers accuracy (review, Part D, item 1). No experiment is recorded as motivated by it; the problem specification names value of information, value of computation and decision-theoretic metareasoning as the tradition that its planned objective for conditional plans continues ([`working_documents/PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §12).

## 7. ToolChoiceConfusion [5]

Babu and Iyer (2026). "ToolChoiceConfusion: Causal Minimal Tool Filtering for Reliable LLM Agents." arXiv:2606.06284, v1 2026-06-04. Link: https://arxiv.org/abs/2606.06284

- **What was read.** Abstract and the full HTML v1. The paper has no appendix. Its code was not fetched (failure map §5).
- **Research question.** Whether showing an agent only causally necessary tools makes tool choice reliable.
- **Method.** One agent step is the choice of one tool given the query, a symbolic state and the visible tool schemas; at most six steps. Tools have required and produced variables. The filter, CMTF, runs a breadth-first search over symbolic states and exposes only the first tool on a shortest path to the goal.
- **Models and settings.** 100 synthetic tools including distractors; calendar, email and files, 34 tasks each (102). Amazon Nova 2 Lite, Nova 2 Pro Preview, Claude 3.5 Haiku, Claude Sonnet 4. 2,448 runs.
- **Main findings as the authors report them.** Aggregate success: all tools 0.83 (1.25 wrong tools per task); keyword top-5 0.61 (2.36); keyword top-10 0.72; state-aware, executable only, 0.65 (1.98); full causal path 0.99; CMTF 0.99 (0.01). Relevant, executable and causally sufficient are three different properties.
- **Failure modes.** Choosing tools that are relevant, or executable, but not on a path to the goal.
- **Limitations.** Stated by the authors: synthetic environment, hand-written contracts, goals assumed mappable to states, four models, wrong-tool scored against one gold chain. Our notes: the near-perfect result may be partly circular, because the filter shows one tool computed from the same contracts that define the task; no variance or significance tests; one registry of 100 tools, with no sweep over the number of tools.
- **Relation to this project.** It establishes that a relevant tool is not a sufficient tool, so that is not a standalone contribution of this project (novelty map §1).
- **What this project does differently.** It is a filter that decides for the model. This project evaluates the model's own pruning against an exact oracle, with unequal costs.
- **Experiments it motivated.** T3, relevance versus necessity at fixed size: hold the number of actions and prompt length fixed and vary only how many offered actions are relevant but unnecessary. The construct is the failure seen for gemma in the diagnostic calibration (sufficient plans padded with actions the oracle marks irrelevant or relevant but insufficient). T3 exists as design text only and was not run (`working_documents/CHALLENGE_V4_DESIGN.md` §3; [`../docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md) §4.14).
- **Would be redundant.** Showing only that distractors hurt or that filtering helps, or making tasks hard by raising the number of tools.

## 8. Active Epistemic Control [6]

Qu (2026). "Active Epistemic Control for Query-Efficient Verified Planning." arXiv:2602.03974, v1 2026-02-03. Link: https://arxiv.org/abs/2602.03974

- **What was read.** The full HTML v1. Figures 1–3 are images and were not read; ablation and backbone numbers come from the text (failure map §6).
- **Research question.** How a planner should decide what to check in the environment before committing to a plan.
- **Method.** A grounded store (observations and query results) is kept apart from a belief store (world-model predictions "never treated as truth"). The planner queries when a prediction is ambiguous or uncertain and simulates otherwise. It commits only if a verifier passes: preconditions grounded or entailed, plus a check defined in another paper.
- **Models and settings.** ALFWorld (134 tasks, 50 steps). ScienceWorld is marked "(planned)" in one section and reported in another. Backbones: GPT-4, Qwen3-14B, DeepSeek-R1-14B, Llama-3-8B; the main model is not named.
- **Main findings as the authors report them.** ALFWorld 98.7% against 98.3% for the strongest baseline; the authors call the gains "modest". In the ablation, "failure rate" is 2 for the full method, 9 without verification and 4 without gating. Success rises from 88% to about 98% over refinement iterations.
- **Failure modes.** The authors conclude that "model-based hypothesis filtering alone is insufficient". The causes they name (grounder errors, incomplete entailment) are not measured; there is no failure taxonomy.
- **Limitations.** Our notes: "failure rate" is undefined, so the figures 2 and 9 are not counts; 98.7 is not k/134 for any k; "query-efficient" is never measured as query counts; no token numbers; no variance; single-author v1.
- **Relation to this project.** It mixes querying and simulated inference in one planner. This is partial overlap and is cited (novelty map §9).
- **What this project does differently.** It is a planning method. It does not evaluate minimal or optimal sets of epistemic actions and has no BOTH or NEITHER cases with an exact oracle.
- **Experiments it motivated.** A baseline idea for the mitigation: compare the Epistemic Obligation Planner against a simple grounded-verification controller that commits only when every obligation is grounded or certified (failure map §6, item 5). No repository document records that a controller was built under that description. Not recorded.
- **Would be redundant.** Presenting epistemic control, or "query before committing", as our contribution.

## 9. EPRAG [26]†

Kinalioglu (2026). "EPRAG: An epistemic policy framework for action selection in multi-source enterprise retrieval-augmented generation." Knowledge-Based Systems 352, 116929. Links: https://doi.org/10.1016/j.knosys.2026.116929 ; as cited in the working timeline: https://www.sciencedirect.com/science/article/abs/pii/S0950705126016552

- **Status.** † Bibliographic details from Crossref; not read at the source. The publisher page returned HTTP 403 and no abstract was available. `paper/references.md` lists it as "not verified at the source (do not cite as read)". A search found an artifact repository under the same title, not the paper (review, Part D, row 23).
- **What is confirmed.** Title, author, journal, volume and article number. The DOI record was created on 2026-08-28; the issue is dated 2026-10. The title says the setting is enterprise retrieval-augmented generation and the subject is an epistemic policy for action selection.
- **What the working documents say and what is not confirmed.** The working timeline (§11) and the novelty map (§1) describe EPRAG as separating evidence-state diagnosis from response selection and as using counterfactual answerability for decisions between clarifying and abstaining, with an LLM/NLI approximation, and give the date 2026-10-25. None of this is confirmed (review, Part D, item 7).
- **Research question, method, models, findings, failure modes, limitations.** Not stated in our notes (content not read).
- **Relation to this project.** On the working documents' unconfirmed description, the novelty map concludes that "diagnose state then choose action" is not novel by itself. The project keeps that non-claim whether or not the description is right.
- **What this project does differently.** By the title alone: the setting here is a formal benchmark with an exact oracle, not enterprise retrieval. Nothing further can be said from our notes.
- **Experiments it motivated.** Not recorded.

## 10. From language to logic [R11]–[R15]

The mitigation depends on translating text into a formal state. `paper/report.md` §2 cites five papers for this step. They appear in the final report's reference list, whose header states that unmarked entries were confirmed on the listed page and their abstracts read. They are not in the failure map and have no row in the review's verification log, so the notes on them are short.

| No. | Reference | Link | What the report cites it for |
|---|---|---|---|
| [R11] | Pan, Albalak, Wang, Wang (2023). Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning. Findings of EMNLP 2023, 3806–3824 | https://aclanthology.org/2023.findings-emnlp.248/ | A solver-backed pipeline with an LLM as semantic parser; repair from solver messages |
| [R12] | Olausson et al. (2023). LINC: A Neurosymbolic Approach for Logical Reasoning by Combining Language Models with First-Order Logic Provers. EMNLP 2023, 5153–5176 | https://aclanthology.org/2023.emnlp-main.313/ | A solver-backed pipeline with an LLM as semantic parser |
| [R13] | Geng, Josifoski, Peyrard, West (2023). Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning. EMNLP 2023, 10932–10952 | https://aclanthology.org/2023.emnlp-main.674/ | Constraining the output grammar |
| [R14] | Kim, Poiroux, Bosselut (2026). Do LLMs Game Formalization? Evaluating Faithfulness in Logical Reasoning. arXiv:2604.19459; VerifAI-2 Workshop at ICLR 2026 (non-archival) | https://arxiv.org/abs/2604.19459 | A formalization can be well-formed and still unfaithful |
| [R15] | Amrollahi, Lopez, Barrett (2026). Faithful Autoformalization via Roundtrip Verification and Repair. Findings of EMNLP 2026, 9836–9852 | https://aclanthology.org/2026.findings-emnlp.469/ | Roundtrip checks and repair |

- **Research question, method, models and settings, findings as the authors report them, limitations.** Not stated in our notes beyond the one-line descriptions above.
- **Relation to this project.** The Epistemic Obligation Planner is a solver-backed pipeline of the same kind: the model extracts a formal state and an exact planner chooses the actions. The project does not claim solver-backed planning as new (`paper/report.md` §2).
- **What this project does differently.** It measures the effect of extraction, and of one repair step, on the exact formal state and on the cost-optimal plan that an exact planner derives from it, against an oracle. The registration of Study 3 names [R11], [R12], [R13] and [R15] as related work that the study "does not claim to improve on" ([`../PREREG_REPAIR.md`](../experiments/preregistrations/PREREG_REPAIR.md) §0).
- **Experiments they motivated.** Study 3 (exploratory follow-up, registered after the held-out results were viewed): each rejected extraction was sent back once with the model's own answer and the reader's message, "as in solver-message refinement" [R11] (`paper/report.md` §4.4). Its result is consistent with [R14]'s point that a well-formed formalization can be unfaithful: repair recovered most rejected extractions and also raised the share of extractions that are accepted but wrong, for gemma from 0.07 to 0.16 ([`../results/aggregate/repair/repair_report.md`](../results/aggregate/repair/repair_report.md)). [R14] and [R15] are also the basis of the first item of future work ([`future_research.md`](future_research.md)). Grammar-constrained decoding [R13] was not tested; the extended report lists constrained decoding for the extraction step as future work.

## 11. Comparison matrix

Each cell is filled only where a repository source supports it; the source is the section of this document named in the last column. "No (recorded)" means our notes record that the paper lacks the feature. "not stated in our notes" means our notes do not settle the cell either way; it does not mean the paper lacks the feature.

| Paper | Information acquisition | Computation allocation | Mixed-resource plans | Exact sufficiency | Plan minimality | Unresolvable states | Controlled diagnosis | Formal action verification | Learned or symbolic mitigation | Notes from |
|---|---|---|---|---|---|---|---|---|---|---|
| MT-InfoSeek [1] | Yes: which variables to query | No (recorded): no computation on offer | No (recorded): information only | Yes by definition (all feasible assignments agree); LLM oracles answer in two domains | Yes: minimal k-sufficient set, equal costs | No (recorded): a sufficient set exists for every problem | Partly: the set is identified with and without the true k | not stated in our notes | not stated in our notes | §2 |
| QuestBench [36] | Yes: the one question that settles the problem | No (recorded): no computation on offer | No (recorded) | not stated in our notes | One missing value; equal costs | No (recorded): a sufficient set always exists | not stated in our notes | not stated in our notes | not stated in our notes | §3 |
| Ask, Relax, or Act? [2] | Yes: ask for a preference or an objective | not stated in our notes (single turn, no tools) | not stated in our notes | Yes: exact solvers label whether intervention is necessary | No (recorded): a decision label is scored, not a set of steps | not stated in our notes (it has a Relax label for constraint repair) | Matched pairs that flip whether intervention is needed; output-specification comparison | A repair-and-act check on Relax responses | No method; output specification changes decisions | §4 |
| SURE-Act [3] | Yes: ask the user, read-only search | No (recorded): both sources are information | not stated in our notes | No (recorded): labels from one rollout per action | Not scored; outcomes are success, cost and critical error | not stated in our notes (a stopping rule hands back after three identical proposals) | Source-shift test on 24 matched pairs | not stated in our notes | Learned controller (Qwen3-1.7B with LoRA) | §5 |
| DIAL [4] | No information action recorded in this strand | Yes: when to invoke an optimizer | No (recorded) | not stated in our notes (benefit is defined as a difference of expected returns) | not stated in our notes | not stated in our notes | One controlled study (one model, one environment) | not stated in our notes | Learned gate | §6 |
| Rational Metareasoning [7] | No information action recorded in this strand | Yes: reason only where it pays | No (recorded) | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | Learned (value-of-computation reward) | §6 |
| ToolChoiceConfusion [5] | not stated in our notes | not stated in our notes | not stated in our notes | Causal sufficiency from symbolic tool contracts | Shortest path to the goal; wrong tools scored against one gold chain | not stated in our notes (goals are assumed mappable to states) | Filter conditions compared on the same tasks | Symbolic contracts (required and produced variables) | Symbolic filter (CMTF) | §7 |
| Active Epistemic Control [6] | Yes: query the environment | Simulation in place of a query | In the method; not evaluated as minimal sets | A verifier (preconditions grounded or entailed) | No (recorded): minimal or optimal action sets are not evaluated | not stated in our notes | Ablations without verification and without gating | Yes: commit only if the verifier passes | Planner method with a verifier | §8 |
| EPRAG [26]† | not stated in our notes (content not read) | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes (title: an epistemic policy framework) | §9 |
| Language to logic [R11]–[R15] | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | not stated in our notes | Solver- or prover-backed pipelines [R11, R12]; roundtrip verification [R15] | Symbolic: LLM as semantic parser with a solver; repair from solver messages; grammar-constrained output | §10 |
| This project (MSEP) | Yes: priced information actions | Yes: priced certified computation actions | Yes: BOTH states | Yes: exact oracle, re-verified by brute force (228,199 checks, 0 failures) | Yes: all cheapest sufficient plans | Yes: NEITHER states | Yes: three modes separate detection, diagnosis and planning | Yes: the planner checks which obligations each action discharges | Symbolic: model extraction plus exact planner (EOP). No learned router was built | `paper/report.md` §3; [`../results/oracle_validation.md`](../results/oracle_validation.md); `docs/EXPERIMENT_INDEX.md` §4.14 |

The row for this project describes the task as defined. It does not say the project solved these problems; the limits are in `paper/report.md` §5 and Appendix A.

## 12. Which experiments each paper motivated

Only links that a repository document states are listed. "Not recorded" means no document states a link.

| Paper | Experiment or design element | What happened | Evidence tier of the result | Source of the link |
|---|---|---|---|---|
| Ask, Relax, or Act? [2] | T1 counterfactual single-edit pairs; flips into ALREADY_SUFFICIENT | Development pilot run; inconclusive under the registered rules | Registered development (pilot); its over-intervention observation was exploratory | `PREREG_T1.md`; `T1_PILOT_FINDINGS.md` |
| Ask, Relax, or Act? [2] | T1B, over-intervention after one edit makes the state sufficient | Supported on development for qwen3.5-397b and gemma; then tested on the held-out split: 0.20 [0.14, 0.27] and 0.72 [0.64, 0.79] | Registered development; registered held-out | `PREREG_T1B.md`; [`../results/aggregate/final_test/RESULTS_TABLES.md`](../results/aggregate/final_test/RESULTS_TABLES.md) |
| Ask, Relax, or Act? [2] | One output protocol per model (format is a treatment) | Applied as a design rule | — | `CHALLENGE_V4_DESIGN.md` §5 |
| MT-InfoSeek [1] | T4 conditional sequential planning | Not run; needs a new oracle | — | `CHALLENGE_V4_DESIGN.md` §3 |
| SURE-Act [3] | T2 information-source switching | Not run; semantics decision open | — | `CHALLENGE_V4_DESIGN.md` §3 |
| ToolChoiceConfusion [5] (with [1]) | T3 relevance versus necessity at fixed size | Not run; design text only | — | `CHALLENGE_V4_DESIGN.md` §3; `docs/EXPERIMENT_INDEX.md` §4.14 |
| Active Epistemic Control [6] | Grounded-verification controller as a mitigation baseline | Not recorded as built | — | Failure map §6 |
| DIAL [4] | None | — | — | Failure map, cross-paper summary |
| Logic-LM [R11] and [R12], [R13], [R15] | Study 3, one diagnostic repair call | Run once | Exploratory follow-up, registered after the held-out results were viewed | `PREREG_REPAIR.md` §0; `paper/report.md` §4.4 |
| EPRAG [26]†, QuestBench [36], Rational Metareasoning [7] | Not recorded | — | — | — |

The later reading of the T1B and held-out over-intervention result changed. A follow-up study on fresh families (Study 1, registered after the held-out results were viewed) showed that most of the strong model's over-intervention came from an ambiguity in the benchmark text: 0.14 falls to 0.03 with clarified wording for qwen3.5-397b, and 0.73 to 0.59 for gemma ([`../results/aggregate/followup/followup_report.md`](../results/aggregate/followup/followup_report.md)). So for the strong models, most of the over-intervention first measured was induced by the benchmark's wording (`paper/report.md` §4.2); for those models it should not be read as the same error that [2] reports (retrospective interpretation). gemma's over-intervention is large under either wording. See [`research_evolution.md`](research_evolution.md).

## 13. Other related work, by strand

The table is from the literature review (`paper/literature_review.md`, Part B), with QuestBench [36] added to the row "What to ask" and the † marks added. The works in it were checked at abstract level or, where marked †, from bibliographic records only. Summaries of each are in [`literature_timeline.md`](literature_timeline.md).

| Strand | Representative work | What it measures | What it leaves open that MSEP tests |
|---|---|---|---|
| Is the model uncertain? | [12]–[14], [28], [29] | calibration and uncertainty signals | which action would resolve the uncertainty |
| What to do, and why | [15]–[19] | clarifying, abstaining, retrieving; cause of uncertainty | the cheapest sufficient remedy, scored exactly |
| When to compute | [4], [7], [20], [21] | when reasoning pays; minimal sufficient reasoning | which certified computation settles a question |
| What to ask | [1], [22], [36] | minimal sufficient queries; value of asking | unequal costs; computation; BOTH and NEITHER states |
| Which intervention | [2], [3], [6], [8], [24], [25]†, [26]†, [27] | decision category; rollout values; method success | minimal mixed plans against an exact oracle |
| Relevant versus sufficient | [5], [23] | sufficiency of tools and of evidence | the model's own pruning of unnecessary actions |

Two works touch the novelty boundary and are cited for it. ConfuseBench [19] already evaluates whether models identify the cause of uncertainty among three types, one of them limited capability. EvoCtx [27] and Lacombe et al. [29] already set retrieval against further reasoning (review, Part D, item 12).

## 14. Logical roots and behavioural motivation

**Logical roots.** The oracle is related to the logical theory of the reasons behind decisions [30, 31]. There, a sufficient reason is a minimal set of an instance's values that fixes a decision, and a necessary reason is a minimal set whose change can flip it. A minimal sufficient plan resembles the first and an obligation the second, with unknown variables in place of the known values of one instance. The papers do not state this correspondence; it is our reading. The posterior-threshold rule, which the benchmark does not use, is related to the same-decision probability [32], and choosing observations in advance for decision robustness was studied for Bayesian network classifiers [33], so scoring a set of observations chosen in advance is not unique to this project (`paper/ucla_related_work.md` §1). The repository does not use knowledge compilation, and the wording is "is related to", not "builds on" (review, Part E).

**Behavioural motivation.** Assistants have been reported to match their answers to a user's stated views instead of the truth [35], and designers have found that no prompt made a model reliably say "I don't know" when it should [34]. This is motivation only. The benchmark does not test deference to a user (review B.2). No sycophancy paper by the second professor named in the author's note was found by any source checked (`paper/ucla_related_work.md` §2).

## 15. Open verification points

- EPRAG [26]† and uncertainty intervention routing [25]† were not read; only their titles and bibliographic records are confirmed.
- Russell and Wefald [10]† and Kirsh and Maglio [11]† are cited from Crossref records; for [11] the deposited abstract was read.
- The five language-to-logic papers and QuestBench have no row in a verification log; their status rests on the reference list of `paper/report.md`.
- Numbers spot-checked against the full text on 2026-11-14 matched the failure map for [1]–[6]; other numbers in the failure map were not re-checked, and numbers for [12]–[29] come from abstracts only (review, Part D).
- Reference [8] is described in the novelty map as "information side only"; its abstract does not address this either way (review, Part D, item 13).
- The literature list is not a systematic search, and the wording of the project's novelty statement is "we did not find", not "first" ([`research_gap_and_novelty.md`](research_gap_and_novelty.md)).
