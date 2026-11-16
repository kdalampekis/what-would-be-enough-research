# Literature timeline: from "how confident is the model?" to "what exactly would be enough?"

This document answers one question: through which stages did the field arrive at the research question of this project? It follows the project's working timeline, [`working_documents/LITERATURE_TIMELINE.md`](working_documents/LITERATURE_TIMELINE.md) (written on 2026-11-03 in Greek with English technical terms; literature cutoff 2026-11-02), and keeps its substance and its references. Where a later repository document corrects the working timeline, the correction is applied here and listed in Section 14. For each stage the document states what the work established, which limitation remained, and how later work addressed it. The list of works is a candidate list checked reference by reference; it is not a systematic literature search ([`../paper/LITERATURE_REFERENCES_MASTER.md`](../paper/LITERATURE_REFERENCES_MASTER.md)).

## How to read this document

- **Reference numbers.** [1]–[36] are the numbers used in the References of [`../paper/extended_report.md`](../paper/extended_report.md) (the same as Part C of [`../paper/literature_review.md`](../paper/literature_review.md) for [1]–[35]). [R11]–[R15] are references 11–15 of [`../paper/report.md`](../paper/report.md), which appear only there. [U…] numbers are those of [`../paper/ucla_related_work.md`](../paper/ucla_related_work.md). The full list with verification status is in Section 15.
- **"The authors report"** marks a number read in the cited paper or its abstract. No number here was produced by this project unless it is said so.
- **†** marks a reference whose bibliographic details were taken from Crossref and which was not read at the source. Such a reference is cited only for what its title and venue show.
- **Source tags.** "Timeline §n" refers to the working timeline. "Review B.n" refers to Part B of `paper/literature_review.md` (reproduced as Appendix G of the extended report). "Failure map §n" refers to [`working_documents/LITERATURE_FAILURE_MAP.md`](working_documents/LITERATURE_FAILURE_MAP.md).
- **Which stages come from which document.** The working timeline names seven works: [1], [2], [3], [4], [6], [7] and [26]. Most other works below were added from the author's consolidated list of 2026-11-14 and checked in the literature review (review, Part D, item 9); [8] comes from the novelty map (review, Part D, "Not in the master list"), [30]–[35] from the notes in `paper/ucla_related_work.md`, and [36] from the final check of 2026-11-15. Stages 2, 4, 6 and 11 have no section of their own in the working timeline; their content comes from the review.

## 1. Classical metareasoning and the value of computation

**What the work established.** Before language models, AI and decision theory already asked when an agent should keep thinking, gather information, or decide now. This is metareasoning: reasoning about reasoning (timeline §1). Horvitz [9] (1988) describes using decision theory to optimise the value of computation under uncertain and varying resource limits. Russell and Wefald [10]† (1991) is the source that Rational Metareasoning [7] cites for the value of computation (review B.1).

**Limitation that remained.** The theory says that thinking and asking have costs and benefits. It does not say whether a language model can weigh them reliably. The working timeline states this as the new problem of the LLM era (timeline §1).

**How later work addressed it.** Stage 8 (adaptive computation) and stage 7 (information seeking) apply these ideas to LLMs.

**Correction.** The working timeline names value of information (VOI) and value of computation (VOC) as the two classical ideas. No verified entry in the project's list supports VOI as a pre-LLM source: [9] and [10] concern the value of computation, and [22] is a 2026 method (review, Part D, item 5). The UCLA notes record one pre-LLM use of value of information for Bayesian classifiers, [U8] (2015); it is not recorded as the classical origin of the idea.

## 2. Epistemic versus pragmatic action

**What the work established.** Kirsh and Maglio [11]† (1994) distinguish pragmatic actions from epistemic actions, which are "performed to uncover information that is hidden or hard to compute mentally" (abstract as deposited with Crossref; review, Part D, row 3).

**Limitation that remained.** The distinction comes from cognitive science. It describes kinds of action; it does not give a test of whether an artificial agent picks the right epistemic action.

**How later work addressed it.** A 2026 position paper [24] brings epistemic action to LLM agents and distinguishes acquiring missing evidence, transforming available evidence and probing a system (review B.5). This project's two action kinds, information actions and certified computation actions, correspond to the first two (retrospective interpretation).

## 3. LLM self-knowledge and calibration (2022–2024)

