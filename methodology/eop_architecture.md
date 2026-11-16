# The Epistemic Obligation Planner (EOP)

This document describes the mitigation tested in this project as it is implemented, not as it was first imagined. It answers: which failure EOP was meant to address; how the model's extraction of the visible state is turned into a formal state and what the reader rejects; how the planner checks sufficiency, lists obligations and finds a cheapest plan; when it stops or defers; what it never sees; which conditions it is compared with (native A, structured prompt B, EOP C and C′, verifier-only D and D′, message-text variants Bt and Dt, parser P, and EOP-N); what the extraction prompts v1, v2, v3 and the repair prompt of Study 3 say; and where EOP fails, with measured rates. The planner is exact. A score of EOP therefore measures how well the model extracts the state, not how well anything plans. On the benchmark's own wording a parser with no model extracts every state and scores the same. Formal definitions are in [formal_problem.md](formal_problem.md); scoring and statistics in [evaluation_protocol.md](evaluation_protocol.md); amendments in [protocol_amendments.md](protocol_amendments.md).

## 1. The failure it targets

The hypothesis, written before the sprint ([EXPERIMENT_PLAN.md](../research/working_documents/EXPERIMENT_PLAN.md) §2, H6): "An obligation-guided planner will reduce insufficient actions, premature stopping, and excess resource cost relative to confidence-based and generic routing baselines." The registered EOP comparison restates it "relative to native planning and a structured prompt" ([PREREG_EOP.md](../PREREG_EOP.md)). The confidence-based and routing baselines were not built ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §3, notes).

The pipeline as specified ([PROBLEM_SPEC.md](../research/working_documents/PROBLEM_SPEC.md) §14): "1. model or parser constructs the current formal state; 2. unresolved epistemic obligations are identified; 3. candidate information/computation actions are generated; 4. the formal layer checks which obligations each action can discharge; 5. a planner searches for a minimum-cost sufficient plan; 6. the agent executes only the selected plan; 7. after each step, sufficiency is re-evaluated; 8. execution stops immediately when sufficient; 9. if no plan exists, defer/abstain."

The idea in one sentence, from the report: "The Epistemic Obligation Planner (EOP) has the model extract the formal state and lets an exact planner choose the actions" ([paper/report.md](../paper/report.md) §1). The planner code and extraction prompt v1 were written before the sprint; prompts v2 and v3 and the repair prompt were written during it ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §7).

## 2. The pipeline as implemented

Source: [src/msep/controllers/realistic_planner.py](../src/msep/controllers/realistic_planner.py). The module separates two planners: "(A) `obligation_planner.py` is the oracle planner. It receives the exact formal state and the instance; it is part of the oracle and validation, not a mitigation. (B) this module sees only what an agent sees: the prompt text and an `AgentEnvironment` whose `execute()` returns observed values. It never receives the latent world or any oracle label."

| Component | Implementation | What it does |
|---|---|---|
| StateExtractor | a model's extraction read by `state_from_extraction` (EOP), or `ParserExtractor` (baseline P) | text → formal state |
| SufficiencyChecker | `status` from [src/msep/oracle/logic.py](../src/msep/oracle/logic.py) | "True/False if the knowledge entails q / not-q; None if undetermined" |
| ObligationIdentifier | `ExactObligations` → `extract` in [src/msep/obligations/extraction.py](../src/msep/obligations/extraction.py) | the minimal difference sets of distinguishing pairs, by SAT; cap 512; "obligation enumeration truncated" raises an error |
| CandidateGenerator | every action on the extracted menu | – |
| ObligationVerifier | `discharges` in [src/msep/obligations/discharge.py](../src/msep/obligations/discharge.py) | an action discharges an obligation if it reveals Q or any variable of the obligation |
| PlanSearch | `HittingSetSearch`: weighted MaxSAT (RC2) | one hard clause per obligation listing the actions that discharge it; one soft clause per action weighted by its cost; if some obligation has no discharging action, there is no plan |

