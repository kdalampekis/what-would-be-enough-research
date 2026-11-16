# CHALLENGE_V4_DESIGN.md
# Challenge Tier v4 — design draft (not frozen, not pre-registered yet)

**Status (2026-11-13):** design draft. No v4 data has been generated and no model has seen any v4
item. No paid calls were made for this document. v3 stays frozen and remains the primary benchmark;
every confirmatory claim stays on v3.

**Disclosure (to carry into the paper).** v4 was motivated by (i) the v3 diagnostic ceiling in the
10-family dev calibration (qwen3.5-397b, qwen3.8-27b and deepseek-v4-flash at 0.96–1.00 sufficiency
and optimality; `results/aggregate/diagnostics_2026-11-13/FINDINGS.md`) and (ii) failure modes reported
in the literature (`LITERATURE_FAILURE_MAP.md`). It was designed after seeing which models are at
ceiling, so it is a prospective challenge tier, not a re-test of v3, and its rationale must be fixed
from the generator's formal structure before any inference.

---

## 1. Design rules

1. **Separate version.** New generator code path and data (`pool_v4`, own seeds and splits), frozen and
   hashed in its own manifest before any model call. v3 code paths and hashes are untouched
   (`freeze_benchmark.py --verify` must still pass).
2. **No tuning on model outputs.** Item properties are chosen from formal parameters only. No item is
   kept or dropped because a tested model fails or passes it. Heuristic baselines (h1/h1p/h1++) may be run
   before freezing to check for shortcuts; LLMs may not.
3. **Difficulty from structure, not size.** Do not raise variable counts or distractor density to make
   models fail. Each test varies one formal property while holding the rest fixed.