**What the work established.** The first large LLM-era question was whether a model can tell how confident it should be (timeline §2). Kadavath et al. [12] (2022) report that larger models are well calibrated on multiple-choice and true/false questions in the right format, and that they struggle to calibrate "I know" predictions on new tasks. Zhu et al. [13] (2023) study calibration through pretraining and alignment training; the abstract states no direction of the result (review B.2; Part D, rows 4–5).

**Limitation that remained.** The working timeline's summary is that being wrong does not mean the model knows it is wrong (timeline §2). A confidence value also does not say what to do next.

**How later work addressed it.** Later work measured uncertainty at the level of meaning (stage 4) and turned uncertainty into decisions: abstain, clarify, retrieve (stages 5–7).

**Correction.** The working timeline says LLMs "are not perfectly calibrated and are often overconfident". The abstracts support this only in part. [28] and [29] report overconfidence for reasoning models, and [19] says LLMs "frequently exhibit overconfidence". [12] reports good calibration for larger models in the right format, and [13] states no direction (review, Part D, item 4).

## 4. Semantic uncertainty (2024)

**What the work established.** Farquhar et al. [14] (2024) compute entropy over meanings instead of word sequences, to detect confabulations (review B.2). The working timeline lists semantic uncertainty among the uncertainty-estimation methods, with token probabilities, entropy, verbal confidence and self-consistency (timeline §2).

**Limitation that remained.** A better uncertainty signal still describes the model's state. The abstracts of the works in stages 3–6 "do not describe scoring a minimal sufficient remedy" (review B.2).

**How later work addressed it.** Stage 8 shows that the same uncertainty signal can point in opposite directions for the benefit of extra computation [4].

## 5. Abstention and selective prediction (2025)

**What the work established.** The next question was whether a model without enough certainty should answer or say that it does not know (timeline §4). AbstentionBench [16] (2025; 20 datasets, 20 models) reports that reasoning fine-tuning degrades abstention by 24% on average (review B.2).

**Limitation that remained.** Abstention is a binary choice. It does not say which missing fact or computation would make an answer possible.

**How later work addressed it.** ConfuseBench [19] asks models to identify the cause of the uncertainty instead of abstaining (stage 6). This project scores deferral only when no available action can settle the question (the NEITHER class; [`working_documents/PROBLEM_SPEC.md`](working_documents/PROBLEM_SPEC.md) §2).

**Correction.** The working timeline illustrates this stage with a utility example (+1 for a correct answer, −10 for a wrong one, 0 for abstaining) and concludes that uncertainty estimation and decision policy are different problems. The example and the conclusion are the timeline's own. The abstract of [16] does not state them (review, Part D, item 6).

## 6. Uncertainty diagnosis and clarification (2024–2025)

**What the work established.** CLAMBER [15] (2024; 12K items) reports limited ability to identify and clarify ambiguous queries. ConfuseBench [19] (2025) asks whether uncertainty comes from document scarcity, limited capability or query ambiguity; the authors report that models struggle to identify the cause and tend to blame ambiguity (review B.2).

**Limitation that remained.** Naming the cause of uncertainty is a diagnosis. It is not yet a remedy scored for sufficiency or cost.

**How later work addressed it.** 2026 work chooses among interventions (stage 12). This project's resource classes (information only, computation only, both, neither) are a diagnosis that an exact oracle derives from the state.

**Note on the novelty boundary.** ConfuseBench already evaluates whether models identify the cause of uncertainty among three types, one of them limited capability. The project's claim that it separates diagnosis from planning must be read with this in mind (review, Part D, item 12).

## 7. Adaptive retrieval and information seeking (2025–2026)

**What the work established.** With retrieval-augmented generation and agents, the question became whether the model knows when it needs more external information. The model should not retrieve always; it should notice when the current context is not enough (timeline §5). SeaKR [18] (2025) retrieves when uncertainty read from internal states is high. Moskvoretskii et al. [17] (2025) compare 35 adaptive retrieval methods and report that uncertainty estimators often beat complex pipelines on efficiency and self-knowledge at comparable QA performance. Dong et al. [22] (ACL 2026) use value of information to decide whether to ask the user, weighing expected utility gain against the user's cost; across four domains the authors report up to 1.36 utility points over the best tuned baseline in high-cost settings (review B.2, B.4).

**Limitation that remained.** These works decide whether to seek information. They do not say which information is enough.

**How later work addressed it.** Stage 9 asks which variables make the answer unique.

## 8. Adaptive computation (2024–2026)

