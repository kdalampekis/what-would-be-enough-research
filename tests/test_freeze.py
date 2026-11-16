"""The v3 benchmark is frozen: generator/oracle code, data and splits must match data/FREEZE_v3.json.

If this fails after an objective bug fix: record the fix in BENCHMARK_CHANGELOG.md and
write a new freeze record (experiments/freeze_benchmark.py --write). Never to change scores."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from freeze_benchmark import FREEZE, verify  # noqa: E402

from msep.benchmark.splits import split_of  # noqa: E402


def test_freeze_record_holds():
    rec = json.loads(FREEZE.read_text())
    assert verify(rec) == []


def test_split_function_reproduces_frozen_assignment():
    rec = json.loads(FREEZE.read_text())
    assert all(split_of(f) == s for f, s in rec["split_assignment_v3"].items())
    assert rec["split_counts"] == {"train": 165, "dev": 72, "test": 63}