The obligation extraction is the same function the oracle's obligation planner uses, and the hitting-set search is the same RC2 encoding ([oracle_validation.md](oracle_validation.md) §2.3; [src/msep/controllers/obligation_planner.py](../src/msep/controllers/obligation_planner.py)). The oracle's obligation planner agrees with brute force: "Obligation planner returns an optimal plan", 9,135 checks, 0 failed; "Obligation planner defers exactly on NEITHER", 2,899 checks, 0 failed ([results/oracle_validation.md](../results/oracle_validation.md)). The realistic planner itself is checked end to end by the parser baseline P, which feeds it the exact parse of the text: optimal plan and correct stopping 1.000 on every development item set ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.11), and 1.00 on held-out data ([results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md)).

## 3. Extraction of the agent-visible state

The model reads the benchmark text followed by an extraction instruction (Section 7) and returns one JSON object with four fields ([src/msep/controllers/llm_extractor.py](../src/msep/controllers/llm_extractor.py), `EXTRACTION_SCHEMA`):

| Field | Content |
|---|---|
| `variables` | list of `{"handle", "kind"}`, kind `world` or `computed`; Q is not listed |
| `rules` | list of strings, one formula each, in the benchmark's notation |
| `known` | list of `{"handle", "value"}` |
| `actions` | list of `{"name", "kind", "cost", "reveals"}`, kind `information` or `computation` |

Computational facts stay opaque: "Computation tasks stay opaque: the extracted state never contains certified results the agent has not paid for" (module docstring). The reader attaches an `OpaqueTask` to each computed variable, so the planner cannot evaluate it. The parser baseline does the same: "Opaque tasks: the planner cannot evaluate a certified computation itself; it must run the computation action in the environment" (`ParserExtractor`).

For gemma-4-26b +schema, the extraction schema is sent as a forced function tool, as for its plan answers ([evaluation_protocol.md](evaluation_protocol.md) §2.3). For the other three models the schema is not enforced; the layout comes from the prompt.

One extraction call is made per state. "One extraction per state; the plan does not depend on the mode" ([PREREG_EOP.md](../PREREG_EOP.md), condition C).

## 4. The reader and what it rejects

The reader is `state_from_extraction` in [src/msep/controllers/llm_extractor.py](../src/msep/controllers/llm_extractor.py). The runner calls it on every extraction answer: "mitigation C: an LLM's state extraction, validated by building the formal state"; "any malformed extraction is an extraction failure, recorded as such" with the message `extraction invalid: <error>` (`_parse` in [src/msep/models/runner.py](../src/msep/models/runner.py)).

**What it rejects** (read from the code of `state_from_extraction`, the formula parser in [src/msep/benchmark/parsing.py](../src/msep/benchmark/parsing.py) and `FormalState.__post_init__` in [src/msep/world/state.py](../src/msep/world/state.py)):

| Defect in the answer | Error |
|---|---|
| No JSON object in the text, or invalid JSON | "no JSON object found"; `JSONDecodeError` |
| A required key is missing (`variables`, `rules`, `known`, `actions`, or a key inside an entry) | `KeyError` |
| A rule that is not one formula in the fixed notation, or uses a handle not declared | `ParseError`: "unknown variable", "trailing tokens", "expected …" |
| A known value for an undeclared handle | `ParseError`: "unknown handle" |
| An action that reveals an undeclared handle | `KeyError` |
| A cost that is not an integer | `ValueError` |
| Duplicate variable or action names; a variable fixed twice | `ValueError` |
| An information action that reveals a computed variable, or a computation action that reveals a world variable | `ValueError` ("Information/computation separation is structural, enforced here") |

At planning time one more case fails: if the extracted rules and known values are contradictory, `status` raises "state is inconsistent", and the item is a planner error ([src/msep/oracle/logic.py](../src/msep/oracle/logic.py); `planned_results` in [experiments/run_eop.py](../experiments/run_eop.py): "inconsistent extracted state, unknown handle, solver error"). Test: `test_inconsistent_extraction_is_a_pipeline_failure` in [tests/test_eop_driver.py](../tests/test_eop_driver.py).

**What it accepts without complaint.** A variable whose kind is not `world` is read as computed; an action whose kind is not `information` is read as a computation; a leading list number such as "1." is stripped from a rule. Above all, the reader accepts any well-formed state, whether or not it is the true one. Such an extraction is "accepted but wrong": "This is the error a system cannot see" ([PREREG_REPAIR.md](../PREREG_REPAIR.md) §3). Whether an accepted state is the true one is measured separately against the exact parse of the canonical text ([src/msep/eval/extraction_match.py](../src/msep/eval/extraction_match.py)).