4. **Controls** reported for every comparison: prompt length (characters and tokens), number of actions,
   number of variables, class balance, oracle complexity (number of minimal sufficient plans, optimal
   cost, size of the target's support), and the h1++ score on the same items.
5. **Static-plan oracle only where it is exact.** Anything that needs contingent policies gets a new
   oracle and is a separate extension, never scored with the static-plan oracle (F2).
6. **Pre-register** hypotheses, primary metrics, models, family counts, analysis and budget before
   generation is frozen; report deviations.

## 2. Evidence from v3 that shapes v4 (diagnostic, 10 dev families, no new calls)

- **Optimality is lost to redundancy, not cost choice.** Sufficient-but-not-optimal plans: gemma +schema
  62 redundant vs 11 minimal-but-dearer; strong models 0–2 per mode. Redundant extras are mostly
  oracle-*irrelevant* (62/107) or *relevant but insufficient* (23/107). → T3.
- **Non-termination on BOTH/NEITHER.** glm-5.3-flash gives no answer at 32k tokens on 11 of 20 NEITHER plan jobs and
  on 22 BOTH jobs, while its completed answers are near perfect. → record non-answer as a
  pre-registered outcome by class in every v4 test.
- **v3 families are counterfactual, but not single-edit.** Siblings share all rules but differ in
  several evidence/computed items and in the action set: of 1,818 dev sibling pairs, only 19
  class-changing pairs differ by ≤2 evidence/computed items with the same actions.
- **On v3, pair correctness adds little beyond item accuracy.** Detection-Controlled, behaviourally
  correct (optimal plan; defer on NEITHER; empty plan on ALREADY_SUFFICIENT), over the 165 sibling pairs
  with different optimal plans:

  | Model | Item correct | Both in pair correct | Independence (item²) | Families all correct |
  |---|---|---|---|---|
  | qwen3.5-397b | 0.969 | 0.945 | 0.939 | 0.90 |
  | qwen3.8-27b | 0.922 | 0.836 | 0.850 | 0.50 |
  | deepseek-v4-flash | 0.984 | 0.970 | 0.968 | 0.90 |
  | gemma-4-26b +schema | 0.438 | 0.182 | 0.192 | 0.00 |
  | glm-5.3-flash (orig) | 0.500 | 0.261 | 0.250 | 0.00 |
  | h1++ | 0.656 | 0.467 | 0.430 | 0.20 |

  So a matched-pair metric is informative only if errors depend on the specific edit. T1 must test
  that directly (excess inconsistency), not assume it.

## 3. Candidate tests, ranked

### T1 — Counterfactual single-edit flips (priority 1, feasible with the existing oracle)

Take a v4 base state and apply **one** edit; relabel with the exact oracle; keep pairs whose
optimal-plan set changes. Edits (all within the static formalism):
- **E-obs:** one world variable becomes observed evidence (an ASK obligation disappears, or a different
  branch of the rules becomes relevant — the *indirect* cases matter most).
- **E-cert:** one computed variable gets its certified value (a COMPUTE obligation disappears).
- **E-mask:** one action becomes unavailable, listed as "unavailable" so prompt length and action count
  stay fixed (may switch to an alternative plan, or to NEITHER).
- **E-cost** is excluded (that is E10, already characterised).

Pre-registered strata by transition type: drop-one-action (direct), plan restructures (indirect),
class change (e.g. BOTH→INFORMATION_ONLY), into ALREADY_SUFFICIENT, into NEITHER.

Metrics: item optimal rate; pair both-optimal; **transition accuracy** (the model's plan change equals an
oracle-optimal change); **excess inconsistency** = P(both correct) − P(A)·P(B), family-clustered CI;
over-intervention rate on ALREADY_SUFFICIENT members; non-answer rate by class.

Hypothesis to pre-register: for the strong models, excess inconsistency is < 0 on *indirect* edits (errors
concentrate where the edit changes the plan beyond removing the revealed action) and ≈ 0 on direct edits.
v3 evidence above predicts ≈ 0 overall; T1 is informative either way.

Implementation: edit operators beside `variants.cost_sweep` (`FormalState.with_knowledge` already exists),
oracle relabelling, a `pair_id` field, `build_variant_jobs` reuse, analysis in a new `analyze_flips`.
Estimate (mine, untested): ~1–1.5 working days including tests and a heuristic-only dry run.

### T3 — Relevance vs necessity at fixed size (priority 2, feasible with generator work)

Hold the number of actions and prompt length fixed; vary only the share of offered non-optimal actions
that are **relevant but unnecessary** (touch the target's support but are in no minimal sufficient plan)
versus **irrelevant**. Matched within family by swapping one kind for the other.
Metrics: redundancy rate (sufficient, not minimal), inclusion rate of relevant-unnecessary vs irrelevant
actions, optimal given sufficient, regret. Construct: the gemma failure; literature anchor:
ToolChoiceConfusion (relevance ≠ necessity), but as an evaluation of the model's own pruning.
Risk: building relevant-but-unnecessary actions without changing oracle complexity; report the
oracle-complexity controls per stratum. Estimate: ~1.5–2 days.

### T5 — Stopping / no intervention (folded into T1)

Flips into ALREADY_SUFFICIENT (over-intervention, the dominant error in Ask/Relax/Act) and into NEITHER
(recognising that nothing suffices; glm's non-termination). No separate generator.

### T2 — Information-source switching (restricted; needs a semantics decision)

The literature version (SURE-Act: ask vs lookup) is information vs information. Our version would be
information vs certified computation for the same X. Under A10/F1 a COMPUTE action exists only when X is
derivable from visible inputs, so in a naive pair the action menu differs (ASK_X in one, COMPUTE_X in the
other) and the answer is **readable from the menu** — a surface-cue test, expected at ceiling.
A menu-constant version (both ASK_X and COMPUTE_X listed; derivability flips with whether the inputs are
visible) needs a computation whose availability depends on unknown inputs — not in the current static
formalism. **Decision needed:** either run only the naive form as a labelled control, or extend F1 (and
then treat it as part of the T4 extension). Not recommended for this sprint.

### T4 — Conditional sequential planning (separate extension)

Contingent epistemic policies (the second action depends on the first's outcome; question order).
Requires a new contingent-policy oracle (policy trees, expected cost, worst-case sufficiency) and new
scoring. Must not be scored with the static-plan oracle. MT-InfoSeek studies order only observationally,
so a controlled version would be new — but it is a project of its own. Not feasible this sprint.

### T6 — Unseen structural families (later)

v3 has four motifs (`and_or`, `parity`, `threshold`, `case_split`) and the held-out theme shift only.
A held-out motif needs a new template. Useful for generalisation claims; not before T1/T3.

## 4. Novelty overlaps and how v4 must differ

| Test | Closest prior work | Overlap | What must be different |
|---|---|---|---|
| T1 | Ask/Relax/Act (IFC, matched pairs) | Matched pairs, solver labels, pair correctness | Edits change a *minimal sufficient plan* over mixed information + computation actions; transition scoring; excess inconsistency vs independence |
| T2 | SURE-Act source shift (0/24) | Same unknown, different correct action | Information vs certified computation, not two information channels; only if the menu-cue problem is solved |
| T3 | ToolChoiceConfusion; MT-InfoSeek MSS | Relevant ≠ necessary; minimal sets | The model's own pruning, exact oracle, unequal costs, fixed action count and length |
| T4 | MT-InfoSeek (order, observational) | Order of queries matters | Controlled contingent policies with an exact oracle |
| Mitigation baseline | Active Epistemic Control | Commit only on grounded/verified facts | A grounded-verification controller as a baseline for the Epistemic Obligation Planner |

Do not claim: that models underestimate missing information (MT-InfoSeek), that output format changes
decisions (Ask/Relax/Act §5), that uncertainty mis-signals compute need (DIAL), or epistemic control as
such (AEC).

## 5. Scientific risks

1. **Ceiling again.** Strong models may solve single-edit flips as easily as v3 items (v3 pair data
   suggest independence). Pre-register that a null T1 result is reported as such.
2. **Selection by design.** v4 dimensions overlap failures already seen (redundancy, NEITHER). Mitigation:
   rationale fixed from formal structure; prospective freeze; disclosure above; evaluate fresh models too.
3. **Surface cues.** A one-line edit is visible; models may pattern-match the edited line. Control: report
   h1++ on the same pairs, and include *indirect* edits where the plan change is not the edited line.
4. **Format as treatment.** Forced schema changes plans (gemma, 2026-11-13; Ask/Relax/Act §5). Fix one
   output protocol per model before freezing and do not mix conditions.
5. **Non-answers.** Truncation is informative (glm) but also budget-dependent. Pre-register the output cap
   per model and report non-answer rates by class, separately from planning errors.
6. **Small samples.** 10 calibration families gave wide intervals. Power the v4 dev/test split on families,
   not instances.

## 6. Feasibility

I don't know the remaining sprint time; it is not recorded in the repository. Effort estimates are mine
and untested.

| Test | Oracle | Generator work | Estimate | This sprint? |
|---|---|---|---|---|
| T1 flips (incl. T5) | existing static oracle | edit operators + pairing + analysis | ~1–1.5 days | yes |
| T3 relevance vs necessity | existing static oracle | new action-construction parameter | ~1.5–2 days | possibly, after T1 |
| T2 source switching | existing (naive form) / extended F1 (menu-constant) | moderate / large | — | naive form only, as a control |
| T4 contingent planning | **new oracle** | large | — | no (separate extension) |
| T6 unseen motifs | existing | new template | ~2+ days | no |

Next step if approved: write the T1 pre-registration (hypotheses, strata, metrics, family counts, models,
output protocol, budget), implement the edit operators with tests, run oracle and heuristic checks only,
then freeze `pool_v4` before any model call.
