# Evaluation protocol

This document describes how a model answer becomes a number in the results. It answers: what the three evaluation modes are and which states each one uses; what the model is shown and what it must return; what "all attempted" means; how each measure is defined in the code (sufficient, optimal with ties, correct stopping, deferral, over-intervention, detection, class accuracy); how intervals and p-values are computed; which tests are registered and how they are corrected for multiplicity; what rules the model runner follows (caching, attempts, rate limits, spend ledger, smoke gate); which model settings were used and how the served model is recorded; what "registered" and "frozen" mean in this repository; and how the evidence tiers are kept apart. Definitions are quoted from the code and the registrations, with the path next to each. The formal task is defined in [formal_problem.md](formal_problem.md), the benchmark in [benchmark_design.md](benchmark_design.md), and the oracle that scores every plan in [oracle_validation.md](oracle_validation.md). The mitigation and its comparison conditions are in [eop_architecture.md](eop_architecture.md). Every change to this protocol is listed in [protocol_amendments.md](protocol_amendments.md).

## 1. The three modes

The modes separate noticing a gap, naming the kind of gap, and planning for it. The prompt text is in [src/msep/models/prompts.py](../src/msep/models/prompts.py).

| Mode | Text added after the state | Eligible states | Source |
|---|---|---|---|
| End-to-End | nothing | all | `build_prompt`, `eligible` |
| Detection-Controlled (primary) | "The current state is not yet sufficient to justify a reliable decision." | all except ALREADY_SUFFICIENT | same |
| Diagnosis-Controlled | the same sentence, then the resource class, e.g. "Resolving this state requires both additional information and additional computation." | INFORMATION_ONLY, COMPUTATION_ONLY, BOTH | `CLASS_SENTENCE` |

"Mode B excludes ALREADY_SUFFICIENT instances (the statement would be false). Mode C also excludes NEITHER (no plan to construct) and AMBIGUOUS" (module docstring of `prompts.py`). AMBIGUOUS states are not in the benchmark ([formal_problem.md](formal_problem.md) §7).

Two rules govern how mode results are read ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §5):

- "Each result names its mode. End-to-End errors are never reported as planning failures."
- "**Mode decomposition** (same instance across modes) attributes each failure to detection, diagnosis or planning." In the code, an item fails "in all modes" only if End-to-End, Detection-Controlled and Diagnosis-Controlled all fail; an item that is unparsed in any mode is excluded from the decomposition, because "attributing it would turn a format failure into a 'diagnosis' or 'detection' failure" (`mode_decomposition` in [src/msep/eval/experiments.py](../src/msep/eval/experiments.py)).

**Which modes each study used.**