**Rejection messages seen in practice.** For gemma-4-26b +schema's first answers with its frozen prompt in Study 3 (125 rejected): unknown variable 54, trailing tokens 44, expected ")" 17, expected "th…" 7, `TypeError` 3 ([results/aggregate/repair/repair_report.md](../results/aggregate/repair/repair_report.md)).

## 5. Sufficiency check, obligations, search, stopping and deferral

`EpistemicObligationPlanner.plan` in [src/msep/controllers/realistic_planner.py](../src/msep/controllers/realistic_planner.py) returns a static plan, "what the planner would do, for plan-level scoring":

1. If the decision rule is not logical entailment, the output is "unsupported". Every benchmark state uses logical entailment ([formal_problem.md](formal_problem.md) §9).
2. **Sufficiency check.** If the extracted state already entails Q or not-Q, the plan is empty and the planner answers.
3. **Obligations.** Otherwise it lists the obligations of the extracted state.
4. **Search.** It returns a minimum-cost hitting set of the obligations, or no plan if some obligation cannot be discharged.

The driver turns this into an answer in the same JSON as a model's answer and scores it with the same code (`_response` and `plan_to_parsed` in [experiments/run_eop.py](../experiments/run_eop.py)):

| Planner output | Answer |
|---|---|
| decided | `state_sufficient` true, class ALREADY_SUFFICIENT, empty plan, `decision` true or false |
| no plan exists | class NEITHER, empty plan, `decision` "defer" |
| a plan | class from the plan's composition (BOTH, INFORMATION_ONLY or COMPUTATION_ONLY), `decision` "defer", `stop_after_plan` true |

**Stopping and deferral follow from the extracted state.** If the extraction is exact, the planner stops exactly on ALREADY_SUFFICIENT states and defers exactly on NEITHER states, because both are decided by exact checks. If the extraction is wrong, the stop or the deferral is wrong with the same confidence. This is named as a risk in the report: "'Already sufficient: stop' from a solver looks authoritative and is only as right as the extracted state" ([paper/report.md](../paper/report.md), Appendix A).

**The execution loop is not used in the results.** The module also has `run`, which executes one action, adds the observation and re-plans: the next action "discharges the most obligations; ties by cost, then name", with at most 20 steps; it defers when no plan exists and stops when Q is decided. Every reported experiment scores the static plan only (`planned_results` in `run_eop.py` calls `plan`).

## 6. What the planner never sees

"No condition sees hidden-world truth, oracle labels, true values or certified results before COMPUTE: planning uses only the prompt text via the extraction" ([PREREG_EOP.md](../PREREG_EOP.md), "Conditions"). The same sentence is in [PREREG_FINAL.md](../PREREG_FINAL.md) §3.

| Not seen | How it is kept out | Test |
|---|---|---|
| The latent world | The planner receives only text; an `AgentEnvironment` "exposes no world" | `test_environment_exposes_no_world` in [tests/test_realistic_planner.py](../tests/test_realistic_planner.py) |
| Oracle labels, true target value, the formal state record | The driver passes only `instance_id`, `family_id` and `prompt_text` in the leakage test | `test_planning_uses_only_the_prompt_text` in [tests/test_eop_driver.py](../tests/test_eop_driver.py) |
| Certified results of computations not run | Opaque tasks | `test_planner_cannot_compute_certified_values_for_free` |
| The oracle's answers | The planner module may not import the latent world, the instance record, the oracle's plan solvers (`minimal_plan`, `solver`, `brute_force`) or the oracle planner. It does use the shared SAT primitives in `msep.oracle.logic` to decide its own extracted state | `test_planner_module_imports_no_oracle_or_hidden_state` (list `FORBIDDEN`) |

The planner's own plan is not trusted: the oracle re-scores it like any model answer (`test_static_plan_is_scored_by_the_oracle_not_trusted`). The evaluation oracle is separate and sees the true state ([paper/report.md](../paper/report.md), Figure 1).

## 7. The prompts

