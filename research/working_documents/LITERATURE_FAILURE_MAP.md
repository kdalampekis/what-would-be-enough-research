# LITERATURE_FAILURE_MAP.md
# Experimental failure modes in six related papers, and what they imply for MSEP v4

**Compiled:** 2026-11-13. **Purpose:** ground the Challenge Tier v4 design (`CHALLENGE_V4_DESIGN.md`)
in measured failures, not in a summary of them.

**How this was checked.** Each paper was read on arxiv.org (abstract page and full HTML v1/v2;
MT-InfoSeek also its project page). Numbers below were read from the text or tables, with the
location given. Where a part was not read verbatim (figures, some appendix tables, a PDF that
exceeded the fetch limit) it is said so. A secondary summary (a chat-assistant digest pasted into
the project on 2026-11-13) was checked claim by claim; its errors are listed per paper.
"Mine" marks an observation of ours, not the authors'.

All six papers exist at the cited arXiv ids with the cited titles. This supersedes the
2026-11-03 reference check in `NOVELTY_MAP.md` §9, which could not reach arxiv.org and listed
SURE-Act as not found.

---

## 1. MT-InfoSeek — "Do LLMs Know What to Ask and When? Evaluating Multi-Turn Information Seeking" (arXiv 2608.14808, v1, 2026-08-14)

**Read:** abstract, intro, §4, §5, App. A, B, C.1–C.6, D.1–D.3, project page. Not verbatim: §3.2–3.3 main text, App. E–G, figures; the PDF exceeded the fetch limit.

1. **Experiment.** Information seeking as a k-underspecified CSP: the target is known when all feasible
   assignments agree (Def. C.1); a minimal k-sufficient set (MSS) is a sufficient set of k variables
   with no smaller sufficient set (Def. C.4). Tasks: predict k; identify the MSS with or without k;
   solve sequentially (≤10 turns; 20Q 20 turns). 5,251 problems / 9,006 task instances (abstract; the
   project page says 8,912 — inconsistent). Models: GPT-5, GPT-5-mini, Gemini-3-Flash, Qwen3-4B-Thinking,
   Qwen3-30B-A3B-Thinking-FP8, gpt-oss-20B; a subset adds Gemini-3.1-Pro, gpt-oss-120B,
   Qwen3-Next-80B-A3B-Thinking-FP8 and the Qwen3.5 family. LLM oracles answer in 20Q and ClinGuide-MT.
2. **Failures.** Models almost never predict k=0 ("0.6±0.8%"); k accuracy "below 0.50 for k≥2", with
   under-prediction ">4×" more common than over-prediction at k=2. Free MSS choice: "no model exceeds
   0.4 accuracy at k=2 or 0.2 at k=3"; giving the true k helps "only modestly". In GSME-Q-MT with one
   query per turn models "stop too early and directly guess". Possible counter-evidence not read
   verbatim: Table 14 may show GPT-5 near ceiling on Logic-Q-MT (k=3 sufficiency ≈0.955) — check before
   citing a blanket "models fail".
3. **Explanation.** Shown: sufficiency falls 25–42 pp from k=1 to k=4 (GeneReg-MT, App. C.5); some
   failures are integration rather than questioning (same dialogue, different answer models, Fig. 8b).
   Interpretation, not tested: "the harder challenge is identifying which variables form the
   target-relevant MSS"; why k is underestimated is argued (App. B.1), not tested.
4. **Confounds / limitations.** Authors: no noisy users, all queries equal cost, LLM oracles, missing
   variables are the only underspecification. Mine: model lists differ across settings (not
   like-for-like); 20Q is one problem (405 tasks); correlations over 6–14 models are small-n.
   **Question order** is studied only in ClinGuide-MT, observationally (stratification and regression
   on Damerau-Levenshtein order similarity); no experiment forces a wrong order.
