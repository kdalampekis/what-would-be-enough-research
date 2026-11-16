# Follow-up calibration diagnostics — findings (2026-11-13)

Scope: dev split, the same 10 calibration families (74 instances). Diagnostic, not confirmatory.
All intervals are 95% family-clustered bootstrap; no significance tests. Full tables:
`diagnostics.md` / `diagnostics.json` (built by `experiments/analyze_calibration.py` from saved raw
responses). The test split was not used. E10, E11, E14 and the mitigation were not run.

## What was run (paid calls, all through the existing credit ledger)

| Condition (model key) | Change vs original | Jobs | Outcome |
|---|---|---|---|
| `adaption-gemma-4-26b-a4b-it-schema` | forced JSON-schema function tool (`settings.structured = "function_tool"`) | 278 (1 probe + full set) | 277 answered; 1 job failed twice with a dropped stream (`RemoteProtocolError`), left missing |
| `adaption-glm-53-flash-schema` | same forced tool | 1 probe | ok, parsed |
| `adaption-glm-53-flash-32k` | 32,000-token cap | the 73 jobs that truncated at 16k | 34 answered, 39 truncated again (no text) |

Budget flag: `--budget` is a cap on the **cumulative** ledger total
(`results/raw/pilot/spend_ledger_credits.jsonl`, `src/msep/models/spend.py`). Ledger was 9.8297 before
this phase; every call used `--budget 24.8297` (9.8297 + 15). Ledger after: **10.6908**, so
**0.8611 additional credits**.

