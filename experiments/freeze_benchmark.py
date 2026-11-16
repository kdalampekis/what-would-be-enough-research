"""Write (or verify) the benchmark freeze record: data/FREEZE_v3.json.

    python experiments/freeze_benchmark.py --write     # create the record (once, at freeze time)
    python experiments/freeze_benchmark.py --verify    # check code, data and splits against it

The record pins everything that determines benchmark content: the commit, a hash of
every source file the generator and oracle depend on, the dataset hashes, the seed
scheme and every family's split. After the freeze, any change to those files must be
an objective bug fix, recorded in BENCHMARK_CHANGELOG.md, with a new record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import pysat

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "data" / "FREEZE_v3.json"
BENCHMARK_VERSION = "msep-benchmark-v3.0"

GENERATOR_FILES = [
    "src/msep/benchmark/template_v3.py", "src/msep/benchmark/families.py", "src/msep/benchmark/rendering.py",
    "src/msep/benchmark/schemas.py", "src/msep/benchmark/splits.py", "src/msep/benchmark/variants.py",
    "src/msep/benchmark/counterfactuals.py", "src/msep/world/state.py", "src/msep/world/constraints.py",
    "src/msep/world/certified_tasks.py", "src/msep/world/compute_tasks.py", "src/msep/world/probabilities.py",
    "src/msep/actions/base.py", "src/msep/actions/information.py", "src/msep/actions/computation.py",
    "experiments/generate_benchmark.py", "experiments/generate_variants.py",
]
ORACLE_FILES = [
    "src/msep/oracle/brute_force.py", "src/msep/oracle/logic.py", "src/msep/oracle/solver.py",
    "src/msep/oracle/probability.py", "src/msep/oracle/sufficiency.py", "src/msep/oracle/minimal_plan.py",
    "src/msep/obligations/model.py", "src/msep/obligations/extraction.py", "src/msep/obligations/discharge.py",
]
DATA = {
    "pool_v3": "data/generated/pool_v3/instances.jsonl",
    "variants_v3_cost": "data/generated/variants_v3/cost.jsonl",
    "variants_v3_risk": "data/generated/variants_v3/risk.jsonl",
    "variants_v3_shift": "data/generated/variants_v3/shift.jsonl",
    "pool_v2_shallow_subset": "data/generated/pool_v2/instances.jsonl",
    "variants_v2_cost": "data/generated/variants_v2/cost.jsonl",
    "variants_v2_risk": "data/generated/variants_v2/risk.jsonl",
    "variants_v2_shift": "data/generated/variants_v2/shift.jsonl",
}


def files_hash(paths: list[str]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.encode() + b"\0" + (ROOT / p).read_bytes() + b"\0")
    return h.hexdigest()


def sha(path: str) -> str | None:
    f = ROOT / path
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None


def splits(path: str) -> dict[str, str]:
    out = {}
    for line in open(ROOT / path):
        r = json.loads(line)
        out[r["family_id"]] = r["split"]
    return out


def record() -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sp = splits(DATA["pool_v3"])
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "frozen_on": "2026-11-04",
        "code_commit_at_freeze": commit,
        "generator_files_sha256": files_hash(GENERATOR_FILES),
        "oracle_files_sha256": files_hash(ORACLE_FILES),
        "generator_files": GENERATOR_FILES,
        "oracle_files": ORACLE_FILES,
        "python": platform.python_version(),
        "pysat": pysat.__version__,
        "datasets_sha256": {k: sha(v) for k, v in DATA.items()},
        "seed_scheme": {
            "families": "seeds 0..299 for both pools",
            "template_v3": "theory and state draws: random.Random(f'v3:{seed}:{attempt}')",
            "template_v2": "random.Random(f'{seed}:{attempt}')",
            "rendering": "random.Random(f'render:{seed}'); v3 shuffles rules with the stored order_seed",
            "family_id": "'G' (v3) or 'F' (v2) + sha256('msep-family-{seed}')[:10]",
            "split": "benchmark/splits.py split_of(family_id), salt 'msep-split-v1', 60/20/20",
        },
        "split_counts": {s: sum(1 for v in sp.values() if v == s) for s in ("train", "dev", "test")},
        "split_assignment_v3": dict(sorted(sp.items())),
        "rules": [
            "The test split is used once, for the frozen final evaluation.",
            "No change to generator or oracle files except objective bug fixes, each recorded in BENCHMARK_CHANGELOG.md "
            "with a new freeze record; never a change made to raise or lower model scores.",
        ],
    }


def verify(rec: dict) -> list[str]:
    problems = []
    if files_hash(GENERATOR_FILES) != rec["generator_files_sha256"]:
        problems.append("generator source files changed since the freeze")
    if files_hash(ORACLE_FILES) != rec["oracle_files_sha256"]:
        problems.append("oracle source files changed since the freeze")
    for k, h in rec["datasets_sha256"].items():
        cur = sha(DATA[k])
        if cur is not None and cur != h:
            problems.append(f"dataset {k} differs from the frozen hash")
    if (ROOT / DATA["pool_v3"]).exists() and splits(DATA["pool_v3"]) != rec["split_assignment_v3"]:
        problems.append("split assignment differs")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.write:
        FREEZE.write_text(json.dumps(record(), indent=1))
        print(f"wrote {FREEZE}")
    rec = json.loads(FREEZE.read_text())
    problems = verify(rec)
    print("FREEZE OK" if not problems else "FREEZE VIOLATED: " + "; ".join(problems))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
