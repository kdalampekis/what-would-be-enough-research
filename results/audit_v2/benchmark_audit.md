# Benchmark audit

Pool: `data/generated/pool_v2/instances.jsonl`. No model was called. The shortcut probe is trained on the train split and evaluated on the dev split; the test split is not used.

## 1. Shortcut probe

A lookup-table classifier memorises the majority resource class for each tuple of surface features of the prompt (counts of offered ASK/COMPUTE actions and of known/unknown world and computed variables). If it beats the majority baseline by a wide margin, the class can be read off the prompt without reasoning about relevance or sufficiency.

| Scope | Features | Comparison pool | This pool | Majority baseline |
|---|---|---|---|---|
| insufficient_only | action_counts | 86.2% | 56.4% | 50.0% |
| insufficient_only | knowledge_counts | 90.0% | 69.2% | 50.0% |
| insufficient_only | all_counts | 90.0% | 57.9% | 50.0% |
| all_classes | action_counts | 78.4% | 51.4% | 45.5% |
| all_classes | knowledge_counts | 90.9% | 63.3% | 45.5% |
| all_classes | all_counts | 90.9% | 52.0% | 45.5% |

**Residual.** The class is defined by which *relevant* variables are unknown, so counts of known variables by kind keep some signal even with randomised distractors. This probe is reported as a surface-feature baseline alongside every E3 result; a model's diagnosis accuracy should be read against it, not against chance.

## 2. Leakage

- Families in more than one split: 0 (of 300)
- Identical prompt texts across splits: 0
- Distinct instruction wrappers per mode (must be 1): {'end_to_end': 1, 'detection_controlled': 1}
- Label or role words in state text: none

## 3. Balance

Resource class by split:

- train: {'ALREADY_SUFFICIENT': 166, 'INFORMATION_ONLY': 830, 'COMPUTATION_ONLY': 332, 'BOTH': 332, 'NEITHER': 166}
- test: {'ALREADY_SUFFICIENT': 73, 'INFORMATION_ONLY': 365, 'COMPUTATION_ONLY': 146, 'BOTH': 146, 'NEITHER': 73}
- dev: {'ALREADY_SUFFICIENT': 61, 'INFORMATION_ONLY': 305, 'COMPUTATION_ONLY': 122, 'BOTH': 122, 'NEITHER': 61}

True rate of computed variables (a skewed rate would let a model guess certified results):

- kind=cnf_sat: 0.49 (n = 433)
- kind=modpow: 0.46 (n = 418)
- kind=posterior_above: 0.46 (n = 392)
- kind=primality: 0.51 (n = 419)
- role=c1: 0.47 (n = 300)
- role=c2: 0.48 (n = 162)
- role=dc: 0.49 (n = 300)
- role=zc1: 0.47 (n = 300)
- role=zc2: 0.49 (n = 300)
- role=zc3: 0.48 (n = 300)

True rate of the target, by sibling type: {'ALREADY_SUFFICIENT': 0.52, 'BOTH': 0.52, 'COMPUTATION_ONLY': 0.52, 'INFORMATION_ONLY': 0.52, 'MULTIPLE_PLANS_DIFFERENT_COSTS': 0.52, 'NEITHER': 0.52, 'PREMATURE_STOP': 0.52, 'RELEVANT_INSUFFICIENT_COMPUTATION': 0.52, 'RELEVANT_INSUFFICIENT_INFORMATION': 0.52, 'SUFFICIENT_NON_MINIMAL': 0.52, 'UNNECESSARY_EXTRA_ACTION': 0.52}

## 4. Labels

- Brute-force re-verification of class, optimal cost and every optimal plan: 3300 instances, 0 mismatches.
- Number of optimal plans per resolvable instance: {'1': 3000}. Scoring accepts any plan that is sufficient at optimal cost, not only the listed ones (tested in `tests/test_scoring_ties.py`).

## 4a. Leaks found by the independent adversarial audit

- Implication rules whose consequent is true in the latent world: 1.00 of 1500 (1.00 = the rule text copies hidden values; about 0.5-0.75 is the unavoidable information in a true rule).
- Rule defining Q: most common position holds 100% of instances across 1 positions.
- Optimal share by action cost: {'1': 0.09, '2': 0.25, '3': 0.28, '4': 0.0, '5': 0.0, '6': 0.0, '7': 0.0, '8': 0.0}

## 4b. Shallow heuristic baselines (dev; deterministic, no model)

| Heuristic | Class accuracy | Plan sufficient | Plan optimal |
|---|---|---|---|
| h1 | 90.9% | 90.9% | 87.2% |
| h1p | 100.0% | 90.9% | 90.9% |
| h1pp | 100.0% | 90.9% | 90.9% |

h1 reads only the rule defining Q; h1p adds aliases and NEITHER when an action is missing; h1pp also expands definitions one level. Model results must be read against these, and are also reported on the subset where h1pp fails (`heuristic_hard`).

## 4c. Can the certified computations be done in the head?

- Posterior by rounded log-likelihood sums: 100.0% correct (n = 293).
- Modular exponentiation, 'true unless refuted by a small factor of m': 90.0% (majority baseline 54.7%, n = 329).
- Primality from the size of n (threshold fitted on train): 69.7% on dev (majority baseline 50.0%, n = 76).
- 3-SAT near the threshold: no shortcut found by the audit.

- Rendering round-trip (state rebuilt from the prompt text alone, then re-solved): 3300 instances, 0 mismatches. The prompt carries everything the oracle uses.

## 5. Variants (E10–E12), deterministic sample

- Brute-force label re-verification: 880 variants, 0 mismatches.
- Rendering round-trip: 880 variants, 0 mismatches.

