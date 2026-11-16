# Research readiness (2026-11-04)

**Verdict: ready for a small, budget-capped calibration pilot on dev, once access and four decisions are in place (§6). Not ready for any claim about language models.** No model has been called.

## 1. Scientifically validated (offline, with evidence)

| Item | Evidence |
|---|---|
| The oracle is exact | E0: 228,199 checks, 0 failures. Three independent exact paths. Mutation tests catch planted bugs. An auditor's independent solver agreed on 671/671 v2 dev items |
| Labels of the frozen benchmark are correct | All 2,282 v3 labels re-verified by brute force; a 534-variant sample too |
| The prompt carries exactly the oracle's information | Text → state round-trip, 0 mismatches on every v3 instance |
| The benchmark is frozen and reproducible | `data/FREEZE_v3.json`; regeneration is byte-identical; a test fails on any untracked change |
| Known shortcuts are closed on v3 | Count probe at chance; no value, position or cost leaks; mental-computation attacks at chance (`results/audit_v3`) |
| Shallow-heuristic ceiling is measured | h1pp on dev, Detection-Controlled: 78% class accuracy, 59% optimal plans on resolvable states, 100% on NEITHER (`results/baselines_v3`) |
| Equally optimal plans are all accepted | Tested on every tie found in v3 (`tests/test_multiple_optima.py`); fixed an E4 bug that penalised ties |
| Metrics, statistics and mode attribution do what they claim | 12 synthetic mock agents with signature tests, including mode-dependent ones (SYNTHETIC; not findings) |
| The candidate mitigation cannot use hidden information | Imports nothing from the oracle; runs on text + `execute()` only; certified tasks are opaque; its final knowledge equals the text plus the observations it paid for (`tests/test_realistic_planner.py`) |
| Real runs cannot overspend or run unchecked | Budget default $0; ledger hard stop; config check; smoke gate; retry cap; raw logs |

## 2. Assumptions that remain

1. **The certified-computation convention.** A model's own correct computation does not count. E14 is prepared to measure how much this matters; it cannot be removed by design.
2. **The logical decision rule.** Sufficiency means certainty in every outcome. The probabilistic rule is a separate stress test (E11).
3. **Static plans** chosen before any outcome. Conditional plans (Level 4, expected cost) are not built.
4. **Synthetic propositional worlds** rendered in three themes plus one held-out theme. No external data has been processed (E13 is a converter only).
5. **One prompt wording per mode.**
6. **The 1,000-token cap** (if kept) includes internal reasoning.

## 3. Only real models can answer

- Is the benchmark too easy, too hard or well calibrated for frontier models (ceiling/floor)?
- Do models beat the shallow heuristics, especially on `heuristic_hard`?
- H2–H4: diagnosis vs planning, relevance vs sufficiency, BOTH vs single-resource.
- How many failures are detection vs diagnosis vs planning (mode decomposition)?
- Do models skip COMPUTE because they can compute internally (E14)?
- Truncation, refusal and parse-failure rates under the chosen settings.
- Whether an LLM can extract the formal state well enough for the planner to help (mitigation S2).

## 4. What would support or falsify the hypotheses

| Hypothesis | Supported by | Falsified (or not supported) by |
|---|---|---|
| H2 Diagnosis is easier than planning | Class correct > plan sufficient on the same instances, Holm p < 0.05, CI excluding 0 | No significant difference, or plan sufficient ≥ class correct |
| H3 Relevance is confused with sufficiency | Relevant-but-insufficient plans judged sufficient more often than optimal plans are misjudged, significant | Both judged equally well |
| H4 BOTH is hardest | BOTH sibling plan sufficiency below INFORMATION_ONLY and COMPUTATION_ONLY siblings, significant | No gap, or BOTH ≥ single-resource |
| The planning failure is real, not detection | Failures persist in Diagnosis-Controlled (mode decomposition "fail in all modes") | Failures vanish once insufficiency or the class is given |
| The benchmark measures more than shallow reading | Model > h1pp on plan optimality, especially on `heuristic_hard` | Model ≈ h1pp or below; or gains only on `heuristic_easy` |
| COMPUTE results reflect planning | Similar COMPUTE skip rates whether or not the model can compute the task (E14) | Skips concentrated where the model is capable (policy substitution) |
| The mitigation helps (later) | B with the LLM extractor beats native planning and the baselines on regret and sufficiency, with extraction accuracy reported | No gain, or gains only from extraction-free conditions |

A null result is reportable if the benchmark is exact and the modes and heuristics are reported (EXPERIMENT_PLAN §13).

## 5. Claims currently prohibited

- Any statement about how a language model performs, including from the synthetic mock agents or the dry run.
- That the Epistemic Obligation Planner (any condition) helps or works.
- That the oracle planner (A), or condition B with the rule-based parser, is a mitigation result.
- That the benchmark is free of shortcuts. It is free of the ones we found; h1pp still gets about 59% of plans optimal.
- That E8 / NEITHER results show epistemic reasoning: h1pp solves every NEITHER item.
- That `heuristic_hard` results generalise to the full distribution, or comparisons pooled across subsets.
- That results transfer to natural tasks or real agents.
- "First" or "novel" without the final literature sweep (SURE-Act is unverified).
- That GPT-5.6 Sol settings are correct before the smoke test.

## 6. Before the first paid call

1. API keys as environment secrets; api.openai.com allowed.
2. GPT-5.6 Sol prices in `configs/models.json`. `check_config.py` blocks without them.
3. The output-cap and effort decision (RISKS #1). Use `--override` to test it on the smoke test.
4. An explicit budget (`--budget-usd`). The default is $0.
5. Whether to include E14 in calibration (adds one call per certified task per family).
6. `python experiments/freeze_benchmark.py --verify` prints FREEZE OK.

## 7. Methodological case study for the paper

The independent audit is a reportable validation result, not a new general discovery. Our first validated benchmark (v2) measured a surface shortcut: reading only the rule that defines Q solved it 100%. We found this before any model was run and contained it by:
- an adversarial audit;
- template v3 with class-independent sampling;
- leak checks;
- heuristic baselines and a pre-registered stress subset.

Paper §4.4 reports it as such.