**What the work established.** With chain-of-thought and reasoning models, the question was whether every query should receive much computation (timeline §3). Rational Metareasoning [7] (2024-10-07) trains an LLM with a value-of-computation reward to reason only where it pays. Its abstract page reports 20–37% fewer generated tokens across three models; the v3 full text says 23–45% (review B.3; Part D, row 8). The working timeline's summary: more reasoning has a cost, so it should be used when it has expected benefit, and "when should I think more?" already has a serious literature (timeline §3).

DIAL [4] (2026-05-07; arXiv v2) studies adaptive test-time compute. The authors report that the Spearman correlation between token entropy and the benefit of extra computation changes sign across models and environments, for example on FEVER −0.156 for Phi-3.5 and +0.428 for Llama-3.1 (failure map §4). The working timeline's summary: an uncertainty signal can mean "extra compute helps" in one setting and "extra compute hurts" in another, so compute need and compute suitability must be kept apart (timeline §7).

Related work from the review (B.2, B.3): SuCo [21] (ICML 2026) defines a Minimal Sufficient CoT, the shortest prefix of a reasoning trace adequate for the correct answer, and trains models toward it. Kim et al. [20] (2026-03-16) give an information-theoretic account of reasoning and self-correction. Mei et al. [28] (2026) and Lacombe et al. [29] (2025) report that deeper reasoning worsens calibration; in [29], search-augmented generation reaches 89.3% accuracy against 48.7% for reasoning models.

**Limitation that remained.** For [7], a stated limitation is that it was not tested on agents, where tool costs would enter the reward. For this strand as a whole, the review records as untested "which certified computation would settle a question, and any information action" (review B.3).

**How later work addressed it.** Some 2026 methods choose between acquiring and reasoning (stage 12). This project puts priced computation actions in the same action space as information actions. Its computation is certified and cannot mislead, so DIAL's finding that computation can lower success does not transfer; what transfers is that a computation can be unnecessary or not worth its cost (failure map §4, item 5).

**Corrections.** (a) An earlier report draft said of both DIAL and Rational Metareasoning that "more computation can hurt". This holds for [4]. For [7], the pages fetched say extra reasoning is costly and penalised when unnecessary; they do not say it lowers accuracy (review, Part D, item 1). (b) [20] is, by its abstract, about the mechanism of reasoning. It does not study allocation between information gathering and computation (review, Part D, item 11).

## 9. Minimal sufficient information (2025–2026)

**What the work established.** MT-InfoSeek [1] (2026-08-14) made the information question strict. It does not ask only whether information is missing. It asks which variables must be learned so that the answer becomes uniquely determined, and it formalises a minimal sufficient set of queries (timeline §6). It has 5,251 problems and 9,006 task instances. The authors report that accuracy in predicting the number of missing variables k falls below 0.5 for k≥2, and that no model exceeds 0.4 exact-set accuracy at k=2 or 0.2 at k=3 when choosing queries freely (review B.4; failure map §1). The working timeline's summary: models often notice that information is missing, but they underestimate how much is missing, a wrong order of questions lowers accuracy, and they stop too early. "Need information" does not mean "know what information is enough" (timeline §6).

QuestBench [36] (2025; NeurIPS 2025 Datasets and Benchmarks Track) gives problems with exactly one missing value and asks for the one question that settles them. The authors report 40–50% accuracy on its logic and planning sets (`paper/report.md` §2). It was added in the final literature check on 2026-11-15 and is not in the working timeline.

**Limitation that remained.** In both benchmarks, queries cost the same, a sufficient set always exists, and no computation is on offer (`paper/report.md` §2). MT-InfoSeek's authors state as limitations equal query costs, LLM oracles in two domains, and a sufficient set for every problem (review B.4).

**How later work addressed it.** This project keeps the idea of a minimal sufficient set and changes the setting: unequal costs, computation actions beside information actions, and states that nothing available can resolve.

**Corrections.** (a) An earlier wording said that models "ask the wrong variables". The abstract does not say this. It says that an incorrect query order reduces accuracy. The working timeline was corrected on 2026-11-03 ([`working_documents/NOVELTY_MAP.md`](working_documents/NOVELTY_MAP.md) §9). (b) The order finding is from one domain (ClinGuide-MT), with an LLM oracle, and is observational; no experiment forces a wrong order (failure map §1). (c) MT-InfoSeek's problems are generated for k from 1 to 4, so its starting states are never already sufficient. The paper does offer k=0 as an answer option and reports an over-questioning rate, so it does not ignore stopping (review, Part D, item 2). (d) The working timeline and the novelty map cite the Microsoft Research page; the failure map says the citation should point to arXiv 2608.14808. Both links are in Section 15. (e) A note of 2026-11-13 recorded 8,912 task instances from the project page; the check of 2026-11-14 found 9,006 on both the arXiv and Microsoft pages and did not find 8,912 on the Microsoft page (failure map §1; review, Part D, row 18).

