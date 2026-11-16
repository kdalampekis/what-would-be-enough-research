# Licensing

Copyright 2026 Konstantinos Dalampekis.

This repository has two licences, one for code and one for writing and data.

| What | Licence | Text |
|---|---|---|
| Original source code: everything under `src/`, `experiments/`, `tests/`, `paper/*.py`, and the configuration files | Apache License 2.0 | [`LICENSE`](LICENSE) |
| Original research writing: the report and its source under `paper/`, the Markdown documents in the repository root and under `docs/`, and the figures under `figures/` | Creative Commons Attribution 4.0 International (CC BY 4.0) | [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) |
| The synthetic benchmark: the generators' outputs (`pool_v3`, the T1 pairs, the rewording set, the variants), the manifests and freeze records under `data/`, and the oracle labels | CC BY 4.0 | [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) |

## Not covered by these licences

- **Model-generated outputs.** Text or structured answers produced by the evaluated language models are
  not licensed here. Any such material in this repository is included as research evidence; the terms of
  the model provider apply to it.
- **Third-party material.** The sprint's report template, the titles and findings of cited papers, and
  anything quoted from them belong to their authors and publishers.
- **Dependencies.** Packages listed in `pyproject.toml` (python-sat and the optional development tools)
  are not distributed with this repository and keep their own licences.

## How to cite

Cite the report: Konstantinos Dalampekis (2026). *What Would Be Enough? Evaluating Minimal Sufficient
Epistemic Plans in LLM Agents.* AI x Epistemics Research Sprint, Apart Research.

## Raw model responses

The complete raw responses of the evaluated models are published in this repository as research evidence
(compressed archives under `results/raw/`), so that every reported table and figure can be regenerated
from them. They are model-generated outputs: the licences above do not cover them, and they are provided
as they were returned by the provider, without warranty.