### 7.1 Structured prompt (condition B)

Appended to the full plan prompt; the output format is unchanged ([src/msep/models/prompts_s1.py](../src/msep/models/prompts_s1.py), `msep-s1-obligations-v1`):

```text
Before answering, reason about the epistemic obligations step by step:
1. List what is already known.
2. Decide whether the known facts already settle Q under the rules. If they do, the plan is empty.
3. If not, list the obligations: each unknown fact or uncertified computational result whose value could still change the answer about Q.
4. For each obligation, list the available actions that would settle it. An action that settles no obligation is unnecessary.
5. Choose the cheapest set of actions that settles every obligation whatever the results are, and remove any action that is not needed. If some obligation cannot be settled by any available action, no plan can justify the decision: use an empty plan and decision "defer".
You may write this reasoning briefly before the JSON object, without curly braces; the JSON object must come last.
```

The module assumed: "With a forced-schema provider condition (structured function tool) the model can only reason internally." This did not hold for gemma ([PREREG_EOP.md](../PREREG_EOP.md), Amendment 2).

### 7.2 Extraction prompt v1 (registered condition C; gemma's frozen prompt)

Appended to the state text ([src/msep/controllers/llm_extractor.py](../src/msep/controllers/llm_extractor.py), `msep-extraction-v1`, written before the sprint):

```text
Extract the formal state from the problem above. Do not solve it.
Return one JSON object:
- "variables": every fact handle (F1, F2, ...) with kind "world" and every computational fact (K1, ...) with kind "computed". Do not include Q.
- "rules": each rule copied exactly in the same notation (use the handles, "and", "or", "not", "if ... then ...", "if and only if", parentheses).
- "known": each value listed under "Known so far".
- "actions": each available action with its exact name, kind, cost and the handles it reveals.
```

### 7.3 Extraction prompt v2 (condition C′; frozen prompt of qwen3.5, qwen3.8 and deepseek)

v1 followed by the exact layout (`msep-extraction-v2`, Amendment 1, 2026-11-14):

```text
Use exactly this JSON layout (lists of objects with these keys; the values here are only an example):
{
  "variables": [{"handle": "F1", "kind": "world"}, {"handle": "K1", "kind": "computed"}],
  "rules": ["if F1 then not K1", "Q if and only if (F2 and K1)"],
  "known": [{"handle": "F2", "value": true}],
  "actions": [{"name": "ASK_F1", "kind": "information", "cost": 3, "reveals": ["F1"]},
              {"name": "COMPUTE_K1", "kind": "computation", "cost": 2, "reveals": ["K1"]}]
}
Answer with this one JSON object and nothing else.
```

Reason, from the code comment: "the v1 instructions above describe the fields in prose only, while the parser requires one exact layout; providers without schema enforcement returned equivalent content in other layouts (e.g. variables as a mapping). v2 adds the exact JSON template, as the plan prompt has always had. v1 is kept unchanged for the registered condition C." The v1 text is byte-identical inside v2 (`test_amendment1_extraction_v2_shows_the_layout_and_keeps_v1_unchanged`).

### 7.4 Extraction prompt v3 (EOP-N; rewording study and Study 3 only)

The field descriptions are replaced; the v2 layout follows ([src/msep/controllers/extraction_v3.py](../src/msep/controllers/extraction_v3.py), `msep-extraction-v3-normalising`):

```text
Extract the formal state from the problem above. Do not solve it.
The problem may word things in its own way; report its content in the fixed form below.
Return one JSON object:
- "variables": every fact about the world (handles F1, F2, ...) with kind "world" and every computational or derived fact (handles K1, ...) with kind "computed". Do not include Q.
- "rules": every rule or constraint the problem states, each written in this notation: the handles, "and", "or", "not", "if ... then ...", "if and only if", parentheses. If the problem states a rule in other words, translate it faithfully into this notation (for example "K1 is false whenever F1 is true" becomes "if F1 then not K1").
- "known": every value the problem says is already known or established.
- "actions": every available action or step with its exact name, its kind ("information" if it obtains evidence about the world, "computation" if it runs a procedure), its cost and the handles it reveals.
```