| Study | Modes | Source |
|---|---|---|
| Held-out native run (E1–E9) | all three | [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §3 |
| EOP, structured prompt, verifier, parser (v3 items) | End-to-End and Detection-Controlled. The EOP plan is "mode-independent and scored on each mode's eligible items" | [PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md), "Item sets" |
| Counterfactual pairs (T1, T1B, T1 test) | End-to-End only, because "the Detection- and Diagnosis-Controlled prompts are ineligible for ALREADY_SUFFICIENT states by definition" | [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md) |
| Rewording study | End-to-End | [PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md) §2 |
| Study 1 (wording clarity) | End-to-End | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1 |
| Study 2 (cost sensitivity, E10) | Detection-Controlled | PREREG_FOLLOWUP §2 |
| Study 3 (extraction repair) | extraction calls only; no answer prompt | [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §2 |

The headline optimal-plan rates are Detection-Controlled. Detection and the stopping measures on already-sufficient states are End-to-End, because the controlled prompts never show such states.

## 2. What the model is shown and what it must return

### 2.1 The plan prompt

A plan prompt is the rendered state (described in [benchmark_design.md](benchmark_design.md) §5), the mode sentence or sentences, and these output instructions, quoted in full from `OUTPUT_INSTRUCTIONS` in [src/msep/models/prompts.py](../src/msep/models/prompts.py):

```text
Answer with one JSON object and nothing else:
{
  "state_sufficient": true or false,
  "resource_class": "ALREADY_SUFFICIENT" | "INFORMATION_ONLY" | "COMPUTATION_ONLY" | "BOTH" | "NEITHER",
  "plan": [{"type": "ASK" or "COMPUTE", "action": "<action name exactly as listed>"}],
  "stop_after_plan": true or false,
  "decision": "true" | "false" | "defer",
  "confidence": number between 0 and 1,
  "short_justification": "<one or two sentences>"
}
"plan" is the cheapest set of actions that would make the decision justified whatever their results are.
Use an empty plan if the decision is already justified, or if no available plan can justify it.
"decision" is your answer about Q now if the decision is already justified, otherwise "defer".
```

Prompt version: `msep-prompts-v2-certified-compute` (`PROMPT_VERSION`). It is recorded in every raw response.

### 2.2 Other prompts

| Pool | Used for | What it asks | Source |
|---|---|---|---|
| `judgment` | E5 (H3) | "if exactly these actions are run (their results are not known in advance), will a decision about Q be justified whatever their results turn out to be?" Answer: `plan_sufficient`, `confidence`, `short_justification` | `build_judgment_prompt` |
| `decision` | E1 | "The current state already justifies a decision about Q. No action is needed. Question: is Q true or false?" | `build_decision_prompt` |
| `capability` | E14 (not run) | the certified task alone, "Work it out yourself; no tools are available." | `build_capability_prompt` |
| structured prompt (condition B) | EOP comparison | the plan prompt plus five steps of obligation reasoning; "the JSON object must come last" | [src/msep/models/prompts_s1.py](../src/msep/models/prompts_s1.py); quoted in [eop_architecture.md](eop_architecture.md) §7 |
| extraction | EOP and Study 3 | the state text plus an extraction instruction | [eop_architecture.md](eop_architecture.md) §7 |

E5 candidates are the first optimal plan and, for each state, either the decoy action alone (trap siblings) or the optimal plan with one action removed; their labels "are recomputed exactly at analysis time" (`judgment_candidates` in [src/msep/eval/pilot.py](../src/msep/eval/pilot.py)).

### 2.3 How an answer is read

The parser `parse_response` in [src/msep/models/schemas.py](../src/msep/models/schemas.py) takes the text from the first `{` to the last `}` and requires:

- `state_sufficient` is a boolean;
- `resource_class` is one of the five classes;
- `plan` is a list of objects, each with a string `action`;
- `decision` is `true`, `false` or `defer` (a missing `decision` is read as `defer`);
- `confidence`, if present, is a number in [0, 1].

A missing `stop_after_plan` is read as true. Anything else raises a parse error, and the answer counts as unreadable. "Fields are scored, not prose" (module docstring).

The JSON schemas are versioned: `SCHEMA_VERSION = "msep-schemas-v2"`; "Changing any schema requires bumping SCHEMA_VERSION; tests/test_inference_readiness.py holds a snapshot of every schema" (same file).

**Schema enforcement.** For three models the schema is not enforced; the prompt asks for JSON and the parser reads it from the text. The provider's SDK has "NO JSON-schema parameter" ([src/msep/models/providers/adaption_provider.py](../src/msep/models/providers/adaption_provider.py)). For gemma-4-26b +schema, "the job's JSON schema is sent as the parameters of one function tool (strict), the call is forced, and the function call's `arguments` string is parsed instead of the message text" (same file). If no function call is made, the answer has no text. The same file states: "Whether the backend actually constrains decoding to the schema is not documented; measure it, do not assume it." Under the structured prompt it did not hold; see Amendment 2 in [protocol_amendments.md](protocol_amendments.md).

## 3. The all-attempted basis

"**Primary basis: all attempted.** A failed call, truncated or unparsed answer, invalid extraction or planner error counts as incorrect. Parsed-only figures are reported separately. Failure counts by type are reported for every condition" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §4). The same rule is in [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §7 ("Unparseable, refused, truncated or failed responses count as incorrect and are reported separately") and in every later registration.

In the code, an unparsed plan answer is scored with `detection_correct`, `class_correct`, `plan_sufficient`, `plan_optimal` and `plan_exact_match` all false (`score_plan_results` in [src/msep/eval/pilot.py](../src/msep/eval/pilot.py)). In the EOP analysis, an eligible item with no response at all is added as a failure (`score` in [experiments/run_eop.py](../experiments/run_eop.py)).

Two recorded exceptions on the development split: one gemma-4-26b +schema Diagnosis-Controlled response is missing and is dropped from the denominator (400, not 401), and one gemma native response on the T1B items is missing and is counted as a failure in the EOP analysis ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §5). On the held-out split, seven gemma calls failed all three attempts and count as wrong ([paper/report.md](../paper/report.md), Appendix B).

## 4. Scoring definitions

Every plan is checked against the exact oracle: "Every plan is re-checked with the oracle (`is_sufficient`), so scores do not depend on matching the oracle's plan text" ([src/msep/eval/plan_metrics.py](../src/msep/eval/plan_metrics.py)). Action names in the answer are mapped back to the formal actions through the state's rendering alias. Names that are not on the menu are dropped before the check and recorded in `unknown_actions`; `plan_valid` is then false (`score` in `plan_metrics.py`).

### 4.1 Plan measures

| Measure | Definition in the code | Source |
|---|---|---|
| Sufficient | `is_sufficient(state, plan)`: the plan settles Q in every outcome (definition in [formal_problem.md](formal_problem.md) §6) | `plan_metrics.score` |
| Inclusion-minimal | the plan is one of the oracle's `minimal_sufficient_plans` | same |
| Optimal | `sufficient and best is not None and cost == best`: sufficient at the oracle's minimum cost | same |
| Exact match | the plan is one of the oracle's `optimal_plans` | same |
| Excess cost | cost minus optimal cost, for sufficient plans | same |
| Regret | "L = 1 + total cost of all available actions (penalty for an unjustified outcome); resolvable instance: V(plan) = -cost(plan) - L * [plan insufficient]; NEITHER instance: V(plan) = -cost(plan) - L * [response commits to an answer]; regret = V(oracle plan) - V(model plan) (always >= 0)" | module docstring of `plan_metrics.py` |
| Unnecessary-action rate | sufficient plans that are not inclusion-minimal | `summarize` in [experiments/run_eop.py](../experiments/run_eop.py) |

**Ties.** "Any sufficient plan at optimal cost counts as optimal" ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §7). Because optimality is defined by cost and sufficiency, not by matching a stored plan, every tied cheapest plan is accepted. Tests: "Every equally optimal plan is accepted by every metric (not only a canonical one)" ([tests/test_scoring_ties.py](../tests/test_scoring_ties.py), [tests/test_multiple_optima.py](../tests/test_multiple_optima.py)). Precision and recall of actions are measured "against the CLOSEST optimal plan (best F1)", because "comparing against their union would penalise an agent that chose any one of them" (`action_overlap` in [src/msep/eval/experiments.py](../src/msep/eval/experiments.py)). In Study 2, on the item at the tie price, "plans with and without d tie; all tied plans count as correct" ([PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §2).

The headline rate is the optimal-plan rate on resolvable states (INFORMATION_ONLY, COMPUTATION_ONLY, BOTH), Detection-Controlled, all attempted ([results/aggregate/final_test/RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md)).

### 4.2 Detection and diagnosis

| Measure | Definition | Source |
|---|---|---|
| Detection | `state_sufficient` equals the oracle's `current_sufficient`. Measured End-to-End; reported as accuracy, sensitivity on insufficient states and specificity on sufficient ones | `plan_metrics.score`; `analyze_e2` in `experiments.py` |
| Class accuracy | `resource_class` equals the oracle's class | `plan_metrics.score` |
| Macro-F1, balanced accuracy, confusion matrix | over the four labels INFORMATION_ONLY, COMPUTATION_ONLY, BOTH, NEITHER (ALREADY_SUFFICIENT appears only as a predicted column) | `analyze_e3` in [src/msep/eval/pilot.py](../src/msep/eval/pilot.py); [src/msep/eval/bootstrap.py](../src/msep/eval/bootstrap.py) |
| Answered prematurely | a decision other than `defer` on a state that is not yet sufficient | `plan_metrics.score` |

### 4.3 Stopping, deferral and over-intervention

Several stopping measures exist. They are close but not identical, and each table names the one it uses.

| Measure | Definition in the code | Where it is reported | Source |
|---|---|---|---|
| Correct stopping (EOP comparison, rewording study) | ALREADY_SUFFICIENT: readable answer, empty plan, and the decision equals the true value. NEITHER: readable answer and decision `defer` | "stop A → EOP" columns; `stop_ok_AS_NEITHER` | `_ok_stop` in [experiments/run_eop.py](../experiments/run_eop.py) |
| Correct stopping (Study 1) | "empty plan and the right answer; on NEITHER: empty plan, 'defer', class NEITHER" | [results/aggregate/followup/followup_report.md](../results/aggregate/followup/followup_report.md) | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1 |
| Deferral on NEITHER (E8 `correct_defer`) | readable answer, empty plan, decision `defer` and predicted class NEITHER | "Defers when nothing helps", "Defers on NEITHER (DC)" | `analyze_e8` in [src/msep/eval/experiments.py](../src/msep/eval/experiments.py) |
| Inappropriate persistence | a non-empty plan on a NEITHER state | E8 | same |
| Acts when sufficient from the start | on native ALREADY_SUFFICIENT states, End-to-End: a plan with positive cost; an unreadable answer counts as acting | "Acts when sufficient (E2E)" | `analyze_e1`, `proposes_any_action`, in [src/msep/eval/pilot.py](../src/msep/eval/pilot.py) |
| Over-intervention O1 | on states that one edit made ALREADY_SUFFICIENT: "the plan is non-empty"; "unparsed counts as failure on the all-attempted basis" | "Acts on newly sufficient states"; test T-OI-1 | [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md); `outcomes` in [experiments/analyze_t1b.py](../experiments/analyze_t1b.py) |
| Acts (Study 1) | proposes any action on an ALREADY_SUFFICIENT state | primary measure of Study 1 | PREREG_FOLLOWUP §1 |
| Re-certification (Study 1, exploratory on held-out) | "the plan includes a computation whose results are all listed as known" | followup_report.md; [results/aggregate/final_test/recertification/recertification.json](../results/aggregate/final_test/recertification/recertification.json) | same |
| Premature stop (E9) | the answer says to stop after its plan, the plan does not settle Q in the actual world at any prefix, and the answer is not an abstention (empty plan, class NEITHER, `defer`) | E9 | `stopping_measures` in `experiments.py` |
| Premature stopping (Study 1 harm check) | on COMPUTATION_ONLY and BOTH controls: "says the state is sufficient, or gives an empty plan" | Table C1 of the report | PREREG_FOLLOWUP §1 |

Continuing a static plan after a prefix already settles Q in the actual world "is not an error for a static plan, which is chosen before outcomes are seen" ([ASSUMPTIONS.md](../research/working_documents/ASSUMPTIONS.md) F9; note in `analyze_e9`).

### 4.4 Pair, sweep and extraction measures

| Measure | Definition | Source |
|---|---|---|
| T1 pair joint accuracy | "A model is correct on a pair only if it is correct on both states" | [paper/extended_report.md](../paper/extended_report.md) §3.4; [benchmark_design.md](benchmark_design.md) §9 |
| Study 2, primary | "Within each sweep, optimal-plan rate on the above item (b + 1) minus the rate on the below item (b − 1)" | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §2 |
| Study 2, below items | "cheapest plan; kept a plan that was cheapest before the price change; another sufficient plan that is not the cheapest; insufficient plan; no usable answer" | same |
| Extraction correctness (exact state) | "same variables with the same kinds, same known values, same actions (name, kind, cost, revealed variables) and logically equivalent rule sets (the conjunction of the rules has the same truth table)" | [src/msep/eval/extraction_match.py](../src/msep/eval/extraction_match.py) |
| Accepted but wrong (Study 3) | "the reader accepts the extraction and it is not the true state. This is the error a system cannot see" | [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §3 |
| Rejected (Study 3) | "the pipeline knows it has no state" | same |

## 5. Statistics

### 5.1 Family-clustered bootstrap intervals

"Clusters are benchmark families: siblings are not independent, so resampling is over families, never over rows" ([src/msep/eval/bootstrap.py](../src/msep/eval/bootstrap.py)).

| Element | Implementation (`cluster_mean_ci`, `paired_diff_ci`) |
|---|---|
| Point estimate | mean over items (ratio of sums over families, so every item has equal weight) |
| Resampling | families drawn with replacement, as many as there are families |
| Replicates and seed | 2,000 resamples, seed 0 (defaults) |
| Interval | 2.5th and 97.5th percentiles of the resampled means, with linear interpolation |
| Paired differences | the same procedure on the per-item difference a − b |
| Fewer than two families | no interval |

Classification statistics (macro-F1, balanced accuracy) use the same family resampling with 1,000 replicates (`cluster_stat_ci`).

### 5.2 One-sided bootstrap p-values

Every registered one-sided test uses the same form. `one_sided_p` in [experiments/run_eop.py](../experiments/run_eop.py): the per-item differences are grouped by family; families are resampled with replacement 10,000 times with seed 0; p is the share of resamples whose mean difference is ≤ 0. "One-sided family-clustered bootstrap p (share of 10,000 resamples with difference ≤ 0, seed 0)" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §5, F1).

| Test | Statistic resampled | p is the share of resamples with | Source |
|---|---|---|---|
| EOP − native (dev C − A; held-out F1; rewording pooled) | mean paired difference in plan optimality | difference ≤ 0 | [PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md); PREREG_FINAL §5; [PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md) §3 |
| T-OI-1 | O1 rate on newly sufficient states | O1 ≤ 0.05 | [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md); `boot` in [experiments/analyze_t1b.py](../experiments/analyze_t1b.py) |
| T-OI-2 | O1 newly sufficient − O1 natively sufficient | difference ≤ 0 | same |
| Study 1 primary | reduction in acting under the clarified wording | no reduction | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1 |
| Study 2 primary | optimal above − optimal below | "above is higher" fails | PREREG_FOLLOWUP §2 |

The smallest non-zero p is 1/10,000. "A Holm p of 0.0 in a file means no bootstrap resample fell at or below the threshold" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §3). The report prints such values as "< 0.001".

