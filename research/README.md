# Guide to the `research/` folder

This folder answers the question of how the project "What Would Be Enough? Evaluating Minimal Sufficient Epistemic Plans in LLM Agents" came to its research question, what it planned, what it decided, and what remains open. It holds the literature and research-story part of the public release. The authoritative statement of the final claims is the report, [`../paper/report.md`](../paper/report.md); the documents here explain and trace it, and none of them makes a claim stronger than the report does.

## Documents and the question each one answers

| Document | Question it answers |
|---|---|
| [`literature_timeline.md`](literature_timeline.md) | Through which stages did the field move, from classical metareasoning to the 2026 work on epistemic actions, and what did each stage leave open? |
| [`literature_review.md`](literature_review.md) | For each of the closest papers: what did it ask, do and find, where does it stop, and how does this project differ? Includes one comparison matrix. |
| [`research_gap_and_novelty.md`](research_gap_and_novelty.md) | What did prior work already cover, which combination does this project evaluate, and what does it explicitly not claim? Includes the statement of reuse of the author's earlier code. |
| [`research_evolution.md`](research_evolution.md) | How did the question develop from "can LLMs recognise uncertainty?" to Minimal Sufficient Epistemic Planning, how did the results refine it, and where does the evidence stand? |
| [`future_research.md`](future_research.md) | Which questions remain open, led by faithful translation from natural language to a formal state, and which planned experiments were not run? |
| [`original_roadmap.md`](original_roadmap.md) | What was the plan as first written, and what of it was executed? |
| [`research_decisions.md`](research_decisions.md) | What was each major decision, and on which evidence was it made? |
| [`hypothesis_tracker.md`](hypothesis_tracker.md) | What was every hypothesis, and what was its outcome? |
| [`working_documents/`](working_documents/) | What did the original working documents say? They are kept as written, unedited. |

## Suggested reading order

1. `research_evolution.md` for the story in a few pages.
2. `research_gap_and_novelty.md` for the boundary of the contribution.
3. `literature_timeline.md` and `literature_review.md` for the detail behind both.
4. `hypothesis_tracker.md`, `research_decisions.md` and `original_roadmap.md` for the record of what was planned, decided and found.
5. `future_research.md` for what is open.

## Conventions used in this folder

- **Sources.** Every fact, date and number comes from a document or result file in the repository, and the path is given next to it. "Not recorded" means the repository does not record the point. "(retrospective interpretation)" marks a rationale reconstructed from the records.
- **Evidence tiers.** Results are never mixed across tiers: registered held-out; registered development; prospective test of an amended method (the Epistemic Obligation Planner on held-out data); rewording study, registered separately; follow-up studies registered after the held-out results were viewed (Studies 1 to 3); exploratory or diagnostic; no-model baselines (oracle, parser).
- **References.** Numbers [1]–[36] follow the References of [`../paper/extended_report.md`](../paper/extended_report.md). [R11]–[R15] are references 11–15 of `paper/report.md`. The full list with links and verification status is in `literature_timeline.md`, Section 15. A dagger (†) marks a reference taken from Crossref and not read at the source.
- **Other papers' findings.** "The authors report" marks a number read in another paper. Such numbers are never presented as findings of this project.
- **Working documents.** The files in `working_documents/` are the originals. Some statements in them were later corrected; the corrections are listed in `literature_timeline.md`, Section 14, and the originals are left as they were. The literature timeline among them is written in Greek with English technical terms.

## Where the rest of the release is

- Report and extended report: [`../paper/`](../paper/).
- Protocol and registrations: [`../PROTOCOL.md`](../PROTOCOL.md) and the `PREREG_*.md` files in the repository root.
- Methods: [`../methodology/`](../methodology/).
- Registry of experiments: [`../experiments/experiment_registry.md`](../experiments/experiment_registry.md).
- Result files and figures: [`../results/`](../results/), [`../figures/`](../figures/).
- Index of every experiment, from hypothesis to figure: [`../docs/EXPERIMENT_INDEX.md`](../docs/EXPERIMENT_INDEX.md).