Why it exists: "prompt v2 tells the model to copy rules 'exactly in the same notation' and names the canonical section 'Known so far'; on reworded text those instructions do not literally apply. v3 asks for the same JSON and tells the model to translate. It separates 'the frozen prompt's wording' from 'the model cannot formalise the text'. Secondary; never used on test" ([PREREG_ROBUST.md](../PREREG_ROBUST.md) §2).

### 7.5 Repair prompt (Study 3)

Sent only when the reader rejects a first answer ([experiments/run_repair.py](../experiments/run_repair.py), `repair_prompt`). It contains the problem text, then:

```text
A first attempt to extract the formal state from the problem above was rejected by an automatic reader.

First attempt:
<the model's first answer, at most 6,000 characters, or "(no answer was returned)">

The reader's message: <the reader's error message>

Write the extraction again so that the reader accepts it.
<extraction prompt v3, as in 7.4, with the v2 layout>
Each entry of "rules" must be one formula in the notation above and nothing else: no other words, no explanation, no trailing text. Use only the handles listed in "variables", and Q.
```

"There is at most one repair call per item and prompt. The exact planner and the reader are unchanged" ([PREREG_REPAIR.md](../PREREG_REPAIR.md) §2). A first answer that is missing or whose call failed gets no repair call (`job2` in `run_repair.py`).

## 8. The comparison conditions

Definitions from [PREREG_EOP.md](../PREREG_EOP.md) ("Conditions" and the two amendments) and [PREREG_FINAL.md](../PREREG_FINAL.md) §3. "Strict scoring: if a call fails, an extraction is invalid or inconsistent, or B's answer does not parse, C/D count as failures (no fallback to another condition)" (PREREG_EOP).

| Label | Definition | Where it was run | Result key | Tier |
|---|---|---|---|---|
| A, native | "the model's own answer to the benchmark prompt" | dev, held-out, rewording, Studies 1–2 | `A` | as the study |
| B, structured prompt | "the same prompt plus step-by-step obligation-reasoning instructions … same output JSON" (Section 7.1) | dev, held-out, rewording | `B` | as the study |
| C, registered EOP | extraction prompt v1, then the planner | dev (all four models); held-out for gemma +schema only | `C` | registered development; on held-out, gemma's frozen configuration |
| C′, amended EOP | extraction prompt v2, then the same planner; "Nothing else changes" | dev and held-out for qwen3.5, qwen3.8, deepseek; not for gemma +schema, because "the schema supplies the layout" | `C2` | development-informed on dev; prospective test on held-out |
| D, verifier only | "B's plan, verified on C's extracted state without search: if the extracted state already decides Q, the plan is emptied and Q is answered; otherwise every action of B's plan that discharges no unresolved obligation (or is not in the extracted menu) is removed; nothing is added" | dev, held-out | `D` | registered, descriptive |
| D′ | B verified on C′'s extraction | dev, held-out | `D2` | development-informed on dev |
| Bt | "parses the JSON from the model's own message text with the standard plan parser … only where no function call was made" | gemma +schema only | `Bt` | Amendment 2, analysis only |
| Dt | Bt verified on C's extraction | gemma +schema only | `Dt` | Amendment 2 |
| P, parser | the rule-based parser `parse_state`, then the same planner; "Upper bounds (not mitigations)" in PREREG_EOP, "reported as a baseline, not only as an upper bound" in PREREG_FINAL | every item set | `upper_bound_parser_EOP` | no-model baseline |
| Oracle | "exact, 1.0 by definition" | – | – | no-model reference |
| EOP-N | extraction prompt v3, then the same planner | rewording study; arm N of Study 3 | – | rewording study (secondary); Study 3 |
| F, N, with or without repair | Study 3: first answer with the frozen prompt (F) or v3 (N), each with and without one repair call | Study 3 | – | follow-up, exploratory |

**The frozen EOP configuration on held-out data** ([PREREG_FINAL.md](../PREREG_FINAL.md) §3): C′ for qwen3.5-397b, qwen3.8-27b and deepseek-v4-flash; registered C (prompt v1 under the forced schema) for gemma-4-26b +schema, "the configuration validated on dev (the schema supplies the layout); the v2 prompt was never run with this model". "Registered C (v1 prompt) is **not** run on test for the three models without schema enforcement: it is a known instrument defect, and its dev results are the registered outcome." The report calls this configuration "EOP" and D′/Dt "verifier only".

