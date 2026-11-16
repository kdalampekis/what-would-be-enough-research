# Scientific risks, ranked by how likely they are to invalidate a future finding

Benchmark v3.0 is frozen (`data/FREEZE_v3.json`); risks below are handled in analysis and reporting, not by further redesign.

**Date:** 2026-11-04. **Ranking:** likelihood × impact on the headline claims (H2–H4, mitigation).

| # | Risk | Likelihood | What it would invalidate | Current mitigation | Still to do |
|---|---|---|---|---|---|
| 1 | **Output cap truncates reasoning.** The 1,000-token cap includes thinking/reasoning on both APIs. At medium effort many responses may be cut off, so failures would measure the cap, not the model | High | Every pilot result | Smoke gate stops on truncation; truncations are counted and reported | Decide the cap and effort before the pilot (cap vs effort) |
| 2 | **Shallow solvability.** On v3, a text-only heuristic gets an optimal plan on about 50% of dev | High | "Models plan well" claims; any comparison not read against the heuristic | `heuristic_hard` stratum pre-registered; heuristic baselines in every report | Report every hypothesis on the hard stratum; consider deeper motifs if the hard stratum is small (about 36% of dev) |
| 2b | **NEITHER is shallow-solvable.** h1pp gets 100% of NEITHER items on v3 ("an unknown input of q has no action"), and the hard subset contains none | High (for E8) | Any claim that NEITHER handling shows epistemic reasoning | Reported against h1pp; prohibited claim in RESEARCH_READINESS | Report E8 only as a comparison with h1pp |
| 2c | **Selection bias of `heuristic_hard`.** Selection on a baseline's failure changes the class and motif mix | Medium | Pooled hard-vs-full comparisons | Composition reported; comparisons within class only; full v3 is primary | — |
| 3 | **Certified-computation convention.** A strong model may compute a K value itself and treat the state as sufficient. End-to-End would score that as a detection error, though it is a different choice | Medium–high | E2 and End-to-End results; COMPUTE-related diagnosis | v3 tasks resist simple mental shortcuts (audit §4c); Detection- and Diagnosis-Controlled modes; the prompt states the rule | E14 control prepared (capability per task kind; skip rate when capable vs not); results reported with and without capable items |
| 4 | **Prompt sensitivity.** One wording per mode | Medium | Size of every effect | Held-out skin (E12) | Add 2 paraphrases per mode on dev before freezing; report variance |
| 5 | **Instrument faults with real APIs.** Unverified GPT-5.6 Sol ID and parameters; refusals; nondeterminism (no temperature control) | Medium | GPT results | Config checker; smoke test; refusals and truncations kept and reported; raw logs | Verify against OpenAI docs; repeat a 100-item subset 5 times for variance |
| 6 | **Statistical power.** The pilot is 10 families; the test split has 63 families | Medium | Confirmatory conclusions | Family-clustered CIs; Holm; McNemar on matched pairs | Power estimate from pilot effect sizes before freezing; enlarge the pool if needed (cheap: generation is deterministic) |
| 7 | **Class and sibling imbalance in v3.** Binning gives more BOTH (848 of 2,282) | Medium–low | Pooled accuracy | Macro-F1, balanced accuracy, per-class tables | Report per class always |
| 8 | **External validity.** Synthetic propositional worlds; E13 is a converter only | Medium for generalisation claims, low for benchmark claims | Claims about real agents | Claims bounded in CLAIMS.md | Obtain licensed ProofWriter/FOLIO conversions |
| 9 | **Mitigation leakage.** The planner could use hidden information | Low (audited) | The mitigation result | Import and attribute guards; opaque tasks; text + `execute()` only; condition B-parser labelled an upper bound | Keep the guards in CI |
| 10 | **Novelty.** SURE-Act unverified; arxiv unreachable here | Medium for novelty wording, none for findings | The "we did not find…" sentence | Bounded wording | Final literature sweep within 24 h of submission |
| 11 | **Oracle error on larger instances** | Low | Labels | 228,199 E0 checks; full brute-force re-verification of all pool labels; independent auditor's solver agreed | Re-run the audit for any new template |
| 12 | **Readability of long prompts.** CNF tasks make prompts long (about 4–8k characters) | Low–medium | Diagnosis on COMPUTE-heavy items | Tasks are listed under their handles | Check length vs accuracy after the pilot (exploratory) |
| 13 | **Contamination.** Synthetic items are freshly generated | Low | — | — | — |

## Already fixed (for the record)

| Issue | How it was found | Fix |
|---|---|---|
| Count shortcuts in template v1 (probe 86–90%) | Our own audit | Template v2 randomisation |
| v2 solved 100% by reading q's rule; rule order, rule signs and costs leaked roles and hidden values | Independent adversarial audit | Template v3; seeded rule order; random implication signs; v2 relegated to a shallow subset |
| Mental shortcuts for posterior (100%), modpow (90%) and primality (70%) | Independent audit | Version-2 tasks (now at chance) |
| Ambiguous rendering of nested biconditionals | Rendering round-trip check | Parenthesised left sides |
| The planner could evaluate certified tasks for free | Leakage audit | Opaque agent-side tasks |
| E9 counted abstention as premature stopping; E10/E12 analysis bugs | Synthetic signature tests | Definitions and filters fixed |