### 5.3 McNemar and Holm

**Exact McNemar** (`mcnemar_exact` in [src/msep/eval/bootstrap.py](../src/msep/eval/bootstrap.py)): with b and c the two discordant counts and n = b + c, the two-sided p is min(1, 2 · Σ_{i ≤ min(b, c)} C(n, i) / 2ⁿ); p = 1 when n = 0.

**Holm** (`holm` in the same file): the Holm step-down adjustment over the p-values of one test family.

**Registered test families and their corrections.**

| Family | Tests | Correction | Supported if | Source |
|---|---|---|---|---|
| F0 (held-out) | H2, H3, H4a, H4b; exact two-sided McNemar, Detection-Controlled, per model | Holm across the four tests, within each model | "Holm p < 0.05 and difference > 0" | [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §8; [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §5; `confirmatory` in [src/msep/eval/experiments.py](../src/msep/eval/experiments.py) |
| F1 (held-out) | EOP − native, plan optimality, Detection-Controlled, resolvable states | Holm across the four models | Holm p < 0.05 | PREREG_FINAL §5 |
| F2 (held-out) | T-OI-1 on the newly sufficient test states, End-to-End, native | Holm across the four models | Holm p < 0.05 | PREREG_FINAL §5; PREREG_T1B |
| Dev EOP | C − A, plan optimality, Detection-Controlled | Holm across the four models | Holm p < 0.05 | [PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md), "Comparisons" |
| T1B (dev) | T-OI-1, T-OI-2 | Holm across the four models, within each test | Holm p < 0.05 | PREREG_T1B |
| Rewording | EOP − native, pooled over four wordings | Holm across the four models, α = 0.05 | Holm p < 0.05 | [PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md) §3 |
| Study 1 | reduction in acting | Holm across three models | Holm p < 0.05 | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1 |
| Study 2 | above − below | Holm across three models | Holm p < 0.05 | PREREG_FOLLOWUP §2 |
| Study 3 | none: "There is no significance test" | none | fixed readings on intervals (Section 5.4) | [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §3 |

"Holm correction within each family, α = 0.05; no correction across families (stated here so it can be judged)" (PREREG_FINAL §5). The report's methods section says "Registered tests are Holm-adjusted across models" ([paper/report.md](../paper/report.md) §3.3). That describes F1, F2 and the later studies; for F0 the registered correction is across the four hypotheses within each model, and that is what the code computes.

**Pre-registered secondary and descriptive analyses.** "Everything else is descriptive, including H1 and H5 and the mode decomposition. Null and inconclusive results are reported as such" (PREREG_FINAL §5). On the development split, all H2–H4 values are exploratory: "By §8 all dev values are exploratory" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §4.4).

### 5.4 Readings fixed in advance without a test

Some registrations fix a reading of an interval instead of a test:

- Study 1: "*The error persists without the ambiguity* if the lower end of the 95% interval of the W1 rate is above 0.05" ([PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §1).
- Study 1 harm check: "W1 must not raise it; a rise whose interval excludes 0 is reported as harm" (same).
- Study 3: "repair is *useful* for a model and prompt if the lower end of the 95% interval of the gain in exact state is above 0.05. It is *harmful* if the accepted-but-wrong rate rises with repair and the interval of that rise excludes 0" ([PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) §3).

## 6. Runner rules

All model calls go through one runner, [src/msep/models/runner.py](../src/msep/models/runner.py), and one spend ledger, [src/msep/models/spend.py](../src/msep/models/spend.py). The rules below apply to every run, including the follow-up studies ("through the same runner as all other runs: jobs cached by id, at most 3 attempts per job, rate-limit waits are not attempts, same spend ledger", [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) §3).

| Rule | What the code does | Source |
|---|---|---|
| Job identity | "Its id is a hash of (model key, pool, instance, mode, candidate, prompt text), so a changed prompt is a new job and old raw files are never overwritten." The id is the first 24 hex characters of a SHA-256 | `Job.job_id`; module docstring of `runner.py` |
| Cache | A job whose saved record has any status other than `error` is done and "is never requested again" | `_done`; [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §6 |
| Attempts | `MAX_ERROR_ATTEMPTS = 3`. A call that ends in an error is saved as `<job_id>.attemptK.json`, and the job stays open; a job that has failed three times is not retried | `run_jobs`, `_attempts` |
| What counts as an attempt | Only an error status from the provider or the transport. A truncated answer or a refusal is a final response, not an error, so it is not retried; it is parsed if possible and otherwise counts as wrong | `_done`; `AdaptionProvider.complete` |
| Retries inside one attempt | "SDK retries 5xx and connection errors (max_retries, 2 here); the runner adds its own per-job cap (MAX_ERROR_ATTEMPTS)" | [src/msep/models/providers/adaption_provider.py](../src/msep/models/providers/adaption_provider.py) |
| Rate limits | A 429 answer is waited out and retried, up to 10 times, 60 s plus a random 0–15 s each time: "the server asks to retry after 60 s; not counted as a failed attempt". The recorded latency excludes the waits | `RATE_LIMIT_RETRIES`, `RATE_LIMIT_WAIT_S` in `runner.py` |
| Settings guard | If saved results for a model key were made with different settings (`max_tokens`, `temperature`, `effort`, `reasoning_effort`, `stream`, `structured`), the run stops: new settings need "their own model key" | `_settings_mismatch` |
| Call cap | A run refuses to start if more calls are needed than `--max-calls` | `run_jobs` |
| Spend ledger | "The ledger (spend_ledger.jsonl) is append-only and shared across models and runs. Before every call the runner reserves the worst case for that call (estimated input + max output tokens); a call whose worst case would take the cumulative total over the budget is not made." The worst case uses input ≈ characters / 3 tokens and the full output cap. After the call the actual cost is settled | `spend.py`; `worst_case_cost` |
| Budget | "Default $0. No real call is possible until `--budget-usd` is given explicitly. The ledger is a hard stop across runs" ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §3). For the provider's models the budget "is read in the model's currency: for these models, credits". Held-out and later runs: "Spend cap: cumulative ledger 519.4324 credits" | PROTOCOL §3; `_note_adaption` in [configs/models.json](../configs/models.json); [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §6 |
| Smoke gate | Before a batch, one plan job per model runs "through the same accounted path"; unless it returns status `ok` with a parsed answer, the run stops "before any further calls" | `main` in [experiments/run_pilot.py](../experiments/run_pilot.py) |
| Smoke gate (EOP driver) | One job per model, item set and condition; if it errors, that combination is skipped | `main` in [experiments/run_eop.py](../experiments/run_eop.py) |
| Configuration check | "Model configuration checks before any real run. No network, no API call. Errors block a run" | [src/msep/models/config_check.py](../src/msep/models/config_check.py) |
| Test split | "The test split is refused unless --allow-test is given (frozen final evaluation only)" | `run_pilot.py`; `run_eop.py` |
| Raw records | `results/raw/<pool>/<model_key>/<job_id>.json`, "each holding the request (no credentials), the full raw provider response, status, usage, timing and the parsed output" | module docstring of `runner.py` |
| Run log | `run_log.jsonl` with one event per job and per batch | `run_jobs` |

The smoke gate exists in the drivers of the native runs and of the EOP comparison. The drivers of the rewording study and of Studies 1–3 (`run_robust.py`, `run_followup.py`, `run_repair.py`) contain no smoke step; they use the same runner, cache, attempt cap and ledger.

**Passes.** Each held-out chain runs the steps "in priority order (v3 native; EOP on v3; T1 native; EOP extraction on T1; structured prompt on T1), then one fill pass" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §6; [experiments/chain_final.sh](../experiments/chain_final.sh)). "If time runs out before every step finishes, steps are dropped from the end of the priority order for all models alike, and the report says which steps did not run. No step is dropped because of its results" (same). No step was dropped ([paper/extended_report.md](../paper/extended_report.md), Appendix C). The follow-up chains run two passes, "one fill pass if needed" ([experiments/chain_followup.sh](../experiments/chain_followup.sh)); the Study 3 chain runs first answers in two passes, then repair calls in two passes ([experiments/chain_repair.sh](../experiments/chain_repair.sh)). The network guard that paused runs while the provider was unreachable, and every restart of a chain, are listed in [protocol_amendments.md](protocol_amendments.md).

Commands to rebuild data and re-run analyses: [experiments/reproduction.md](../experiments/reproduction.md) and [docs/RUNNING.md](../docs/RUNNING.md).

## 7. Models, settings and the served model

Four open-weight models were evaluated, all hosted by one provider ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md), amendment of 2026-11-14). The settings are in [configs/models.json](../configs/models.json) and are pinned in every protocol freeze record. The configuration holds no credentials: the key is read from the environment (`AdaptionProvider`).