## 10. Evidence sufficiency versus relevance (2026)

**What the work established.** In tool use, retrieval and evidence evaluation, the literature began to separate two properties: an action, tool or passage is relevant, or it is sufficient to settle the decision. A retrieved passage can be on topic and still lack the decisive fact (timeline §8). RINSE [23] (2026-09-27) judges, before generation, whether retrieved passages suffice. The authors report that 12 generators answer 40.0–99.3% of insufficient-evidence questions even when told to abstain, and that RINSE ranks sufficient above insufficient evidence with a score of 0.837, against 0.746 for the best of ten prior methods (review B.6).

**Limitation that remained.** The sufficiency judgment concerns retrieved evidence. It is not a judgment over a priced menu of actions, and it is not scored against an exact answer in the notes we hold.

**How later work addressed it.** Stage 11 applies the same distinction to tools. This project scores the model's own choice among actions that are irrelevant, relevant but insufficient, and sufficient (`working_documents/PROBLEM_SPEC.md` §9).

## 11. Causal tool selection (2026)

**What the work established.** ToolChoiceConfusion [5] (2026-06-04) treats tool choice as a question of causal sufficiency, not semantic relevance. Its filter (CMTF) searches over symbolic states and exposes only the first tool on a shortest path to the goal. On 102 synthetic tasks with 100 tools and four models, the authors report success of 0.83 with all tools, 0.61 and 0.65 with keyword and executable-only filters, and 0.99 with the causal filter (failure map §5; review B.6). The working timeline's summary of this stage: the right action is not simply the most relevant one (timeline §8).

**Limitation that remained.** It is a filtering method that uses symbolic tool contracts, which are assumed to be available. It decides for the model. It is not an evaluation of the model's own pruning (`working_documents/NOVELTY_MAP.md` §1). Our note: the near-perfect result may be partly circular, because the filter shows one tool computed from the same contracts that define the task (failure map §5, item 4).

**How later work addressed it.** This project evaluates the model's own pruning against an exact oracle (failure map §5, item 5).

## 12. Counterfactual evaluation of epistemic actions and action routing (2026)

**What the work established.** Four lines of 2026 work evaluate or learn the choice among epistemic actions.

- *Solver-grounded action labels.* "Ask, Relax, or Act?" [2] (2026-10-02) builds a benchmark in which exact solvers label whether the model can act, must ask, or must repair constraints. Matched pairs flip whether intervention is needed. The authors report 92.57% item accuracy against 85.56% matched-pair correctness for GPT-6-Astra, and 303 of its 321 errors fall on tasks where acting was right (failure map §2). The working timeline's summary: a model can find the right high-level label and still produce a wrong concrete question or repair, so the correct action type is not the correct usable intervention (timeline §9).
- *Counterfactual action outcomes.* Agents' Last Doubt / SURE-Act [3] (2026-10-16) executes each legal action category at 1,036 ToolSandbox decision points, measures task success, interaction cost and irreversible errors, and trains a controller on the outcomes. In a source-shift test, where the missing fact moves between the environment and the user, the authors report the right choice on 0 of 24 pairs (failure map §3; review B.5). The working timeline's summary: comparing the counterfactual value of several actions is not new in itself (timeline §10).
- *Diagnosis before action.* EPRAG [26]† (Knowledge-Based Systems, 2026) is, by its title, an epistemic policy framework for action selection in multi-source enterprise retrieval-augmented generation. The working timeline describes it as separating evidence-state diagnosis from response selection and as using counterfactual answerability (a clarification that, if answered, would make the query answerable), and says this comes close to the logic of "what would be enough?" while being RAG-specific and approximate (timeline §11). These content claims are not confirmed; see the correction below. Uncertainty intervention routing [25]† belongs to the same strand by its title.
- *Methods that choose between acquiring and reasoning.* Active Epistemic Control [6] (2026-02-03) is a planner that queries the environment or simulates a predicate and commits only on grounded facts; on ALFWorld the authors report 98.7% success against 98.3% for the strongest baseline. EvoCtx [27] (EMNLP Findings 2026) decides whether to retrieve or to refine reasoning within the existing context. EPC-AW [8] (2026-05-22) checks whether plans stay supported under varying information conditions (review B.5).