**Labels.** "The code and PROTOCOL.md §10 call the extractor condition S2; PREREG_EOP.md calls it S3 and uses S2 for the verifier. Result keys: `C2`, `D2` for C′, D′; `upper_bound_parser_EOP` for P" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §5).

**About the parser.** "Audit (2026-11-14): the parser's only input is the prompt text; it uses a fixed grammar and no generator metadata, oracle label or hidden value. … It was written by the benchmark authors as the inverse of the benchmark's own renderer, so its score on canonical text says nothing about other wordings" ([PREREG_FINAL.md](../PREREG_FINAL.md) §3).

## 9. The planner is exact, so EOP measures extraction

The planner is exact on the state it is given (Section 2). Given the true state, it returns a cheapest sufficient plan, stops when the state is sufficient and defers when no plan exists. Any error of EOP therefore comes from the extraction. "EOP measures extraction, not planning. Its planner is exact" ([paper/report.md](../paper/report.md), Appendix A).

A parser with no model matches EOP on the benchmark's own wording:

| Item set | Parser P: optimal plan | EOP: optimal plan (frozen configuration) | Source |
|---|---|---|---|
| Dev, v3 resolvable states (both modes) | 1.000, correct stopping 1.000, 0 unparsed | C′ 1.000 for three models; gemma C 0.99 | [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.8, §4.11; [results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md) |
| Held-out, Detection-Controlled | 1.00 | 1.00 / 1.00 / 1.00 / 0.99 (qwen3.5, qwen3.8, deepseek, gemma) | [results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md) |
| Rewording, reorder | 1.00 | 0.99–1.00 | [results/aggregate/robust_dev/robust_report.md](../results/aggregate/robust_dev/robust_report.md) |
| Rewording, lexical, syntax, prose | 0.00 | see Section 10.3 | same |

"On the benchmark's own wording, a model is not needed to obtain the state" ([paper/extended_report.md](../paper/extended_report.md) §4.2). The registered test of EOP against native on held-out data is supported for all four models (Holm p < 0.001, 0.005, 0.004, < 0.001), but "the gain is large only for gemma (+0.57), and the parser with no model also scores 1.00" ([paper/report.md](../paper/report.md) §4.3). Tier of that test: prospective test of an amended method.

## 10. Where EOP fails

### 10.1 The registered prompt on the development split

Registered development tier. Optimal plans, Detection-Controlled, all attempted, 401 resolvable states ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.7, "n = 401"); the denominator 473 of the extraction column is from [paper/report.md](../paper/report.md), Appendix B, Table B1:

| Model | Native | EOP as registered (v1) | Items with no usable extraction | EOP, amended prompt (v2) |
|---|---|---|---|---|
| qwen3.5-397b | 0.96 | 0.69 | 150 / 473 | 1.00 |
| qwen3.8-27b | 0.98 | 0.65 | 163 / 473 | 1.00 |
| deepseek-v4-flash | 0.96 | 0.03 | 461 / 473 | 1.00 |
| gemma-4-26b +schema | 0.45 | 0.99 | 3 / 473 | not run |

"The registered test (EOP better than native) was supported for gemma only. That is the registered outcome and it stands." Cause: "The registered extraction prompt described the output fields in prose and never showed the layout the reader requires. Models without schema enforcement returned the right content in other layouts and were rejected" (same appendix). Registered C − A: −0.264 / −0.329 / −0.935 / +0.546; Holm p 1 / 1 / 1 / 0.0 ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.7). The amended column is development-informed: "Prompt v2 was written after the v1 failures were seen on these items: the dev score is optimistic and is not the registered result" (EXPERIMENT_INDEX §4.8).

### 10.2 Held-out split, benchmark wording

Extracted state against the exact parse of the same text ([results/aggregate/final_test/t1/t1_test_summary.json](../results/aggregate/final_test/t1/t1_test_summary.json), key `extraction_match`):

