# Pre-registration: Study 3, one diagnostic repair call for rejected extractions

Written on 2026-11-16, about 00:20 UTC, before any response for this study existed.

## 0. Standing

- **Exploratory follow-up, proposed after the held-out and rewording results had been viewed.** It is motivated by
  them: in the rewording study, EOP failed mostly because the reader rejected the model's extraction (for gemma
  on the syntax wording, 118 of 137). It is not part of the held-out confirmation or of the rewording study, and
  it changes nothing in them.
- The method tested here was designed with knowledge of the rewording results on 18 development families. It is
  run on other families (below), with prompts fixed here and not changed after the first response.
- Related work that this study does not claim to improve on: solver-message self-refinement in Logic-LM (Pan et
  al., 2023), LLM-as-semantic-parser pipelines (LINC, Olausson et al., 2023), grammar-constrained decoding (Geng
  et al., 2023), roundtrip verification and repair (Amrollahi et al., 2026). What is specific here: the effect of
  a repair step is measured on the exact formal state and on the cost-optimal plan that an exact planner derives
  from it, against an oracle.
- We planned a third arm with source-grounded, typed extraction. It is **not run**: the forced output schema of
  gemma and the frozen runner accept only the existing extraction layout, and changing them would touch frozen
  code. It is listed as future work.

## 1. Items

`experiments/run_repair.py --generate`; counts in `data/repair_v1_manifest.json`. The first 12 train families, in
sorted order, that were used by neither Study 1 nor Study 2 (`PREREG_FOLLOWUP.md`). No train family was sent to
any model before the follow-up studies. Every state of these families (87), in the **syntax** and **prose**
rewordings of the rewording study's generator (`src/msep/benchmark/rephrase.py`, unchanged): 174 items. For each
item the generator's inverse parser recovers the exact state, as in `PREREG_ROBUST.md`.

## 2. Conditions

Models: gemma-4-26b +schema and deepseek-v4-flash, the two models whose extraction broke under rewording.

Two first prompts:

- **F**: the model's frozen EOP extraction prompt (gemma: v1 under its forced schema; deepseek: v2).
- **N**: the translating prompt v3 of the rewording study.

Each with and without **one repair call**. A repair call is made only when the reader rejects the first answer. Its
prompt is the problem text, the model's first answer, the reader's message, and the v3 instructions followed by one
sentence on the form of a rule (`repair_prompt` in `run_repair.py`). There is at most one repair call per item
and prompt. The exact planner and the reader are unchanged.

**Reading an answer.** The reader is the frozen one (`state_from_extraction`). One rule is fixed here: when a
forced-schema answer contains no function call, the reader is given the message text instead. In the rewording
study such answers were counted as empty; inspection of those raw records on 2026-11-16 showed that gemma had
written its answer as message text. The count under the earlier, function-call-only reading is reported beside
it. This is the same kind of rule as Amendment 2 of `PREREG_EOP.md`.

## 3. Outcomes

All attempted: a rejected or missing extraction counts as wrong. 95% family-clustered bootstrap intervals. Per
model and prompt, pooled over the two wordings and for each wording:

1. **Exact state**: the extracted state equals the true state (same variables, known values and actions;
   logically equivalent rules), for the first answer and with repair, and the paired gain.
2. **Accepted but wrong**: the reader accepts the extraction and it is not the true state. This is the error a
   system cannot see. Reported for the first answer and with repair.
3. **Rejected**: the pipeline knows it has no state (first answer; with repair).
4. **Optimal plan** from the exact planner on resolvable states (first answer; with repair).
5. Of the rejected first answers: recovered to the exact state, accepted but wrong after repair, still rejected.
6. Calls per item.

A repair call can only change items whose first answer was rejected, so the gain in exact state cannot be
negative. **Reading fixed in advance:** repair is *useful* for a model and prompt if the lower end of the 95%
interval of the gain in exact state is above 0.05. It is *harmful* if the accepted-but-wrong rate rises with
repair and the interval of that rise excludes 0. Both are reported. There is no significance test.

## 4. Execution

- `experiments/chain_repair.sh MODEL CONCURRENCY CAP`: first answers in two passes, then repair calls in two
  passes, through the same runner (cache by job id, at most 3 attempts per job, same spend ledger).
- It starts when provider capacity is free and does not take capacity from Studies 1 and 2.
- **Inference stops at 2026-11-16 06:00 UTC.** If the chains have not finished by then for a model, the study is
  reported as not completed for that model.
- The analysis (`run_repair.py --analyze-only`) is run once, after the chains have finished.

## 5. Freeze

`data/FREEZE_REPAIR.json`; check with `python experiments/freeze_protocol.py --name REPAIR --verify`.
