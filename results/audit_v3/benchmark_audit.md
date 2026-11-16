# Benchmark audit

Pool: `data/generated/pool_v3/instances.jsonl`. No model was called. The shortcut probe is trained on the train split and evaluated on the dev split; the test split is not used.

## 1. Shortcut probe

A lookup-table classifier memorises the majority resource class for each tuple of surface features of the prompt (counts of offered ASK/COMPUTE actions and of known/unknown world and computed variables). If it beats the majority baseline by a wide margin, the class can be read off the prompt without reasoning about relevance or sufficiency.

| Scope | Features | Comparison pool | This pool | Majority baseline |
|---|---|---|---|---|
| insufficient_only | action_counts | 56.4% | 40.2% | 42.7% |
| insufficient_only | knowledge_counts | 69.2% | 42.9% | 42.7% |
| insufficient_only | all_counts | 57.9% | 41.9% | 42.7% |
| all_classes | action_counts | 51.4% | 34.9% | 37.1% |
| all_classes | knowledge_counts | 63.3% | 38.0% | 37.1% |
| all_classes | all_counts | 52.0% | 35.6% | 37.1% |

**Residual.** The class is defined by which *relevant* variables are unknown, so counts of known variables by kind keep some signal even with randomised distractors. This probe is reported as a surface-feature baseline alongside every E3 result; a model's diagnosis accuracy should be read against it, not against chance.

## 2. Leakage

- Families in more than one split: 0 (of 300)
- Identical prompt texts across splits: 0
- Distinct instruction wrappers per mode (must be 1): {'end_to_end': 1, 'detection_controlled': 1}
- Label or role words in state text: none

## 3. Balance

Resource class by split:

- train: {'ALREADY_SUFFICIENT': 165, 'INFORMATION_ONLY': 238, 'COMPUTATION_ONLY': 235, 'BOTH': 466, 'NEITHER': 165}
- dev: {'ALREADY_SUFFICIENT': 72, 'INFORMATION_ONLY': 103, 'COMPUTATION_ONLY': 96, 'BOTH': 202, 'NEITHER': 72}
- test: {'ALREADY_SUFFICIENT': 63, 'INFORMATION_ONLY': 78, 'COMPUTATION_ONLY': 84, 'BOTH': 180, 'NEITHER': 63}

True rate of computed variables (a skewed rate would let a model guess certified results):

- kind=cnf_sat: 0.47 (n = 326)
- kind=modpow: 0.46 (n = 319)
- kind=posterior_above: 0.50 (n = 296)
- kind=primality: 0.49 (n = 309)
- role=d1: 0.50 (n = 163)
- role=d2: 0.43 (n = 69)
- role=i1: 0.50 (n = 118)
- role=i2: 0.40 (n = 120)
- role=i3: 0.56 (n = 136)
- role=i4: 0.86 (n = 7)
- role=m1: 0.40 (n = 53)
- role=u1: 0.43 (n = 67)
- role=u2: 0.51 (n = 59)
- role=z1: 0.54 (n = 147)
- role=z2: 0.46 (n = 154)
- role=z3: 0.45 (n = 110)
- role=z4: 0.43 (n = 47)

True rate of the target, by sibling type: {'ALREADY_SUFFICIENT': 0.5, 'BOTH': 0.5, 'COMPUTATION_ONLY': 0.5, 'INFORMATION_ONLY': 0.5, 'NEITHER': 0.5, 'PREMATURE_STOP': 0.48, 'RELEVANT_INSUFFICIENT_COMPUTATION': 0.5, 'RELEVANT_INSUFFICIENT_INFORMATION': 0.48, 'SUFFICIENT_NON_MINIMAL': 0.51}

## 4. Labels

- Brute-force re-verification of class, optimal cost and every optimal plan: 2282 instances, 0 mismatches.
- Number of optimal plans per resolvable instance: {'1': 1952, '2': 26, '4': 4}. Scoring accepts any plan that is sufficient at optimal cost, not only the listed ones (tested in `tests/test_scoring_ties.py`).

## 4a. Leaks found by the independent adversarial audit

- Implication rules whose consequent is true in the latent world: 0.51 of 1307 (1.00 = the rule text copies hidden values; about 0.5-0.75 is the unavoidable information in a true rule).
- Rule defining Q: most common position holds 18% of instances across 8 positions.
- Optimal share by action cost: {'1': 0.17, '2': 0.18, '3': 0.18, '4': 0.2, '5': 0.21, '6': 0.12, '7': 0.12, '8': 0.11, '9': 0.1, '10': 0.11}

## 4b. Shallow heuristic baselines (dev; deterministic, no model)

| Heuristic | Class accuracy | Plan sufficient | Plan optimal |
|---|---|---|---|
| h1 | 67.0% | 61.5% | 46.2% |
| h1p | 57.2% | 54.5% | 40.9% |
| h1pp | 74.7% | 75.4% | 50.6% |

h1 reads only the rule defining Q; h1p adds aliases and NEITHER when an action is missing; h1pp also expands definitions one level. Model results must be read against these, and are also reported on the subset where h1pp fails (`heuristic_hard`).

## 4c. Can the certified computations be done in the head?

- Posterior by rounded log-likelihood sums: 51.5% correct (n = 233).
- Modular exponentiation, 'true unless refuted by a small factor of m': 47.6% (majority baseline 52.4%, n = 267).
- Primality from the size of n (threshold fitted on train): 49.3% on dev (majority baseline 56.7%, n = 67).
- 3-SAT near the threshold: no shortcut found by the audit.

## 4d. Composition of the pre-registered heuristic_hard subset (dev)

Selecting on a baseline's failure selects on a correlate of difficulty. Compare within class, never pooled across subsets.

| Subset | n | Classes | Motifs | Mean optimal-plan size | Mean actions | Mean prompt chars |
|---|---|---|---|---|---|---|
| all | 545 | {'ALREADY_SUFFICIENT': 0.132, 'BOTH': 0.371, 'COMPUTATION_ONLY': 0.176, 'INFORMATION_ONLY': 0.189, 'NEITHER': 0.132} | {'and_or': 0.125, 'case_split': 0.273, 'parity': 0.365, 'threshold': 0.237} | 1.39 | 7.66 | 5770.91 |
| heuristic_hard | 198 | {'ALREADY_SUFFICIENT': 0.162, 'BOTH': 0.374, 'COMPUTATION_ONLY': 0.242, 'INFORMATION_ONLY': 0.222} | {'and_or': 0.157, 'case_split': 0.364, 'parity': 0.268, 'threshold': 0.212} | 1.33 | 8.01 | 6087.57 |
| heuristic_easy | 347 | {'ALREADY_SUFFICIENT': 0.115, 'BOTH': 0.369, 'COMPUTATION_ONLY': 0.138, 'INFORMATION_ONLY': 0.17, 'NEITHER': 0.207} | {'and_or': 0.107, 'case_split': 0.222, 'parity': 0.421, 'threshold': 0.251} | 1.42 | 7.46 | 5590.22 |

Share of each class that is heuristic_hard: {'ALREADY_SUFFICIENT': 0.444, 'BOTH': 0.366, 'COMPUTATION_ONLY': 0.5, 'INFORMATION_ONLY': 0.427, 'NEITHER': 0.0}.

- Rendering round-trip (state rebuilt from the prompt text alone, then re-solved): 2282 instances, 0 mismatches. The prompt carries everything the oracle uses.

## 5. Variants (E10–E12), deterministic sample

- Brute-force label re-verification: 534 variants, 0 mismatches.
- Rendering round-trip: 534 variants, 0 mismatches.