| Model (prompt) | v3 test states: exact / invalid / accepted but not exact (of 468) | T1 test items: exact / invalid (of 804) |
|---|---|---|
| qwen3.5-397b (v2) | 468 / 0 / 0 | 804 / 0 |
| qwen3.8-27b (v2) | 468 / 0 / 0 | 803 / 0 (1 wrong rule set) |
| deepseek-v4-flash (v2) | 468 / 0 / 0 | 804 / 0 |
| gemma-4-26b +schema (v1) | 456 / 6 / 6 | 790 / 6 (8 accepted but not exact) |

EOP optimal-plan rate on resolvable states, Detection-Controlled: 1.00 / 1.00 / 1.00 / 0.99 ([results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md)).

### 10.3 Rewording study (development families)

Tier: rewording study, registered separately. 137 states per wording, End-to-End, all attempted. EOP is the frozen configuration; "state" is the share of exact extractions ([results/aggregate/robust_dev/robust_report.md](../results/aggregate/robust_dev/robust_report.md)):

| Model | Wording | Native | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P |
|---|---|---|---|---|---|---|---|
| qwen3.5-397b | lexical / syntax / reorder / prose | 1.00 / 0.98 / 0.97 / 0.99 | 0.99 / 1.00 / 1.00 / 1.00 | 0.99 / 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 / 0.99 | 1.00 / 0.99 / 1.00 / 0.99 | 0.00 / 0.00 / 1.00 / 0.00 |
| qwen3.8-27b | same order | 0.98 / 0.98 / 0.96 / 0.95 | 1.00 / 1.00 / 1.00 / 0.99 | 1.00 / 0.99 / 1.00 / 0.99 | 1.00 / 1.00 / 1.00 / 1.00 | 1.00 / 0.99 / 1.00 / 0.99 | 0.00 / 0.00 / 1.00 / 0.00 |
| deepseek-v4-flash | same order | 0.96 / 0.98 / 0.93 / 0.98 | 0.99 / **0.81** / 1.00 / 0.92 | 0.98 / 0.81 / 1.00 / 0.92 | 0.88 / 0.97 / 0.99 / 0.88 | 0.87 / 0.98 / 0.97 / 0.88 | 0.00 / 0.00 / 1.00 / 0.00 |
| gemma-4-26b +schema | same order | 0.17 / 0.35 / 0.43 / 0.20 | 0.93 / **0.05** / 0.99 / 0.61 | 0.93 / 0.07 / 0.99 / 0.46 | 0.05 / 0.05 / 0.25 / 0.26 | 0.05 / 0.04 / 0.26 / 0.19 | 0.00 / 0.00 / 1.00 / 0.00 |

The registered test, EOP − native pooled over the four wordings (same file): qwen3.5-397b +0.01 [−0.00, +0.03], Holm p 0.154; qwen3.8-27b +0.03 [+0.01, +0.06], Holm p 0.014; deepseek-v4-flash −0.03 [−0.06, +0.00], Holm p 0.984; gemma-4-26b +schema +0.36 [+0.29, +0.43], Holm p 0.0 (no resample at or below 0). Supported for gemma and qwen3.8.

**How the failures look** (counts from [results/aggregate/robust_dev/robust_summary.json](../results/aggregate/robust_dev/robust_summary.json), `kinds.<wording>.extraction`):

- deepseek-v4-flash, syntax: 26 of 137 extractions invalid (formula errors 25, no text 1); no accepted extraction was wrong.
- gemma-4-26b +schema, syntax: 123 of 137 invalid (formula errors 118, no text 5). "In 118 of gemma's 137 syntax items the extraction does not parse in the planner's notation" ([paper/extended_report.md](../paper/extended_report.md) §4.3).
- gemma-4-26b +schema, prose: 50 invalid; and "24 of 137 extractions are well-formed but are not the true state" (extended report §4.3). The field counts for prose are wrong variables 18, wrong rules 22, wrong actions 2; an item can be wrong in more than one field.

"Most failures are visible: the planner rejects a malformed extraction. The exception is gemma on prose" ([paper/report.md](../paper/report.md) §4.3).

**A reader artifact in EOP-N for gemma.** Most of gemma's EOP-N items were scored as "no text" (129 of 137 on syntax, 130 on lexical). Study 3 found the cause: these "were answers written as plain text instead of the forced function call. Read as text, that prompt gives the exact state on 0.67 of the Study 3 items, so Figure 2 understates EOP-N for gemma" ([paper/report.md](../paper/report.md) §4.4). The rewording study's numbers were not changed.

