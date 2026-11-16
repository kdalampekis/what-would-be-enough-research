"""Freeze (or verify) a registered protocol: the protocol text, the analysis code, the data it reads and the
model settings, pinned by sha256 in data/FREEZE_<NAME>.json.

    python experiments/freeze_protocol.py --name T1B --write
    python experiments/freeze_protocol.py --name T1B --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTOCOLS = {
    "T1B": {"files": ["PREREG_T1B.md", "experiments/analyze_t1b.py", "experiments/analyze_t1.py",
                      "src/msep/models/prompts.py", "src/msep/eval/pilot.py",
                      "src/msep/eval/plan_metrics.py", "src/msep/models/schemas.py",
                      "data/generated/t1_v1/pairs.jsonl", "data/generated/pool_v3/instances.jsonl"],
            "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                       "adaption-deepseek-v4-flash"]},
    "EOP": {"files": ["PREREG_EOP.md", "experiments/run_eop.py", "experiments/analyze_t1.py",
                      "src/msep/models/prompts_s1.py", "src/msep/models/prompts.py",
                      "src/msep/controllers/realistic_planner.py", "src/msep/controllers/llm_extractor.py",
                      "src/msep/obligations/extraction.py", "src/msep/obligations/discharge.py",
                      "src/msep/obligations/model.py", "src/msep/benchmark/parsing.py", "src/msep/eval/pilot.py",
                      "src/msep/eval/plan_metrics.py", "src/msep/models/schemas.py",
                      "data/generated/t1_v1/pairs.jsonl", "data/generated/pool_v3/instances.jsonl"],
            "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                       "adaption-deepseek-v4-flash"]},
    "EOP_A1": {"files": ["PREREG_EOP.md", "experiments/run_eop.py", "experiments/analyze_t1.py",
                         "src/msep/models/prompts_s1.py", "src/msep/models/prompts.py",
                         "src/msep/controllers/realistic_planner.py", "src/msep/controllers/llm_extractor.py",
                         "src/msep/obligations/extraction.py", "src/msep/obligations/discharge.py",
                         "src/msep/obligations/model.py", "src/msep/benchmark/parsing.py", "src/msep/eval/pilot.py",
                         "src/msep/eval/plan_metrics.py", "src/msep/models/schemas.py",
                         "data/generated/t1_v1/pairs.jsonl", "data/generated/pool_v3/instances.jsonl"],
               "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                          "adaption-deepseek-v4-flash"]},
    "EOP_A2": {"files": ["PREREG_EOP.md", "experiments/run_eop.py", "experiments/analyze_t1.py",
                         "src/msep/models/prompts_s1.py", "src/msep/models/prompts.py",
                         "src/msep/controllers/realistic_planner.py", "src/msep/controllers/llm_extractor.py",
                         "src/msep/obligations/extraction.py", "src/msep/obligations/discharge.py",
                         "src/msep/obligations/model.py", "src/msep/benchmark/parsing.py", "src/msep/eval/pilot.py",
                         "src/msep/eval/plan_metrics.py", "src/msep/models/schemas.py",
                         "data/generated/t1_v1/pairs.jsonl", "data/generated/pool_v3/instances.jsonl"],
               "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                          "adaption-deepseek-v4-flash"]},
    "FINAL": {"files": ["PREREG_FINAL.md", "PREREG_EOP.md", "PREREG_T1B.md", "PREREG_T1.md", "PROTOCOL.md",
                        "experiments/run_eop.py", "experiments/run_pilot.py", "experiments/analyze_final.py",
                        "experiments/analyze_t1.py", "experiments/analyze_t1b.py", "experiments/chain_final.sh",
                        "experiments/final_finalize.sh",
                        "src/msep/models/prompts_s1.py", "src/msep/models/prompts.py", "src/msep/models/runner.py",
                        "src/msep/models/providers/adaption_provider.py",
                        "src/msep/controllers/realistic_planner.py", "src/msep/controllers/llm_extractor.py",
                        "src/msep/obligations/extraction.py", "src/msep/obligations/discharge.py",
                        "src/msep/obligations/model.py", "src/msep/benchmark/parsing.py", "src/msep/eval/pilot.py",
                        "src/msep/eval/experiments.py", "src/msep/eval/bootstrap.py", "src/msep/eval/extraction_match.py",
                        "src/msep/eval/plan_metrics.py", "src/msep/models/schemas.py",
                        "data/generated/t1_v1/pairs.jsonl", "data/generated/pool_v3/instances.jsonl"],
              "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                         "adaption-deepseek-v4-flash"]},
    "FOLLOWUP": {"files": ["PREREG_FOLLOWUP.md", "experiments/generate_followup.py", "experiments/run_followup.py",
                           "experiments/chain_followup.sh", "data/followup_v1_manifest.json",
                           "src/msep/models/prompts.py", "src/msep/models/schemas.py", "src/msep/models/runner.py",
                           "src/msep/models/providers/adaption_provider.py", "src/msep/eval/pilot.py",
                           "src/msep/eval/plan_metrics.py", "src/msep/eval/bootstrap.py",
                           "src/msep/benchmark/rendering.py", "src/msep/benchmark/variants.py",
                           "data/generated/followup_v1/clarity.jsonl", "data/generated/followup_v1/cost.jsonl",
                           "data/generated/variants_v3/cost.jsonl", "data/generated/t1_v1/pairs.jsonl",
                           "data/generated/pool_v3/instances.jsonl"],
                 "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema"]},
    "REPAIR": {"files": ["PREREG_REPAIR.md", "experiments/run_repair.py", "experiments/chain_repair.sh",
                         "experiments/generate_robust.py", "experiments/run_eop.py", "data/repair_v1_manifest.json",
                         "src/msep/benchmark/rephrase.py", "src/msep/controllers/extraction_v3.py",
                         "src/msep/controllers/llm_extractor.py", "src/msep/controllers/realistic_planner.py",
                         "src/msep/eval/extraction_match.py", "src/msep/benchmark/parsing.py",
                         "src/msep/models/runner.py", "src/msep/models/providers/adaption_provider.py",
                         "data/generated/repair_v1/items.jsonl", "data/generated/pool_v3/instances.jsonl"],
               "models": ["adaption-gemma-4-26b-a4b-it-schema", "adaption-deepseek-v4-flash"]},
    "ROBUST": {"files": ["PREREG_ROBUST.md", "experiments/run_robust.py", "experiments/generate_robust.py",
                         "experiments/chain_robust.sh", "experiments/run_eop.py",
                         "src/msep/benchmark/rephrase.py", "src/msep/controllers/extraction_v3.py",
                         "src/msep/controllers/llm_extractor.py", "src/msep/controllers/realistic_planner.py",
                         "src/msep/eval/extraction_match.py", "src/msep/benchmark/parsing.py",
                         "src/msep/models/prompts_s1.py", "src/msep/models/prompts.py", "src/msep/models/runner.py",
                         "src/msep/eval/pilot.py", "src/msep/eval/plan_metrics.py", "src/msep/eval/bootstrap.py",
                         "data/generated/robust_v1/items.jsonl", "data/generated/robust_v1/validation.json",
                         "ROBUST_AUDIT.md", "data/robust_v1_validation.json", "data/generated/pool_v3/instances.jsonl"],
               "models": ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema",
                          "adaption-deepseek-v4-flash"]},
}


def _sha(p: str) -> str | None:
    f = ROOT / p
    if not f.exists():  # registrations live in experiments/preregistrations/ in the public release
        f = ROOT / "experiments" / "preregistrations" / Path(p).name
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None


def record(name: str) -> dict:
    spec = PROTOCOLS[name]
    models = json.loads((ROOT / "configs" / "models.json").read_text())
    return {"protocol": name, "commit_at_freeze": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                                         text=True).strip(),
            "files_sha256": {p: _sha(p) for p in spec["files"]},
            "models": {k: {"model_id": models[k]["model_id"], "settings": models[k]["settings"]} for k in spec["models"]}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, choices=sorted(PROTOCOLS))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    path = ROOT / "data" / f"FREEZE_{a.name}.json"
    if a.write:
        if path.exists():
            print(f"{path} exists; refusing to overwrite")
            return 2
        path.write_text(json.dumps(record(a.name), indent=1) + "\n")
        print(f"wrote {path}")
    if a.verify:
        frozen, now = json.loads(path.read_text()), record(a.name)
        bad = [p for p, h in frozen["files_sha256"].items() if now["files_sha256"].get(p) != h or h is None]
        if frozen["models"] != now["models"]:
            bad.append("model settings")
        for b in bad:
            print("FAIL", b)
        print(f"{a.name} FREEZE OK" if not bad else f"{a.name} FREEZE FAILED")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
