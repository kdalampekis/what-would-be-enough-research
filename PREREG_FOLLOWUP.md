# Pre-registration: two follow-up studies (wording clarity; cost sensitivity)

Written on 2026-11-15, about 21:00 UTC, before any response for either study existed.

## 0. Standing of these studies

- They were **proposed after the held-out results had been viewed** (first viewed 2026-11-15 20:23 UTC, see
  `results/aggregate/final_test/INTERIM_NOTE.md`). They are motivated by those results.
- They are **new studies on new items**. They are not part of the held-out confirmation (`PREREG_FINAL.md`) and
  cannot become part of it. Nothing in the held-out or rewording data, prompts, scoring or results changes.
- Study 2 is experiment E10 of the original plan (`EXPERIMENT_PLAN.md`). The decision of 2026-11-14 not to start
  E10 is replaced by the project owner's instruction of 2026-11-15 to run it.
- Evidence tier in the report: "follow-up, registered after viewing the held-out results".

Both studies use **train-split families only**. No train family was sent to any model before these studies
(checked against the complete call log on 2026-11-15). The two studies use disjoint families.

## 1. Study 1: does unambiguous wording remove the stopping errors?

**Background.** The benchmark text says of every computational fact that "its certified value is not yet known",
while the "Known so far" line can list such a value and the action for it is usually still offered. On the
held-out split, 21 of the 34 unnecessary plans of qwen3.5-397b on newly sufficient states only re-obtain values
that the text lists as known. The stopping errors may come from the wording, from the model, or from both.

**Intervention.** Each state is rendered twice. W0 is the benchmark text, unchanged. W1 differs in two lines only:

| | W0 | W1 |
|---|---|---|
| Header of the computational facts | `...; its certified value is not yet known):` | `...; its certified value is unknown unless it is listed under "Known so far"):` |
| Known-values line | `Known so far: ...` | `Known so far (established values, including certified results of computations already run): ...` |

Variables, rules, known values, actions, costs, certified computations and oracle labels are identical; the
generator asserts that no other line differs and re-solves every state with the oracle.

**Items** (`experiments/generate_followup.py`; counts in `data/followup_v1_manifest.json`). The first 60 train
families in sorted order. From each: the ALREADY_SUFFICIENT, COMPUTATION_ONLY, BOTH and NEITHER siblings, and every
counterfactual-pair state that one edit turned into ALREADY_SUFFICIENT. 436 states, 872 items:

- 256 ALREADY_SUFFICIENT states: 60 sufficient from the start, 196 after one edit. 237 are *exposed* (the state
  offers a computation whose results are all listed as known, which is where W0 is ambiguous) and 19 are not.
- 60 COMPUTATION_ONLY, 60 BOTH and 60 NEITHER states as controls.

Items were chosen by these rules and oracle labels only. No model output was involved.

**Condition.** Native answer, End-to-End mode, the unchanged answer prompt. Models: qwen3.5-397b,
gemma-4-26b +schema, and qwen3.8-27b as a near-ceiling control. deepseek-v4-flash is not included: its capacity
is reserved for finishing the held-out run.

**Outcomes.** All attempted is the primary basis: a missing or unreadable answer counts as the bad outcome of each
measure. Parsed-only values are reported beside it. Every comparison is paired within state (W1 − W0) with a 95%
family-clustered bootstrap interval.

1. **Primary.** Rate of proposing any action on the 256 ALREADY_SUFFICIENT states. One-sided family-cluster
   bootstrap p-value for a reduction under W1 (10,000 resamples), Holm-adjusted across the three models.
2. Rate of plans that include a computation whose results are all listed as known ("re-certification").
3. Correct stopping (empty plan and the right answer; on NEITHER: empty plan, "defer", class NEITHER).
4. **Check for harm.** Premature stopping on COMPUTATION_ONLY and BOTH states (says the state is sufficient, or
   gives an empty plan). W1 must not raise it; a rise whose interval excludes 0 is reported as harm.

Secondary: plan optimality and resource-class accuracy on the control states; all measures by group (exposed or
not; sufficient from the start or after one edit).