### 10.4 Study 3: one repair call

Tier: follow-up, registered after the held-out results were viewed; exploratory; no test. 174 reworded items (syntax and prose) from 12 train families. All attempted ([results/aggregate/repair/repair_report.md](../results/aggregate/repair/repair_report.md); rise intervals from [results/aggregate/repair/repair_supplement.json](../results/aggregate/repair/repair_supplement.json)):

| Model | First prompt | Exact state: first → with repair (gain) | Accepted but wrong: first → with repair (rise) | Optimal plan: first → with repair | Rejected first answers: recovered / wrong / still rejected |
|---|---|---|---|---|---|
| gemma-4-26b +schema | F (v1) | 0.21 → 0.78 (+0.56 [+0.47, +0.65]) | 0.07 → 0.16 (+0.09 [+0.03, +0.15]); 12 → 27 items | 0.29 → 0.93 | 98 / 15 / 12 of 125 |
| gemma-4-26b +schema | N (v3) | 0.67 → 0.74 (+0.07 [+0.02, +0.12]) | 0.15 → 0.17 (+0.02 [+0.01, +0.05]); 26 → 30 items | 0.75 → 0.87 | 12 / 4 / 15 of 31 |
| deepseek-v4-flash | F (v2) | 0.89 → 0.97 (+0.09 [+0.04, +0.13]) | 0.00 → 0.00 | 0.90 → 0.97 | 15 / 0 / 5 of 20 |
| deepseek-v4-flash | N (v3) | 0.95 → 0.97 (+0.02 [+0.01, +0.05]) | 0.00 → 0.00 | 0.94 → 0.97 | 4 / 0 / 5 of 9 |

**The readings fixed in advance** ([PREREG_REPAIR.md](../PREREG_REPAIR.md) §3), applied to these numbers: repair is "useful" if the lower end of the gain interval is above 0.05, and "harmful" if the accepted-but-wrong rate rises with an interval that excludes 0.

| Model, prompt | Lower end of the gain | Useful by the fixed reading | Rise interval excludes 0 | Harmful by the fixed reading |
|---|---|---|---|---|
| gemma +schema, F | 0.467 | yes | yes | yes |
| gemma +schema, N | 0.023 | no | yes | yes |
| deepseek-v4-flash, F | 0.045 | no | no (rise 0) | no |
| deepseek-v4-flash, N | 0.006 | no | no (rise 0) | no |

Lower ends from [results/aggregate/repair/repair_summary.json](../results/aggregate/repair/repair_summary.json) (`gain_state_exact`). This table applies the registered reading mechanically; the report states the same numbers as "One repair call recovers most rejected extractions and adds some silent errors" ([paper/report.md](../paper/report.md) §4.4) and does not use the two labels.

The message-text reading rule of Study 3 matters for these numbers. Under the function-call-only reading, the share of gemma's first answers accepted with prompt N would be 29 of 174 instead of 143 (repair_report.md, "Counts"). The rule is described in [protocol_amendments.md](protocol_amendments.md).

### 10.5 What the failures show

Three patterns, each with its source:

- **Layout, not content, on the registered prompt.** "Inspection: the models extracted the correct content (variables and kinds, rules, known values) in other JSON layouts" ([PREREG_EOP.md](../PREREG_EOP.md), Amendment 1).
- **Formalising reworded rules.** Under rewording, most rejections are formula errors in the rule strings (Section 10.3). The parser cannot read three of the four wordings at all.
- **Silent errors.** Well-formed wrong states occur for gemma on prose (24 of 137) and rise with repair (Section 10.4). A wrong state gives a confident wrong plan or stop. "A wrong but well-formed state yields a confident wrong plan, so symbolic correctness is not the same as reliability in use" ([paper/report.md](../paper/report.md) §5).

The report's conclusion: "Planning on a correct formal state is reliable; obtaining that state from language is the open problem" ([paper/report.md](../paper/report.md), Abstract). Limitations of EOP are collected in [limitations.md](limitations.md).