**Limitation that remained.** The review records as untested in this strand "plans over information and certified computation, scored for minimality" (review B.5). In [3], both sources in the source-shift test are information. [6] and [27] are methods, not benchmarks with exact minimal plans. [2] scores a decision category, not the cheapest set of steps (`paper/report.md` §2).

**How later work addressed it.** This is the point where the present project starts (stage 13).

**Corrections.** (a) The working timeline says SURE-Act could not be found and calls it unconfirmed. This is out of date. On 2026-11-13 the paper was opened at arXiv 2610.24194 (v1, 2026-10-16) and read in full (`working_documents/NOVELTY_MAP.md` §9a; failure map §3; review, Part D, item 8). (b) The working timeline says "Ask, Relax, or Act?" was found only on an aggregator. It was confirmed at the source on 2026-11-13 (novelty map §9a). (c) For EPRAG, only the title, author and journal are confirmed, from Crossref; the publisher page returned HTTP 403 and no abstract was read. The descriptions in the working timeline and the novelty map (RAG-specific, counterfactual answerability with an LLM/NLI approximation, separation of diagnosis from response selection) and the date 2026-10-25 are not confirmed. The Crossref record was created on 2026-08-28 and the journal issue is dated 2026-10 (review, Part D, row 23 and item 7; [`../paper/references.md`](../paper/references.md)). (d) For [25], the description "commit / deliberate / acquire / defer" could not be confirmed; only the title is (review, Part D, item 10). (e) SURE-Act's lack of generalisation to unseen families holds offline only; end-to-end gains on unseen families are positive, with two of three intervals including zero (failure map §3).

## 13. Where this project sits

**What had already been studied.** By November 2026 there was substantial work on uncertainty detection, calibration, abstention, adaptive retrieval, clarification, minimal sufficient information, adaptive compute and the value of computation, evidence sufficiency, relevant versus sufficient tools and evidence, action routing, solver-grounded action selection and counterfactual action outcomes. The project claims none of these as its own problem (timeline §12).

**What appeared to be missing.** The gap not found covered as one exact benchmark: a state in which the model may need only information, only computation, both, or in which no available intervention is enough, with an exact oracle that knows which minimal plan is sufficient (timeline §13). The literature review puts it this way: sufficiency and minimality appear separately for information [1], reasoning [21], evidence [23] and tools [5]; we did not find them scored jointly over information and certified computation, in one priced action space, with states that need either, both or neither, against an exact oracle (review, Part A).

**The question.** "When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?" (timeline §14; `working_documents/PROBLEM_SPEC.md` §1).

**Why three evaluation modes.** A model may never reach "what do I need?" because it did not notice that something is missing. The working timeline therefore plans three modes: End-to-End (notice, diagnose, plan), Detection-Controlled (the model is told the state is insufficient) and Diagnosis-Controlled (it is also told the resource class) (timeline §15).

**What the working timeline planned.** For every formal state the benchmark would record whether it is already sufficient, which information and computation actions exist, which are irrelevant, relevant but insufficient, or sufficient, which minimal combination is sufficient, and whether nothing is enough (timeline §16). The gold label can be a plan, not only an action type. The timeline's example of a gold label is an ordered plan (ask, then verify, then stop); the benchmark as built scores static plans, sets of actions chosen before any result is seen, and sequential plans were not implemented (`paper/extended_report.md`, Appendix D).

**Findings the working timeline expected.** It listed six possible findings: models detect insufficiency but not the resource needed; they know the resource type but choose the wrong concrete action; they confuse relevance with sufficiency; they fail mainly on states that need both resources; they stop before the plan is sufficient; they keep spending after the decision is justified (timeline §17). These were expectations, not results. What the experiments showed is in [`research_evolution.md`](research_evolution.md) and [`hypothesis_tracker.md`](hypothesis_tracker.md); most of the registered hypotheses were not supported on the held-out split (`paper/report.md` §4.1).