| Model key | Model id | temperature | max_tokens | stream | max_retries | structured | Price, credits per 1M tokens (input / output) |
|---|---|---|---|---|---|---|---|
| `adaption-qwen3.5-397b` | qwen3.5-397b | 0.0 | 16000 | true | 2 | – | 0.55 / 3.5 |
| `adaption-qwen3.8-27b` | qwen3.8-27b | 0.0 | 16000 | true | 2 | – | 0.039 / 1.25 |
| `adaption-deepseek-v4-flash` | deepseek-v4-flash | 0.0 | 16000 | true | 2 | – | 0.04444 / 0.13332 |
| `adaption-gemma-4-26b-a4b-it-schema` | gemma-4-26b-a4b-it | 0.0 | 16000 | true | 2 | `function_tool` | 0.0765 / 0.255 |

Reasons recorded in the configuration note (`_note_adaption`): "max_tokens 16000 because these models reason before answering and the API has no reasoning control"; "streaming on because a non-streamed glm-5.2 call returned 504 after 375 s"; "temperature 0.0 for determinism where the backend honours it". Prices were "copied from the Adaption 'Models' docs page pasted by the user; the docs host was unreachable from the build environment". The configuration marks the connector as not verified against documentation ("written from SDK 0.19.0 source and the pasted docs page; run --smoke first"); the smoke gate was the check.

