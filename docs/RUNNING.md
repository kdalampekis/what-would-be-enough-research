# Running models

How to run the benchmark against hosted models. This needs an API key and spends credits. To rebuild the reported numbers and figures without any API call, see the README.

The sections below were written during the project and are kept as they were. The runs actually made are listed in [`EXPERIMENT_INDEX.md`](EXPERIMENT_INDEX.md).

## Run on your own computer

Requires Python 3.10+ and git.

Clone the repository (private: you need access on GitHub) and enter it:

```bash
git clone https://github.com/kdalampekis/what-would-be-enough.git
```

```bash
cd what-would-be-enough
```

Create a virtual environment, activate it and install (on Windows activate with `.venv\Scripts\activate`):

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev,models]"
```

Generate the frozen benchmark (deterministic; may take several minutes) and check it matches the freeze:

```bash
python experiments/generate_benchmark.py --template v3 --families 300 --out data/generated/pool_v3
```

```bash
python experiments/freeze_benchmark.py --verify
```

Put your API key in `.env` (copy `.env.example`; `.env` is gitignored). The scripts read it automatically.

## Adaption-hosted open-weight models

Seven models are configured as `adaption-<model id>` in `configs/models.json`: gemma-4-31b-it, glm-5.2, qwen3.5-397b, gemma-4-26b-a4b-it, qwen3.8-27b, deepseek-v4-flash and glm-53-flash.
- Prices are in Adaption credits, so `--budget` is read in credits. Models priced in credits and in dollars cannot share a run.
- The SDK (0.19.0) has no JSON-schema option. The prompt asks for one JSON object and the parser extracts it; parse failures are reported, never repaired.
- Calls are streamed, the cap is 16,000 output tokens (these models reason first; the qwen3.5-397b smoke call spent 4,578 of 4,685 output tokens reasoning) and the SDK retries twice.
- Smoke test 2026-11-13 (before streaming): qwen3.5-397b passed (0.0175 credits, 101 s); a non-streamed glm-5.2 call returned 504 Gateway Time-out after 376 s.

Check the configuration and the key:

```bash
python experiments/check_config.py --models adaption-glm-5.2,adaption-qwen3.5-397b
```

Smoke test (one call per model; stops on any error, truncation or parse failure):

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --models adaption-glm-5.2,adaption-qwen3.5-397b --smoke --budget 5
```

Calibration run (278 calls per model; worst case at the cap about 20.3 credits for glm-5.2 and 15.8 for qwen3.5-397b; at the smoke call's token use, about 5 credits for qwen3.5-397b):

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --models adaption-glm-5.2,adaption-qwen3.5-397b --max-calls 300 --budget 50
```

## Real-model calibration pilot (Phase 2B; original plan — the runs actually made are in PROTOCOL.md's amendment and GATE2_DEV_REPORT.md)

Prerequisites:
- `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` as environment secrets;
- api.openai.com allowed;
- GPT-5.6 Sol's prices in `configs/models.json`;
- the output-cap decision (`RISKS.md` #1).

Run in this order, on dev only (the test split is refused).

Check the configuration (fails until the prerequisites are met):

```bash
python experiments/check_config.py
```

Count calls and the worst-case cost:

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --dry-run
```

Run the whole pipeline with a mock agent, no network:

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --dry-run-mock oracle_perfect
```

Verify the benchmark freeze:

```bash
python experiments/freeze_benchmark.py --verify
```

Smoke test (one real call per model; stops on truncation, refusal or parse error). The real-model budget defaults to $0, so it must be given explicitly:

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --smoke --budget-usd 75
```

Calibration run (E1, E3, E5, E7). Add `--experiments e1,e3,e5,e7,e14` to include the computation-capability control, and `--override claude-sonnet-5-5.settings.max_tokens=4000` (for example) to change a model's settings:

```bash
python experiments/run_pilot.py --data data/generated/pool_v3/instances.jsonl --splits dev --max-families 10 --max-calls 420 --budget-usd 75
```

Outputs:
- raw responses (with tokens and cost): `results/raw/pilot/`;
- structured log: `results/raw/pilot/run_log.jsonl`;
- spend ledger: `results/raw/pilot/spend_ledger.jsonl`;
- report and figures: `results/aggregate/calibration_dev/`.