Provider configuration for the forced schema (`src/msep/models/providers/adaption_provider.py`):
`tools=[{"type": "function", "name": <schema name>, "parameters": <job JSON schema>, "strict": true,
"description": "Submit your answer as the arguments of this call."}]`,
`tool_choice={"type": "function", "name": <schema name>}`; the function call's `arguments` string is
parsed; no call means no text (scored unparsed). SDK `adaption` 0.19.0 has no response_format /
text.format parameter; this tool form is the documented pass-through ("another OpenAI-compatible
Responses tool forwarded to the model provider"). Enforcement is **not** strict in practice: 1 of 277
schema answers still violated the schema, and 2 judgment answers made no call.

## 1. Original vs corrected results

Plan sufficiency / optimality on resolvable states, *all attempted* basis (unparsed = failure),
Detection-Controlled (E2E and DxC in `diagnostics.md`):

| Condition | Parse-error rate | Truncation rate | Sufficient | Optimal | Optimal given sufficient | Class acc. (DC) |
|---|---|---|---|---|---|---|
| gemma-4-26b original | 0.342 | 0.000 | 0.44 [0.31, 0.59] | 0.26 [0.15, 0.39] | 0.58 (n=24) | 0.33 [0.24, 0.42] |
| gemma-4-26b +schema | 0.011 | 0.000 | 0.81 [0.66, 0.96] | 0.33 [0.20, 0.47] | 0.41 (n=44) | 0.69 [0.58, 0.78] |
| glm-5.3-flash original | 0.263 | 0.263 | 0.59 [0.46, 0.71] | 0.56 [0.40, 0.69] | 0.94 (n=32) | 0.52 [0.41, 0.61] |
| glm-5.3-flash recovered (16k + 32k re-runs) | 0.140 | 0.140 | 0.83 [0.77, 0.89] | 0.80 [0.73, 0.86] | 0.96 (n=45) | 0.75 [0.69, 0.82] |

Caveats that change interpretation:
- **gemma +schema is a different condition, not a pure format fix.** On the 97 resolvable items parsed
  in both conditions, the schema condition is lower: optimal −0.14 [−0.25, −0.05], sufficient −0.08
  [−0.17, −0.01]; 26 of 97 plans differ. Items that did not parse originally are harder (under the
  schema: sufficient 0.75, optimal 0.19, n=64). So the original *parsed-only* rates (optimal 0.48 DC)
  were inflated by selection, and the schema rates mix a format fix with a behaviour change.
- **glm recovered mixes two output caps** (16k for originally answered jobs, 32k for re-runs). It is a
  sensitivity analysis. When glm answers, it is at ceiling (parsed-only sufficient 1.00, optimal
  0.96–1.00 in every mode); its gap is entirely non-answers.

## 2. Sufficiency vs optimality (all attempted, resolvable, n=54 per mode, 10 families)

| Model | Mode | Sufficient | Optimal | Ceiling (≥0.95) suff / opt |
|---|---|---|---|---|
| qwen3.5-397b | E2E / DC / DxC | 1.00 / 1.00 / 1.00 | 0.96 / 0.96 / 1.00 | Y / Y in all |
| qwen3.8-27b | E2E / DC / DxC | 0.98 / 0.98 / 1.00 | 0.98 / 0.96 / 0.96 | Y / Y in all |
| deepseek-v4-flash | E2E / DC / DxC | 0.98 / 1.00 / 0.98 | 0.98 / 0.98 / 0.96 | Y / Y in all |
| gemma-4-26b (orig) | E2E / DC / DxC | 0.52 / 0.44 / 0.65 | 0.35 / 0.26 / 0.43 | n / n |
| gemma-4-26b +schema | E2E / DC / DxC | 0.74 / 0.81 / 0.79 | 0.30 / 0.33 / 0.36 | n / n |
| glm-5.3-flash (orig) | E2E / DC / DxC | 0.70 / 0.59 / 0.67 | 0.70 / 0.56 / 0.67 | n / n |
| glm-5.3-flash recovered | E2E / DC / DxC | 0.89 / 0.83 / 0.76 | 0.89 / 0.80 / 0.76 | n / n |
| h1++ baseline | E2E / DC / DxC | 0.89 / 0.89 / 0.89 | 0.59 / 0.59 / 0.59 | n / n |

The three strong models are at **both** a sufficiency and an optimality ceiling. Where optimality is
lost below sufficiency, it is almost always **redundancy**, not cost choice (counts of sufficient but
non-optimal plans, all modes pooled): gemma +schema 62 redundant (not minimal) vs 11 minimal-but-dearer;
strong models 0–2 of either per mode. Versus h1++ on the same pairs (DC, optimal, all attempted):
qwen3.5-397b +0.37 [0.15, 0.58], qwen3.8-27b +0.37 [0.19, 0.55], deepseek +0.39 [0.23, 0.57],
glm recovered +0.20 [0.02, 0.38], gemma +schema −0.26 [−0.38, −0.16].

## 3. Format / truncation: improvements and what remains

- gemma: parse errors 95/278 (34.2%) → 3/277 (1.1%): 1 plan still violates the schema, 2 judgments made
  no function call; 1 job missing (stream dropped after ~61 s, twice). The 48 original
  "plan must be a list of {type, action} objects" errors and the "Extra data" / code-fence errors are gone.
- glm-5.3-flash: truncations 73/278 (26.3%) → 39/278 (14.0%). Recovered answers used 7,278 output tokens
  on average (max 24,262). The 39 that still truncate produced only reasoning, no text, at 32,000 tokens.
  They are concentrated: BOTH 22, NEITHER 11, COMPUTATION_ONLY 5, INFORMATION_ONLY 1; 30 instances in
  all 10 families. 11 of the 20 NEITHER jobs give no answer even at 32k.
- glm-5.2 was not repeated (no answer at 16k or 32k earlier).

## 4. Strongest unexplained epistemic-planning failure

**Redundant plans: sufficient plans padded with unnecessary actions (gemma-4-26b).** Under the forced
schema, 41% of its sufficient DC plans are optimal; 52 of 67 redundant plans contain a complete optimal
plan plus 1–2 extra actions, and the extras are mostly ones the oracle marks *irrelevant* (62 of 107
extra actions) or *relevant but insufficient* (23). It persists in Diagnosis-Controlled (optimal 0.36),
so it is not a diagnosis failure, and it is worse than the text-only h1++ heuristic. This is a failure of
minimality (pruning), the benchmark's target construct, not of cost arithmetic.

Second, different in kind: **glm-5.3-flash does not terminate** on a subset of items, mostly BOTH and
NEITHER (the states where the right conclusion is "no plan resolves it" or that two kinds of resource
are needed), while its completed answers are near perfect.

For the strong models there is no unexplained planning failure at this size: their residual errors are
resource-class labels on INFORMATION_ONLY and NEITHER items whose plans and deferrals are still correct
(e.g. qwen3.5-397b DC: NEITHER class accuracy 0.80, defer 1.00).

All of this rests on 10 families; it is diagnostic.

## 5. E10 vs a separate challenge tier

**A separate challenge tier is the better next experiment; E10 is not.** Evidence (offline inspection,
regenerated `variants_v3/cost.jsonl` matches the frozen sha256 `7273fc78…`):
- An E10 variant changes one action's cost by a little. Only the 120 "below" variants of 527 dev variants
  (23%, 38 families) change which plan is cheapest; the cost gap there is always 1, and 75 of 120 are a
  bulk-vs-single comparison of two numbers. A cost-blind policy that keeps the base plan scores ~0.77
  pooled (1.00 on equal/above, 0.00 on below).
- E10 probes cost choice, but the failures observed are redundancy and non-termination; minimal-but-dearer
  errors are 0–1 per mode for the strong models, which are already 0.96–1.00 optimal on base items that
  include the same kind of cost choice (148 of 401 resolvable dev base items have two minimal plans of
  different cost). Expected E10 result for strong models: ceiling.
- Prepared but not run: `run_pilot.py --experiments e10 --variants data/generated/variants_v3
  --e10-items flip` (tests in `tests/test_e10_runner.py`); `analyze_e10` and the report now give the
  flip-item ("below") optimal rate separately. Dry run on full dev, flip items: 240 jobs per model;
  worst case 13.66 (qwen3.5-397b), 4.82 (qwen3.8-27b), 0.53 (deepseek) credits.

Proposed challenge tier (v3 stays frozen and primary): new structural difficulty fixed *a priori* from
the generator's parameters, not tuned on these models' outputs: larger theories and deeper rule chains,
many more irrelevant and relevant-but-insufficient actions per state (pruning load), more NEITHER and
BOTH states with larger search spaces, and alternative minimal plans with larger, multi-action cost
trade-offs. Released as a new version, frozen and hashed before any model sees it, validated first with
the oracle and the h1/h1p/h1++ heuristics only, and evaluated on fresh models as well as these. Tension
to decide explicitly: the dimensions above overlap with failures seen here, so the design rationale must
be pre-registered from the generator's structure, and the confirmatory claims stay on v3.

## 6. Credits

Additional this phase: **0.8611 credits** (ledger 9.8297 → 10.6908), against an authorization of 15.