The +schema key is "a separate condition, not comparable to plain gemma" ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §1). The calibration also ran plain gemma-4-26b-a4b-it and glm-5.3-flash; the proprietary models named in PROTOCOL.md §3 were not run (same section). One answer per item; no sampling repetitions.

**Recording of the served model.** The provider's response names the model that served it. The runner stores it as `served_model` in every raw record, together with the settings, the prompt hash and the prompt version (`run_jobs` in [src/msep/models/runner.py](../src/msep/models/runner.py)). Summaries count the identifiers per pool (`usage_summary` in [src/msep/eval/pilot.py](../src/msep/eval/pilot.py)). qwen3.5-397b was served as `qwen3.5-397b-a17b-nvfp4` (EXPERIMENT_INDEX §1). "In the held-out native run each model key was served by a single model identifier throughout" ([paper/extended_report.md](../paper/extended_report.md), Appendix C). The registrations require that "a provider-side change is reported" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §2).

## 8. What "registered" and "frozen" mean here

**Registered.** A protocol document (`PROTOCOL.md` or a `PREREG_*.md` file) that states the items, conditions, outcomes, tests and readings, committed to this repository before any model response for the data it covers exists. The registrations are files in the repository; their time is the git commit time. "The commit times are the authoritative ones" ([paper/extended_report.md](../paper/extended_report.md), Appendix C). The repository records no registration with an outside registry.

