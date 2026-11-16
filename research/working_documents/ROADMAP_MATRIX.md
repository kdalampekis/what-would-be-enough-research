# ROADMAP_MATRIX.md — original roadmap vs current state (2026-11-14 00:05 UTC)

Research question (PROBLEM_SPEC.md §1): when an agent lacks sufficient grounds for a decision, can it tell
whether the minimal sufficient epistemic plan needs information, computation, both or neither, and construct
that plan? Hypotheses H1–H6 (EXPERIMENT_PLAN.md §2) are unchanged. T1/T1B/T3 are literature-motivated
extensions; they do not replace E0–E14. Priority: P0 must be done for submission; P1 if time; P2 later.

"Calibration" = 10 dev families (2026-11-13, diagnostic). "dev run" = all 72 dev families (running now).

## Hypotheses

| | Purpose | Evidence so far | Remaining | Pri |
|---|---|---|---|---|
| H1 detection is not the whole problem (DC > E2E, planning error remains) | separates detection from planning | calibration: strong models ~1.0 in every mode (ceiling); gemma/glm lower in E2E/DC than DxC, partly format/truncation | dev run E1–E9 by mode, 4 models | P0 |
| H2 diagnosis easier than exact planning | class vs plan | calibration: for strong models plan sufficiency 1.00 while class accuracy 0.94 (opposite direction) | dev run E3 vs E4/E6 | P0 |
| H3 sufficiency harder than relevance | relevance trap | calibration E5 at ceiling for strong models | dev run E5; T3 (secondary) | P0 / P1 |
| H4 BOTH is a major failure regime | mixed plans | calibration: no BOTH deficit for strong models; glm non-termination concentrated on BOTH/NEITHER | dev run E7 | P0 |
| H5 minimality and stopping are distinct | over-consumption, continued acting | calibration: optimality lost to redundancy (gemma); T1 pilot exploratory: over-intervention when state becomes sufficient | dev run E6/E9; **T1B registered test** (running) | P0 |
| H6 explicit obligations help | mitigation | infrastructure + leakage tests; parser+EOP upper bound 1.00 | **registered EOP comparison A/B/C/D** (running) | P0 |

## Experiments

| | Purpose | Implementation | Evidence | Remaining | Pri |
|---|---|---|---|---|---|
| E0 oracle validation | exactness of labels | done (SAT = brute force; E0 results) | validated; T1 items 3,938/3,938 agree | — | done |
| E1 base decision competence | task vs epistemic failure | run_pilot (decision pool) | calibration 1.00 (strong), ceiling | dev run | P0 |
| E2 insufficiency detection (E2E) | detection | run_pilot | calibration ~1.00 strong | dev run | P0 |
| E3 resource-class diagnosis (DC) | diagnosis | run_pilot | calibration 0.94–1.00 strong | dev run | P0 |
| E4 exact targeting (DxC) | action choice given class | run_pilot | calibration 1.00 strong | dev run | P0 |
| E5 relevance vs sufficiency | judgment pairs | run_pilot (judgment pool) | calibration 1.00 strong | dev run | P0 |
| E6 minimality | optimal among sufficient | run_pilot / analyze_calibration | calibration 0.96–1.00 strong; gemma 0.41 (schema) | dev run | P0 |
| E7 BOTH | mixed plans | run_pilot | calibration ceiling strong | dev run | P0 |
| E8 NEITHER / defer | recognising no plan | run_pilot | calibration defer 1.00 strong; glm non-termination | dev run | P0 |
| E9 stopping | excess acting | run_pilot | calibration premature stop 0.00 | dev run; T1B | P0 |
| E10 cost sensitivity | plan flips at cost boundaries | runner `--experiments e10 --e10-items flip` + tests; variants frozen | offline: only 120/527 dev variants flip; cost-blind policy ~0.77 pooled | run flip items only if time | P2 |
| E11 risk sensitivity | probabilistic/utility criterion | variants frozen (risk.jsonl); analyze_e11 exists; not wired in run_pilot | none | separate criterion; keep apart from logical benchmark | P2 |
| E12 structural shift | generalisation across structures/renderings | v3 has theme shift only; width/depth for v2 | none | define v3 shift set; run | P1 |
| E13 external validity | transfer to external tasks | partial (conversion to information actions only, F11) | none | small validated set if feasible | P2 |
| E14 internal computation capability | does capability change COMPUTE selection | `build_capability_jobs`, analyze_e14 (opt-in) | none | run capability pool on dev | P2 |
| T1 single-edit flips | counterfactual plan consistency | generator, freeze, analysis | dev pilot: inconclusive under registered rules | held-out (test) T1 after freeze | P0 (held-out) |
| T1B over-intervention (H-OI) | H1/H5 follow-up | registered + frozen | running (families 31–72) | analyse | P0 |
| T3 necessity vs relevance | causal necessity | design only (CHALLENGE_V4_DESIGN.md) | v3 action categories; gemma redundancy | limited secondary | P1 |
| S1 structured prompt (= B) | prompt-only mitigation | prompts_s1.py | running | analyse | P0 |
| S2 obligation verifier (= D) | verification without search | run_eop verified_results + tests | after B/C | analyse | P1 (no extra calls) |
| S3 EOP (= C) | extraction + formal planner | realistic_planner + llm_extractor | running | analyse; error analysis if it fails | P0 |
| S4 hybrid planner | LLM-estimated action effects | not built | — | out of scope this sprint | P2 |
| S5 shift robustness | EOP vs router under shift | not built (no learned router) | — | only if E12 runs | P2 |

## Held-out evaluation (P0, after the dev gate)

Test split untouched. Final run once after prompts, settings, mitigation and analysis are frozen: v3 test
(E1–E9, three modes), T1 test pairs, EOP A/B/C/D on test — with the same four models.
