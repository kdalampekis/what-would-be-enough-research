# PREREG_ROBUST.md — linguistic robustness of state extraction and EOP

**Registered:** 2026-11-14 (UTC), before any model saw any robustness item. Frozen with the generator, the
dataset, the driver and the analysis in `data/FREEZE_ROBUST.json`
(`experiments/freeze_protocol.py --name ROBUST --verify`). Decided by the PI at dev decision gate 2.

**Why.** On canonical benchmark text the EOP extraction matched the visible state in 545 of 545 dev cases
per model, and so did a deterministic parser with no model at all. The benchmark's wording is regular and
machine-generated. This study asks whether the result survives when the same problems are worded
differently, and whether an LLM extractor gives anything a parser does not.

**Separate from the held-out evaluation.** Dev families only. Nothing found here changes the EOP
configuration, and nothing is re-run on the test split because of it (PREREG_FINAL.md §7).

## 1. Dataset (`data/generated/robust_v1/`, generator `rb-v1`)

- **Base items:** v3 dev families at positions 0, 4, 8, … of the sorted family ids: 18 families, all 137
  of their states. Chosen by position, not by any model result.
- **Four variants per state** (`src/msep/benchmark/rephrase.py`), 548 items. The formal state, the handles
  (Q, F1, K2, …), the action names, the costs and every oracle label are those of the base item. Only the
  wording of the state description changes; the task instructions and output format after it are
  unchanged.
  - **lexical** — same layout, order and rule notation; different terminology (e.g. "Constraints",
    "Established so far", "evidence query", "calculation", "price", "holds / does not hold").
  - **syntax** — canonical terminology and order; facts, rules, known values and actions as sentences
    with a different structure. Rules are in words ("K4 is true whenever K2 is false"; "Q is true exactly
    when …"); every compound sub-statement is in parentheses so that each rule has one reading.
  - **reorder** — canonical wording; sections and the items inside them in a different order.
  - **prose** — running paragraphs without list markup, combining the lexical terminology, the sentence
    forms and a different order. The least template-like rendering.
- **Validation (all 548 items; also all 5,076 variants of the train split during development):** an
  inverse parser written for these templates recovers, from each rendered unit, a state equal to the
  canonical one (same variables and kinds, known values, actions with costs and reveals, logically
  equivalent rule set: `eval/extraction_match.py`); every handle and action name occurs in the variant;
  generation is deterministic. Results: `data/robust_v1_validation.json` (0 failures). The generated items are not in git (as for the other pools); `python experiments/generate_robust.py` rebuilds them byte-identically and the freeze pins their hash.
- **Limit of that validation:** it shows that the intended reading recovers the state. It cannot show
  that no other reading is plausible. For that, an independent reader audited a sample (below).
- **Independent audit for ambiguous wording:** 24 train-split variants (6 per kind, 24 different
  families, seed 20261114, texts under 7,000 characters), read by a separate Claude agent that had only
  the texts (no code, no data, no labels). It wrote down the formal state it understood and listed every
  phrase with more than one reasonable reading. Its states were then compared with the true states by
  program. The reader is a language model, not a person; this is stated wherever the audit is cited.
  Outcome and any wording fix made before the freeze: `ROBUST_AUDIT.md`.
- Variants were generated and validated without any model inference. One property is known in advance
  from the generator alone: the benchmark's own parser still reads the *reorder* variants (137 of 137)
  and none of the others.

## 2. Conditions (End-to-End mode; the four dev models with their frozen settings)

- **A — native** prompt on the variant text.
- **B — structured obligation prompt** (S1) on the variant text. For gemma +schema, the message-text
  parse of PREREG_EOP Amendment 2 is used where no function call was made, and this is labelled.
- **EOP — the frozen configuration of PREREG_FINAL §3:** extraction prompt v2 (gemma +schema: prompt v1
  under its forced schema), then the unchanged planner. Primary mitigation condition.
- **EOP-N — normalising extraction prompt v3** (`controllers/extraction_v3.py`), then the same planner.
  Registered now, before any response, because prompt v2 tells the model to copy rules "exactly in the
  same notation" and names the canonical section "Known so far"; on reworded text those instructions do
  not literally apply. v3 asks for the same JSON and tells the model to translate. It separates "the
  frozen prompt's wording" from "the model cannot formalise the text". Secondary; never used on test.
- **P — deterministic parser + planner** (no model).
- **Canonical reference:** A, B, EOP and P on the same 137 states in canonical wording, from the dev runs.

## 3. Questions and outcomes

All attempted; a failed call, unparsed answer, invalid extraction or planner error is incorrect.
Parsed-only figures separately. 95% family-clustered bootstrap intervals. Reported per wording and per
model, never only pooled.

1. **Does state extraction stay correct?** Share of items whose extracted state equals the canonical
   state exactly; which field is wrong (variables, rules, known values, actions); invalid extractions.
2. **Does EOP stay sufficient and optimal?** Plan optimality and sufficiency on resolvable states;
   correct stopping on ALREADY_SUFFICIENT and NEITHER.
3. **How much is lost relative to canonical wording?** Paired difference variant − canonical, per
   condition (A, B, EOP, EOP-N, P).
4. **Does the LLM extractor give robustness beyond the parser?** EOP − P and EOP-N − P per wording.
5. **Does EOP keep its advantage?** EOP − A and EOP − B per wording.

**One registered test:** EOP − A on plan optimality, resolvable states, pooled over the four wordings,
per model; one-sided family-clustered bootstrap p (share of 10,000 resamples ≤ 0, seed 0), Holm across the
four models, α = 0.05. Everything else is descriptive with intervals.

Any outcome is a result. If extraction breaks under rewording, the conclusion is that turning language
into a reliable formal state is the bottleneck, and it is reported that way.

## 4. Execution

`experiments/chain_robust.sh MODEL CONCURRENCY CAP` per model: frozen extraction, v3 extraction, native,
structured prompt, then one fill pass. 548 × 4 = 2,192 calls per model, 8,768 in total, same cumulative
spend cap as the held-out run (519.4324 credits). Analysis: `experiments/run_robust.py --analyze-only`.
No prompt, generator, planner or scoring change after the first robustness response.