**Frozen.** A freeze record `data/FREEZE_<NAME>.json` pins, by SHA-256, the registration, the analysis and driver code, the prompt and scoring code, the data the analysis reads, and the model settings. [experiments/freeze_protocol.py](../experiments/freeze_protocol.py) writes it ("refusing to overwrite" an existing record) and verifies it: `--verify` recomputes every hash and the model settings and prints `FREEZE OK` or the files that differ. The record also stores the commit at freeze time (`commit_at_freeze`). The benchmark and the T1 pairs have their own freeze scripts (`experiments/freeze_benchmark.py`, `experiments/freeze_t1.py`). The rule after freezing: "No change to prompts, extraction schema, planner or scoring after seeing B/C/D results on these sets" ([PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md), "Discipline"); "No prompt, extractor, planner, scoring rule or model setting changes after the first test response" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §1).

| Registration | Committed (UTC) | Freeze record | Verification status recorded |
|---|---|---|---|
| [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) v0.2 | 2026-11-04 (models amendment 2026-11-14 00:08) | none of its own; pinned unchanged in FREEZE_FINAL | header still reads "Not frozen" ([protocol_amendments.md](protocol_amendments.md)) |
| [PREREG_T1.md](../experiments/preregistrations/PREREG_T1.md) | 2026-11-13 21:22 | [data/FREEZE_T1.json](../data/FREEZE_T1.json) | OK on 2026-11-14 |
| [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md) | 2026-11-13 23:53 | [data/FREEZE_T1B.json](../data/FREEZE_T1B.json) | OK on 2026-11-14 |
| [PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md) | 2026-11-13 23:58; Amendment 1 2026-11-14 11:36; Amendment 2 13:32 | [FREEZE_EOP](../data/FREEZE_EOP.json), [FREEZE_EOP_A1](../data/FREEZE_EOP_A1.json), [FREEZE_EOP_A2](../data/FREEZE_EOP_A2.json) | fail by design: later amendments changed files they pin |
| [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) | 2026-11-14 20:04 | [data/FREEZE_FINAL.json](../data/FREEZE_FINAL.json) | OK on 2026-11-14 |
| [PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md) | 2026-11-14 20:20 | [data/FREEZE_ROBUST.json](../data/FREEZE_ROBUST.json) | OK on 2026-11-14 |
| [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) | 2026-11-15 21:03 | [data/FREEZE_FOLLOWUP.json](../data/FREEZE_FOLLOWUP.json) | Not recorded |
| [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) | 2026-11-16 00:13 | [data/FREEZE_REPAIR.json](../data/FREEZE_REPAIR.json) | Not recorded |

