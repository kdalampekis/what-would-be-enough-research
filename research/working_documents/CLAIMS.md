# What we can and cannot claim (2026-11-04, after the adversarial audit)

See also `RESEARCH_READINESS.md` §5 (prohibited claims) and §4 (what would support or falsify each hypothesis).

No language model has been evaluated. Every model-related claim below is therefore **not yet supported**.

## Can claim now (with the evidence)

| Claim | Evidence |
|---|---|
| The oracle is exact on the validated instance sizes | E0: 228,199 checks (including 100 template-v3 families), 0 disagreements across brute force, SAT/MaxSAT, obligation planner and WMC (`results/oracle_validation.md`); mutation tests show the checks catch planted bugs |
| Computation actions cannot reveal hidden world facts | Enforced at construction; E0 checks invariance across consistent worlds |
| Benchmark labels are correct | All pool_v2 (3,300) and pool_v3 (2,282) labels re-verified by brute force; an independent solver written by the adversarial auditor agreed on all 671 v2 dev items |
| The prompt text carries everything the oracle uses | Rendering round-trip on every pool instance and a variant sample, 0 mismatches |
| Template v2 does not measure sufficiency reasoning | A text-only heuristic scores 100% on it (`results/audit_v2`) |
| On template v3 the known shortcuts are closed | Count probe at chance, no value or position leaks, mental-computation attacks at chance (`results/audit_v3`) |
| Shallow heuristics reach about 50% optimal plans on v3 dev | `results/baselines_v3` (deterministic, real) |
| No family-level split leakage; instruction wrappers are identical across classes | Benchmark audit |
| The analysis pipeline computes what it claims to | 12 synthetic mock agents with signature tests, including mode-dependent ones for the mode decomposition (`tests/test_mock_signatures.py`) |
| The candidate mitigation cannot use hidden information | Import and attribute guards; opaque certified tasks; runs on text + `execute()` only (`tests/test_realistic_planner.py`) |

## Cannot claim yet

| Claim | Why not | What would support it |
|---|---|---|
| LLMs fail (or succeed) at minimal sufficient epistemic planning | No model run | Calibration pilot (dev), then frozen test evaluation |
| Diagnosis is easier than planning (H2), relevance is confused with sufficiency (H3), BOTH is harder (H4) | No model run | Confirmatory tests, PROTOCOL.md §4 |
| The benchmark is hard, not too easy, not impossible | Ceiling/floor unknown until models run | Calibration pilot |
| The benchmark is free of shortcuts | Shortcuts we know of are closed on v3, but a definition-reading heuristic still gets about half the plans optimal; unknown shortcuts may remain | Heuristic baselines and the `heuristic_hard` stratum in every report; further audits |
| The Epistemic Obligation Planner helps agents | Not evaluated. With the rule-based parser it recovers the formal state exactly, which says nothing about LLMs | (B) with an LLM extractor vs baselines on real models |
| The oracle planner (A) is a mitigation | It has the exact formal state; it is part of the oracle | Never claim this |
| Results transfer to natural tasks | E13 is a converter only; no external dataset was processed | Licensed ProofWriter/FOLIO conversions and runs |
| Robustness to structural/linguistic shift | Variants exist; no model results | E12 on real models |
| Novelty ("first") | Literature check incomplete; SURE-Act unverified; arxiv/sciencedirect unreachable from here | Final literature sweep within 24 h of submission (NOVELTY_MAP §8) |
| GPT-5.6 Sol settings are right | Model ID and parameters unverified | `--smoke` once OpenAI is reachable |

## Synthetic outputs

`results/synthetic/` contains mock-agent outputs. They are pipeline tests, labelled SYNTHETIC, and are never to be cited as findings.