**The mitigation the working timeline proposed.** The Epistemic Obligation Planner makes unresolved obligations explicit, checks which actions discharge them, finds a minimum-cost sufficient plan, and stops when nothing more is needed (timeline §18). The working timeline also lists the value it hoped for if this worked: fewer useless searches, less wasted reasoning, better questions to people, better tool use, better stopping and more auditability (timeline §19). These are stated hopes. The measured boundary of the mitigation is in `paper/report.md` §4.3–4.4.

**The working timeline's one-sentence summary.** "Existing work increasingly measures whether AI knows that it needs help; we study whether it knows exactly what would be enough." (timeline §20).

**Logical roots added on 2026-11-14.** The oracle is related to the logical theory of the reasons behind decisions [30, 31]: a minimal sufficient plan resembles a sufficient reason and an obligation a necessary reason, with unknown variables in place of the known values of one instance. The cited papers do not state this correspondence; it is our reading. The same-decision probability [32] is a probabilistic relative of the sufficiency test, and choosing observations in advance for decision robustness was studied for Bayesian network classifiers [33] (review, Part B, "Logical roots"; `paper/ucla_related_work.md` §1).

## 14. Corrections applied to the working timeline

| Working timeline | Correction | Source of the correction |
|---|---|---|
| §1: VOI and VOC are the two classical ideas | No verified pre-LLM source for VOI in the project's list; [9], [10] concern value of computation | `paper/literature_review.md`, Part D, item 5 |
| §2: LLMs are often overconfident | Supported only in part by the abstracts read | Part D, item 4 |
| §4: utility example and "estimation and policy are different problems" | The timeline's own illustration; not stated in the abstract of [16] | Part D, item 6 |
| §6: MT-InfoSeek cited by the Microsoft page | Citation should point to arXiv 2608.14808 | `working_documents/LITERATURE_FAILURE_MAP.md` §1 |
| §6: wrong question order lowers accuracy | One domain, LLM oracle, observational | Failure map §1 |
| §9: "Ask, Relax, or Act?" found only on an aggregator | Confirmed at the source on 2026-11-13 | `working_documents/NOVELTY_MAP.md` §9a |
| §10 and closing note: SURE-Act not found | Exists at arXiv 2610.24194; read in full on 2026-11-13 | Novelty map §9a; failure map §3 |
| §11: EPRAG content and date 2026-10-25 | Only title, author and journal confirmed (Crossref); content and date unconfirmed | Part D, row 23 and item 7 |
| Closing note: Active Epistemic Control "must be cited" | Cited as [6]; full HTML read on 2026-11-13 (figures not read) | Failure map §6 |

## 15. References and verification status

Statuses are those recorded in the repository. "Read at source 2026-11-13": opened on arxiv.org and read as described in the failure map (the parts read differ by paper). "Abstract read 2026-11-14": title, authors, year and venue confirmed on the listed page and the abstract read (`paper/literature_review.md`, Parts C and D). "† Crossref only": bibliographic details from Crossref; not read at the source.