Sources: commit times from [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §6 and the commit history; status from EXPERIMENT_INDEX §6 ("re-checked 2026-11-14"). The dataset freezes are listed in [benchmark_design.md](benchmark_design.md) §13.

## 9. Evidence tiers

Results differ in standing, and the tiers are never mixed in one table or claim. The report names them in Section 3.5 ([paper/report.md](../paper/report.md)): "**Registered, held-out:** the planning hypotheses (H2–H4) and the test of over-intervention on newly sufficient states. **Prospective test of an amended method:** EOP on held-out data. … **Rewording study:** registered separately and never used to change EOP. **Follow-up studies:** three studies registered *after* the held-out results had been viewed … they are new evidence, not part of the original confirmation."

The full list used across the public documents:

| Tier | What belongs to it | Where it was fixed | How to read it |
|---|---|---|---|
| Registered held-out | F0 (H2, H3, H4a, H4b) and F2 (T-OI-1) on the test split | [PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md) §8; [PREREG_T1B.md](../experiments/preregistrations/PREREG_T1B.md); [PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §5 | Confirmatory |
| Registered development | T1 decision rules; T-OI-1 and T-OI-2 on dev; registered EOP condition C against native | [PREREG_T1.md](../experiments/preregistrations/PREREG_T1.md), PREREG_T1B, [PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md) | Confirmatory for the dev split |
| Prospective test of an amended method | F1: EOP in its frozen configuration against native on the test split | PREREG_FINAL §3, §5 | Evidence for the amended method; "they do not turn the original registered experiment into a success" (PREREG_FINAL §1) |
| Development-informed conditions | C′ and D′ on dev (Amendment 1); Bt and Dt (Amendment 2, analysis only) | PREREG_EOP Amendments 1 and 2 | "Not the registered treatment. Reported next to it, never in its place" ([paper/extended_report.md](../paper/extended_report.md), Appendix C) |
| Rewording study (registered separately) | One test: EOP − native pooled over four wordings; EOP-N is a registered secondary condition; the rest descriptive | [PREREG_ROBUST.md](../experiments/preregistrations/PREREG_ROBUST.md) | Frozen separately; "never used to change EOP or to re-run the test split" |
| Follow-up studies, registered after the held-out results were viewed | Study 1 (wording clarity), Study 2 (cost sensitivity, E10), Study 3 (extraction repair, exploratory, no test) | [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md), [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) | New evidence on train families; their questions were chosen with knowledge of the held-out results |
| Exploratory and descriptive | H1, H5, the mode decomposition, all dev values of H2–H4, the re-certification split of over-intervention, the worked examples | PREREG_FINAL §5 | No test; generates hypotheses |
| No-model baselines | The oracle (1.0 by definition), the parser P with the same planner, text-only heuristics, fixed policies | PREREG_FINAL §3; [benchmark_design.md](benchmark_design.md) §8 | References, not evidence about models |

Other documents number the tiers differently. [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §1 uses five numbered tiers written on 2026-11-14, before the held-out results and the follow-up studies existed, and puts T1B and the rewording study together as "Prospectively registered follow-up". [paper/extended_report.md](../paper/extended_report.md) Appendix C uses seven numbered tiers that predate the follow-up studies. The content is the same as in the table above; the follow-up tier was added later.