**Reading fixed in advance, per model.**

- *The wording contributes* if the primary reduction has Holm p < 0.05.
- *The error persists without the ambiguity* if the lower end of the 95% interval of the W1 rate is above 0.05
  (the threshold of the registered held-out test).
- Both can be true. If neither is, we say the study does not separate the two for that model.
- This is a new wording intervention. It is not a replication of the held-out stopping test.

## 2. Study 2 (E10): do models follow the cheapest plan when a price changes?

**Items.** From the frozen cost-variant file (`data/generated/variants_v3/cost.jsonl`, generator
`src/msep/benchmark/variants.py`): for a state with an action d that is in some minimal sufficient plan but in no
cheapest one, d's cost is set to b − 1, b, b + 1 and its original value, where b is the exact cost at which d's
plan ties the cheapest plan. Everything else in the state is unchanged.

- *below* (b − 1): every cheapest plan contains d. The cheapest plan has changed.
- *equal* (b): plans with and without d tie; all tied plans count as correct.
- *above* (b + 1, and the original cost): no cheapest plan contains d.

`generate_followup.py` re-solves every item with the oracle and checks these three properties and the stored
labels. Sweeps without all three sides (a cost below 1 would be needed) are dropped before families are chosen:
49 sweeps. Then the first 60 train families, in sorted order after the 60 of Study 1, that have a complete
sweep: 209 sweeps, 780 items (209 below, 209 equal, 362 above).

**Condition.** Native answer, Detection-Controlled mode. Models: qwen3.5-397b, qwen3.8-27b, gemma-4-26b +schema.

**Outcomes.** All attempted primary; parsed-only beside it; 95% family-clustered bootstrap intervals.

1. **Primary.** Within each sweep, optimal-plan rate on the above item (b + 1) minus the rate on the below item
   (b − 1). One-sided bootstrap p-value for "above is higher" (10,000 resamples), Holm-adjusted across the three
   models. *Cost insensitivity is supported* for a model if Holm p < 0.05.
2. Optimal and sufficient rates on each side; share of flip pairs with both sides optimal; rate on the below item
   given that the above item was optimal.
3. What the model did on below items: cheapest plan; kept a plan that was cheapest before the price change;
   another sufficient plan that is not the cheapest; insufficient plan; no usable answer. Mean excess cost of
   sufficient plans.
4. Control pairs in which the price changes and the cheapest plan does not (b + 1 against the original cost).

Baselines, both fixed by construction: a cost-blind policy that keeps the plan of the above item (0 on below
items, 1 elsewhere) and the exact planner on the true state (1 everywhere). EOP is not run in this study: its
planner is exact given the state, so its score at a price boundary equals its extraction accuracy, which the
held-out and rewording runs already measure. We make no claim that EOP has learned cost-sensitive planning.

## 3. Execution

- `experiments/chain_followup.sh MODEL STUDY CONCURRENCY CAP`, two passes, through the same runner as all other
  runs: jobs cached by id, at most 3 attempts per job, rate-limit waits are not attempts, same spend ledger.
- Order: Study 1 first. Study 2 starts when provider capacity is free. The held-out recovery of deepseek-v4-flash
  keeps its 12 concurrent calls until it ends or its cut-off (2026-11-16 00:00 UTC).
- **Inference stops at 2026-11-16 03:00 UTC.** A study is analysed for a model only if its first pass covered every
  item of that model; otherwise it is reported as not completed for that model. If Study 2 does not reach that
  point for any model, it is reported as not executed. Nothing is dropped because of its results.
- **The analysis (`experiments/run_followup.py --analyze-only`) is run once, after the chains have finished or the
  stop time has passed.** No prompt, item, measure or reading above is changed after the first response.
- Model settings as in `configs/models.json`, unchanged from the held-out run; the served model is recorded for
  every response.

## 4. Freeze

`data/FREEZE_FOLLOWUP.json` pins this file, the generator, the runner and its chain script, the prompt and scoring
code, the datasets and the model settings by SHA-256. Check with
`python experiments/freeze_protocol.py --name FOLLOWUP --verify`.
