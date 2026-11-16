"""Write (or verify) the T1 freeze record: data/FREEZE_T1.json.

    python experiments/freeze_t1.py --write     # once, after generation and validation, before any model call
    python experiments/freeze_t1.py --verify    # data, code, protocol and pilot config against the record

Unlike the v3 verify, every pinned file must exist: a missing T1 file is a failure.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from freeze_benchmark import GENERATOR_FILES, ORACLE_FILES, files_hash, sha

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "data" / "FREEZE_T1.json"
VERSION = "msep-t1-v1"
T1_GENERATOR = ["src/msep/benchmark/t1_flips.py", "experiments/generate_t1.py"]
ANALYSIS = ["experiments/analyze_t1.py", "src/msep/eval/pilot.py", "src/msep/eval/plan_metrics.py",
            "src/msep/models/prompts.py", "src/msep/models/schemas.py", "src/msep/eval/experiments.py"]
DATA = {"pool_v3": "data/generated/pool_v3/instances.jsonl", "t1_pairs": "data/generated/t1_v1/pairs.jsonl",
        "t1_validation": "data/generated/t1_v1/validation.json", "protocol": "PREREG_T1.md"}
PILOT_MODELS = ["adaption-qwen3.5-397b", "adaption-qwen3.8-27b", "adaption-gemma-4-26b-a4b-it-schema"]


def pilot_config() -> dict:
    models = json.loads((ROOT / "configs" / "models.json").read_text())
    return {"split": "dev", "skip_families": 10, "max_families": 20, "mode": "end_to_end",
            "budget_cap_total": 22.6908, "budget_increment": 12.0,
            "models": {k: {"model_id": models[k]["model_id"], "settings": models[k]["settings"]} for k in PILOT_MODELS}}


def record() -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    return {"version": VERSION, "frozen_on": "2026-11-13", "code_commit_at_freeze": commit,
            "t1_generator_sha256": files_hash(T1_GENERATOR + GENERATOR_FILES),
            "oracle_sha256": files_hash(ORACLE_FILES), "analysis_sha256": files_hash(ANALYSIS),
            "t1_generator_files": T1_GENERATOR + GENERATOR_FILES, "oracle_files": ORACLE_FILES,
            "analysis_files": ANALYSIS, "data_sha256": {k: sha(v) for k, v in DATA.items()},
            "seed_scheme": "one edit per base record; rng = Random(int(sha256('t1-v1:' + base_instance_id)))",
            "pilot": pilot_config()}


def verify(rec: dict) -> list[str]:
    p = []
    if files_hash(T1_GENERATOR + GENERATOR_FILES) != rec["t1_generator_sha256"]:
        p.append("T1 generator files changed")
    if files_hash(ORACLE_FILES) != rec["oracle_sha256"]:
        p.append("oracle files changed")
    if files_hash(ANALYSIS) != rec["analysis_sha256"]:
        p.append("analysis files changed")
    for k, h in rec["data_sha256"].items():
        cur = sha(DATA[k])
        if cur is None:
            p.append(f"{k} missing ({DATA[k]})")
        elif cur != h:
            p.append(f"{k} differs from the frozen hash")
    if pilot_config() != rec["pilot"]:
        p.append("pilot models/settings/budget differ from the record")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        if FREEZE.exists():
            print(f"{FREEZE} exists; refusing to overwrite")
            return 2
        FREEZE.write_text(json.dumps(record(), indent=1) + "\n")
        print(f"wrote {FREEZE}")
    if a.verify:
        problems = verify(json.loads(FREEZE.read_text()))
        for x in problems:
            print("FAIL", x)
        print("T1 FREEZE OK" if not problems else "T1 FREEZE FAILED")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