5. **Test for MSEP.** Equal-cost information-only MSS identification is what MT-InfoSeek already
   measures. Our distinct test: minimal sufficient plans that **mix** information and certified
   computation with **unequal costs**, scored by an exact oracle, including the cases MT-InfoSeek
   lacks (BOTH, NEITHER, ALREADY_SUFFICIENT).
6. **Redundant if** we report only information-only minimal sets, equal costs, or "k" prediction; or if
   we claim "models underestimate missing information" as our finding.

**Secondary-summary check:** (a) underestimate how much is missing — verified (abstract; Takeaway 1).
(b) given k, still fail to find the exact variables — verified (Takeaway 2). (c) sequential beats
up-front — verified with a caveat: spreading queries across turns helps, but forced one-per-turn causes
early stopping. (d) wrong order lowers accuracy even with all information — verified with a caveat:
ClinGuide-MT only, LLM oracle, observational. The summary's link and citation should point to
arXiv 2608.14808 (NOVELTY_MAP cites the Microsoft page).

---

## 2. Ask, Relax, or Act? — "Evaluating Actionable Indeterminacy in LLM Preference Reasoning" (arXiv 2610.03102, v1, 2026-10-02)

**Read:** abstract, §1–6, App. B.3–I.1, most tables. Not verbatim: App. A, B.1–B.2 (incl. Table 5), I.2–P. No limitations section in the table of contents.

1. **Experiment.** Four structures (object allocation, meeting scheduling, apartment choice, stable
   matching), n ∈ {4,6,8}, three seeds (36 cells). One information source varies per task
   (preferences, objectives, constraints). Exact solvers label Act / Ask-Preference / Ask-Objective /
   Relax. Matched pairs: each pair "changes whether intervention is necessary" (§2.2); e.g. preference
   pairs "hide one adjacent comparison". 4,320 prompts in the common V3 subset (720 pairs per source).
   Models: GPT-6-Astra, Claude-5-Sonnet, Gemini-3.1-Pro, gpt-oss-120b; single turn, no tools.
2. **Failures.** Matched-pair correctness (IFC, both members right) is well below item accuracy:
   GPT-6-Astra 92.57% accuracy vs 85.56% IFC (§3.1); Claude-5-Sonnet IFC 76.39 (App. C);
   gpt-oss-120b 83.54 / 70.37 (App. B.4). Errors are mostly **over-intervention**: 303 of 321 Astra
   errors and 468 of 551 Claude errors are on Act tasks (§3.2). Relax: all 720 Relax labels correct,
   yet no response passes the repair-and-act check (§3.3).
3. **Explanation.** Evidence: error counts and the output-specification comparison (§5). Description
   only, no ablation: models "repeatedly fail to act when the available information already suffices".
4. **Confounds / limitations.** Authors: within-model comparisons only; gpt-oss truncations (185);
   Claude quota gaps; one response per prompt. Mine: no confidence intervals for few-point gaps; the
   explicit-output condition also defines the label strings, so clearer labels and better reasoning are
   confounded; label correctness depends on the accepted-set rule.
   **Output specification changes decisions (§5.3, Table 1, 2,160 tasks):** Astra accuracy
   92.59 → 94.58 → 97.59 and IFC 85.74 → 89.17 → 95.19 (original / explicit JSON / JSON+evidence);
   Claude and Gemini rise similarly. Counter-evidence: in an earlier gpt-oss setting accuracy fell
   77.2 / 74.7 / 71.1 (App. H); Claude's answer order and token cap also move accuracy (Tables 25, 28).