| No. | Reference | Link | Status |
|---|---|---|---|
| [1] | Huang et al. (2026). Do LLMs Know What to Ask and When? Evaluating Multi-Turn Information Seeking (MT-InfoSeek). arXiv:2608.14808 | https://arxiv.org/abs/2608.14808 ; Microsoft page as cited in the working timeline: https://www.microsoft.com/en-us/research/publication/do-llms-know-what-to-ask-and-when-evaluating-multi-turn-information-seeking/ | Read at source 2026-11-13 (parts); abstract page 2026-11-14 |
| [2] | Li et al. (2026). Ask, Relax, or Act? Evaluating Actionable Indeterminacy in LLM Preference Reasoning. arXiv:2610.03102 | https://arxiv.org/abs/2610.03102 | Read at source 2026-11-13 (parts); abstract page 2026-11-14 |
| [3] | Liu et al. (2026). Agents' Last Doubt: Knowing When to Act and When to Step Back in Tool-Using Agents (SURE-Act). arXiv:2610.24194 | https://arxiv.org/abs/2610.24194 | Read in full at source 2026-11-13; abstract page 2026-11-14 |
| [4] | Li et al. (2026). Same Signal, Opposite Meaning: Direction-Informed Adaptive Learning for LLM Agents (DIAL). arXiv:2605.06908 (v2) | https://arxiv.org/abs/2605.06908 | Read at source 2026-11-13 (parts); abstract page 2026-11-14 |
| [5] | Babu & Iyer (2026). ToolChoiceConfusion: Causal Minimal Tool Filtering for Reliable LLM Agents. arXiv:2606.06284 | https://arxiv.org/abs/2606.06284 | Read in full at source 2026-11-13; abstract page 2026-11-14 |
| [6] | Qu (2026). Active Epistemic Control for Query-Efficient Verified Planning. arXiv:2602.03974 | https://arxiv.org/abs/2602.03974 | Read at source 2026-11-13 (figures not read); abstract page 2026-11-14 |
| [7] | De Sabbata et al. (2024). Rational Metareasoning for Large Language Models. arXiv:2410.05563 (v3, 2025) | https://arxiv.org/abs/2410.05563 | Abstract page and v3 full text, 2026-11-14 |
| [8] | Wang et al. (2026). When Planning Fails Despite Correct Execution: On Epistemic Calibration for LLM-Based Multi-Agent Systems. ICML 2026 (poster); arXiv:2605.23414 | https://arxiv.org/abs/2605.23414 | Abstract read 2026-11-14 |
| [9] | Horvitz (1988). Reasoning Under Varying and Uncertain Resource Constraints. Morgan Kaufmann Publishers | https://www.microsoft.com/en-us/research/publication/reasoning-under-varying-and-uncertain-resource-constraints/ | Microsoft Research page read 2026-11-14; the page names no proceedings |
| [10] | Russell & Wefald (1991). Principles of metareasoning. Artificial Intelligence 49(1–3), 361–395 | https://doi.org/10.1016/0004-3702(91)90015-C | † Crossref only; no abstract in the record |
| [11] | Kirsh & Maglio (1994). On Distinguishing Epistemic from Pragmatic Action. Cognitive Science 18(4), 513–549 | https://doi.org/10.1207/s15516709cog1804_1 | † Crossref only; the abstract deposited with Crossref was read, the publisher page was not |
| [12] | Kadavath et al. (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221 | https://arxiv.org/abs/2207.05221 | Abstract read 2026-11-14 |
| [13] | Zhu et al. (2023). On the Calibration of Large Language Models and Alignment. Findings of EMNLP 2023 | https://aclanthology.org/2023.findings-emnlp.654/ | Abstract read 2026-11-14 |
| [14] | Farquhar et al. (2024). Detecting hallucinations in large language models using semantic entropy. Nature 630, 625–630 | https://www.nature.com/articles/s41586-024-07421-0 | Abstract read 2026-11-14 |
| [15] | Zhang et al. (2024). CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models. ACL 2024 | https://aclanthology.org/2024.acl-long.578/ | Abstract read 2026-11-14 |
| [16] | Kirichenko et al. (2025). AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions. NeurIPS 2025, Datasets and Benchmarks Track | https://papers.nips.cc/paper_files/paper/2025/hash/fb122bfc3f0127a94ded048b5b03496f-Abstract-Datasets_and_Benchmarks_Track.html | Abstract read 2026-11-14 |
| [17] | Moskvoretskii et al. (2025). Adaptive Retrieval Without Self-Knowledge? Bringing Uncertainty Back Home. ACL 2025 | https://aclanthology.org/2025.acl-long.319/ | Abstract read 2026-11-14 |
| [18] | Yao et al. (2025). SeaKR: Self-aware Knowledge Retrieval for Adaptive Retrieval Augmented Generation. ACL 2025 | https://aclanthology.org/2025.acl-long.1312/ | Abstract read 2026-11-14 |
| [19] | Liu et al. (2025). Do not Abstain! Identify and Solve the Uncertainty (ConfuseBench). ACL 2025 | https://aclanthology.org/2025.acl-long.840/ | Abstract read 2026-11-14 |
| [20] | Kim et al. (2026). Understanding Reasoning in LLMs through Strategic Information Allocation under Uncertainty. arXiv:2603.15500 | https://arxiv.org/abs/2603.15500 | Abstract read 2026-11-14 |
| [21] | Wang et al. (2026). SuCo: Sufficiency-guided Continuous Adaptive Reasoning. ICML 2026, PMLR 306 | https://proceedings.mlr.press/v306/wang26dz.html | Abstract read 2026-11-14 |
| [22] | Dong et al. (2026). Value of Information: A Framework for Human–Agent Communication. ACL 2026 | https://aclanthology.org/2026.acl-long.1987/ | Abstract read 2026-11-14 |
| [23] | Chen, Hua & Xiao (2026). Relevance Is Not Sufficient Evidence: Detecting Evidence Gaps Before Generation in RAG (RINSE). arXiv:2609.37469 | https://arxiv.org/abs/2609.37469 | Abstract read 2026-11-14 |
| [24] | Liu, Padmanabhan & Viswanathan (2026). Before Agents Decide: Epistemic Action in LLM-Based Systems. arXiv:2610.00511 | https://arxiv.org/abs/2610.00511 | Abstract read 2026-11-14 |
| [25] | Yin & Zhang (2026). Failure-mode-aware uncertainty intervention routing for large language models. Knowledge-Based Systems 351, 116685 | https://doi.org/10.1016/j.knosys.2026.116685 (master list: https://www.sciencedirect.com/science/article/pii/S0950705126014115) | † Crossref only; no abstract |
| [26] | Kinalioglu (2026). EPRAG: An epistemic policy framework for action selection in multi-source enterprise retrieval-augmented generation. Knowledge-Based Systems 352, 116929 | https://doi.org/10.1016/j.knosys.2026.116929 (working timeline: https://www.sciencedirect.com/science/article/abs/pii/S0950705126016552) | † Crossref only; no abstract; "do not cite as read" (`paper/references.md`) |
| [27] | Chen et al. (2026). To Retrieve or To Think? Cross-Boundary Context Evolution for Multi-hop Complex Reasoning (EvoCtx). Findings of EMNLP 2026 | https://aclanthology.org/2026.findings-emnlp.2385/ | Abstract read 2026-11-14 |
| [28] | Mei et al. (2026). Reasoning about Uncertainty: Do Reasoning Models Know When They Don't Know? Findings of EACL 2026 | https://aclanthology.org/2026.findings-eacl.178/ | Abstract read 2026-11-14 |
| [29] | Lacombe, Wu & Dilworth (2025). Don't Think Twice! Over-Reasoning Impairs Confidence Calibration. arXiv:2508.15050 | https://arxiv.org/abs/2508.15050 | Abstract read 2026-11-14 |
| [30] | Darwiche & Hirth (2020). On the Reasons Behind Decisions. ECAI 2020 | https://doi.org/10.3233/FAIA200158 (arXiv:2002.09284) | arXiv full text (Definitions 1–3) and Crossref, 2026-11-14 |
| [31] | Darwiche & Ji (2022). On the Computation of Necessary and Sufficient Explanations. AAAI 2022 | https://doi.org/10.1609/aaai.v36i5.20498 (arXiv:2203.10451) | arXiv full text (Definition 5, Proposition 10) and Crossref, 2026-11-14 |
| [32] | Chen, Choi & Darwiche (2014). Algorithms and Applications for the Same-Decision Probability. JAIR 49, 601–633 | https://doi.org/10.1613/jair.4218 | JAIR page and PDF (Definition 1, §4.1), 2026-11-14 |
| [33] | Choi, Darwiche & Van den Broeck (2017). Optimal Feature Selection for Decision Robustness in Bayesian Networks. IJCAI 2017 | https://doi.org/10.24963/ijcai.2017/215 | Crossref record with abstract, 2026-11-14 |
| [34] | Zamfirescu-Pereira et al. (2023). Herding AI Cats: Lessons from Designing a Chatbot by Prompting GPT-3. DIS 2023 | https://doi.org/10.1145/3563657.3596138 | Crossref record; abstract read in the Semantic Scholar record, 2026-11-14 |
| [35] | Sharma et al. (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548; ICLR 2024 | https://arxiv.org/abs/2310.13548 | arXiv abstract page and ICLR proceedings page, 2026-11-14 |
| [36] | Li, Kim & Wang (2025). QuestBench: Can LLMs ask the right question to acquire information in reasoning tasks? NeurIPS 2025, Datasets and Benchmarks Track; arXiv:2503.22674 | https://arxiv.org/abs/2503.22674 | Confirmed on the arXiv page on 2026-11-15 (`paper/report.md`, reference 5) |

References [R11]–[R15] (language to logic) are listed in [`literature_review.md`](literature_review.md), Section 10. References [34] and [35] are cited in the report only as behavioural motivation: the project does not test deference to a user (review B.2).

**Not done.** The final search sweep that the novelty map asks for within 24 hours of submission was not run as part of the literature review of 2026-11-14 (review, Part D, item 15). The repository records one result of a final literature check on 2026-11-15: QuestBench [36] was found and cited (git history, commit `a635ddd`). Whether the full sweep of search terms was repeated is not recorded.