5. **Test for MSEP.** Matched single-edit flips where the edit changes the **minimal sufficient plan**
   (not only whether to intervene), scored on both members and on the **transition** (the plan change
   equals the oracle's plan change). Report excess inconsistency over what independent errors predict.
6. **Redundant if** the flip only toggles intervene/act, or the metric is only pair correctness of a
   decision label: that is their IFC.

**Relevance to our own data:** their §5 is independent evidence for what we saw on 2026-11-13 — the
forced-schema gemma condition changed plans, not only format (−0.14 optimal on items parsed in both).
Output format is a treatment, not a nuisance.

**Secondary-summary check:** (a) 92.57% vs 85.56% — verified (§3.1; the paper's name for the measure is
IFC). (b) explicit outputs improved decisions, not only format — verified in substance for the three
API models, with the gpt-oss counter-example above.

---

## 3. Agents' Last Doubt / SURE-Act (arXiv 2610.24194, v1, 2026-10-16)

**Read:** full HTML v1 (re-fetched with offsets to cover all ~121k characters).

1. **Experiment.** ToolSandbox only. Action categories: Ask (user), Search (read-only lookup),
   Act-Reversible, Commit-Irreversible. Counterfactuals: clone the state, force one action category for
   one turn, let the backbone finish; one temperature-0 rollout per action; labels from Qwen3-8B/14B
   continuations. 1,036 checkpoints, 378 tasks, 82 families. Controller: Qwen3-1.7B + LoRA predicting
   success, cost and critical error; family split 60/20/20. End-to-end with Qwen3-4B/8B/14B on the dev
   pool and 89 unseen families; stopping rule hands back after k=3 identical proposals.
2. **Failures.** Offline on unseen families: "-0.0000 (SE 0.0003)" (D.3). Ask chosen on 0.36% of
   natural decisions (D.1). Lookup vs reversible action: the controller chose a reversible change "on 53
   of 53 occasions" where lookup was best (D.2). Source shift: "0 of 24 pairs" correct in both
   conditions (D.1). Label instability: best action changed on 345 of 725 checkpoints (D.1). Captured
   headroom 8.3% (D.4). Critical errors rise (+0.0220 dev).
3. **Explanation.** Tested: a bag-of-words baseline is at chance and adding reversibility classes does
   not help, from which the authors infer the controller's input "cannot express that distinction"
   (D.2). The stopping-rule analysis (−0.77 correlation between intervention rate and score) is called
   descriptive. Speculation: the tau2-bench collapse is attributed to truncated branches, not relabelled.
4. **Confounds / limitations.** Authors: one benchmark, one rollout per label, one-turn interventions.
   Mine: the source-shift test is one paragraph — no construction details, backbone or per-condition
   numbers; Ask is almost never learned, so ask-vs-lookup is barely tested; many contrasts, no
   multiple-comparison correction; the abstract's best gain (0.0575) has an interval including zero.
5. **Test for MSEP.** Their source shift is **ask vs lookup — both information**. Ours would be
   **information vs certified computation**, which their setting does not contain. But see the design
   risk: in MSEP a COMPUTE action can only exist when X is derivable from visible inputs (A10/F1), so a
   naive source switch is readable from the action menu (`CHALLENGE_V4_DESIGN.md`, T2).
6. **Redundant if** the switch is between two information channels, or between "ask" and "act".

**Secondary-summary check:** (a) 0/24 matched source-shift pairs — verified (D.1). (b) "no
generalisation to 89 new families, essentially zero benefit" — **partly wrong**: true offline (D.3), but
end-to-end Table 3 gives positive unseen-family gains (+0.0216 8B, +0.0575 4B, +0.0252 14B; the 4B and
8B intervals include zero).

---

## 4. Same Signal, Opposite Meaning / DIAL (arXiv 2605.06908, v2)

**Read:** abstract, §1–7, Tables 1–5, App. D.1–D.6, E, F.1–F.4; partly G.1. Not read: B.2, C, G.2–G.6, H.

1. **Experiment.** "Additional computation" is an optimizer invoked at a step (top-K=5 candidates, N=5
   truncated rollouts, H=3). Benefit U = E[R | optimizer] − E[R | base policy] (Eq. 1). Signal: token
   entropy (plus other features in DIAL). Environments: HotpotQA, APPS, WebShop, FEVER, TWExpress,
   Plancraft. Models: Qwen3-4B-Instruct, Phi-3.5-mini-Instruct, Llama-3.1-8B-Instruct; three seeds.
2. **Failures.** Spearman ρ(entropy, U) changes sign across models and environments (Table 1), e.g.
   FEVER Phi −0.156 vs Llama +0.428; HotpotQA Qwen −0.327 vs Phi +0.184. Reversing DIAL's gate weights
   costs up to −37 SR points (Table 3). Extra computation can fall below no computation (Qwen FEVER
   CATTS 32.2% vs 37.0% baseline, §5.2; Plancraft s1_budget 16.3% vs 29.8%).
3. **Explanation.** Evidence: one controlled study (HotpotQA, Qwen, Table 4). The Type I/Type D account
   is "a regime-level abstraction", "not a mechanistic claim" (§3.3).
4. **Confounds / limitations.** Mine: Table 7 and Table 10 give conflicting FEVER always-trigger numbers
   (99.8% vs 59.8%); most ablations are on Qwen only; cost excludes the exploration phase; no
   significance tests found.
5. **Test for MSEP.** Not transferable to v3/v4 as is: in MSEP a certified computation adds knowledge
   and never lowers sufficiency (F1). What does transfer: computation can be **unnecessary or not worth
   its cost** — already measured as redundancy and excess cost. A "computation can hurt" test needs a
   separate approximate/stochastic computation setting (out of scope for v4).
6. **Redundant if** we claim that uncertainty is a poor proxy for compute need, or that compute need
   and compute suitability differ.

**Secondary-summary check:** FEVER −0.156 (Phi-3.5) vs +0.428 (Llama-3.1) — verified (§3.2, Table 1);
it is Spearman ρ. The harm conclusion is supported by Table 3 and §3.2, not by that pair itself.

---

## 5. ToolChoiceConfusion — "Causal Minimal Tool Filtering for Reliable LLM Agents" (arXiv 2606.06284, v1, 2026-06-04)

**Read:** abstract and full HTML v1 (two reads covering all of it). No appendix. Code not fetched.

1. **Experiment.** One agent step = choose one tool given query, symbolic state and visible tool
   schemas; ≤6 steps. 100 synthetic tools incl. distractors; calendar, email and files, 34 tasks each
   (102). Tools have required variables R and produced variables E; CMTF does a breadth-first search over
   symbolic states and exposes only the first tool on a shortest path to the goal. Models: Amazon Nova 2
   Lite, Nova 2 Pro Preview, Claude 3.5 Haiku, Claude Sonnet 4. 2,448 runs.
2. **Failures.** Table 4 (aggregate): all tools success 0.83 (1.25 wrong tools/task); keyword top-5 0.61
   (2.36); keyword top-10 0.72; state-aware (executable only) 0.65 (1.98); full causal path 0.99; CMTF
   0.99 (0.01). Relevant ≠ executable ≠ causally sufficient (§3.2).
3. **Explanation.** Evidence: more wrong-tool calls under keyword and state-aware filtering (§7.2),
   read as "relevance is not necessity" (§8.1). Untested: "plausible but operationally incorrect"
   account, claims about small models (one model, Haiku).
4. **Confounds / limitations.** Authors: synthetic environment, hand-written contracts, goals assumed
   mappable to states, four models, wrong-tool scored against one gold chain. Mine: the near-perfect
   CMTF result may be **partly circular** — it shows one tool computed from the same contracts that define
   the task, so the model can hardly choose wrongly; no variance or significance tests; distractors and
   contracts written by the authors.
5. **Test for MSEP.** It is a **filtering method** that uses symbolic contracts; we would **evaluate the
   model's own pruning** against an exact oracle. The construct is the one gemma failed on
   (2026-11-13: sufficient plans padded with oracle-irrelevant and relevant-but-insufficient actions).
   Test: hold the number of actions and prompt length fixed and vary only how many offered actions are
   *relevant but unnecessary* (share variables with the target's support but are in no minimal plan).
6. **Redundant if** we only show that distractors hurt, or that filtering tools helps; or if difficulty
   comes from raising the number of tools.

**Secondary-summary check:** 61% / 65% / 83% / 99% — verified as fractions in Table 4 (aggregate over
four models and 102 tasks; one registry of 100 tools, no tool-count sweep).

---

## 6. Active Epistemic Control for Query-Efficient Verified Planning (arXiv 2602.03974, v1, 2026-02-03)

**Read:** full HTML v1. Figures 1–3 are images and were not read; ablation and backbone numbers come from the text.

1. **Experiment / method.** Grounded store (observations and query results) vs belief store (world-model
   predictions "never treated as truth"). Query when a prediction is ambiguous or uncertain, else
   simulate. Commit only if a verifier passes: preconditions grounded or entailed, plus a pullback check
   defined in another paper. ALFWorld (134 tasks, 50 steps); ScienceWorld is marked "(planned)" in §4.1
   yet reported in §5.2. Backbones: GPT-4, Qwen3-14B, DeepSeek-R1-14B, Llama-3-8B; main model unnamed.
2. **Results.** ALFWorld 98.7% vs WALL-E2.0 98.3% (Table 1; the authors call the gains "modest"; 0.4
   points ≈ half a task). Ablation (§5.3.1): failure rate 2 (full) vs 9 (no verification) vs 4 (no
   gating). Success rises 88% → ≈98% over refinement iterations (§5.3.2).
3. **Explanation.** "model-based hypothesis filtering alone is insufficient" (§5.3.1). Causes in §6
   (grounder errors, incomplete entailment) are not measured; no failure taxonomy.
4. **Confounds / limitations.** Mine: "failure rate" is undefined (2 cannot be 100 − 98.7); 98.7 is not
   k/134 for any k; "query-efficient" is never measured as query counts; no token numbers despite claims;
   iteration count behind the headline is unstated; single-author v1; no variance.
5. **Test for MSEP.** It mixes querying and (simulated) inference in a planner but does **not evaluate
   minimal or optimal sets of epistemic actions** (§6 of the agent report: only success, failure and
   replanning rates). For us it is a **baseline idea for the mitigation**: compare the Epistemic
   Obligation Planner against a simple grounded-verification controller (commit only when every
   obligation is grounded or certified), not only against native LLMs.
6. **Redundant if** we present epistemic control or "query before committing" as our contribution.

**Secondary-summary check:** (a) 98.7% on ALFWorld — verified (§5.1, Table 1), with the averaging
caveat. (b) "failures increase from 2 to 9" — verified as text, but it is an undefined "failure rate",
not a count, and the figure was not readable.

---

## Cross-paper summary

| Failure mode (measured) | Paper | Already in MSEP v3? | v4 test |
|---|---|---|---|
| Item accuracy ≫ matched-pair correctness | Ask/Relax/Act (85.56 vs 92.57) | Families are counterfactual but not single-edit; on v3 pair correctness ≈ independence (see design doc) | T1 single-edit flips with transition scoring |
| Over-intervention when information suffices | Ask/Relax/Act (303/321 Astra errors on Act) | ALREADY_SUFFICIENT siblings, E2/E8 | T1 flips into/out of ALREADY_SUFFICIENT |
| Source of the missing fact ignored | SURE-Act (0/24) | No | T2, restricted form only (A10 risk) |
| Relevant ≠ necessary | ToolChoiceConfusion; MT-InfoSeek MSS | Action categories; E5; gemma redundancy | T3 at fixed action count and length |
| Underestimating how much is missing | MT-InfoSeek | Partly (plan insufficiency) | none new |
| Order / contingency of queries | MT-InfoSeek (observational) | No — static plans only (F2) | T4, separate extension, new oracle |
| Compute signal sign flips; compute can hurt | DIAL | Not applicable (certified computation, F1) | none in v4 |
| Verified commitment beats simulation alone | Active Epistemic Control | Mitigation idea | baseline for the mitigation, not a v4 test |
