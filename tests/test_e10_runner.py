"""E10 (cost sweeps) through the real pilot driver, with a SYNTHETIC mock agent. No network."""

import json
import sys
from pathlib import Path

from msep.benchmark import variants

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from run_pilot import main  # noqa: E402
from test_pilot_pipeline import make_records  # noqa: E402


def _data(tmp_path, n=3):
    recs = make_records(n)
    data = tmp_path / "d.jsonl"
    data.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    vdir = tmp_path / "variants"
    vdir.mkdir()
    cost = [v for r in recs for v in variants.cost_sweep(r)]
    (vdir / "cost.jsonl").write_text("\n".join(json.dumps(v) for v in cost) + "\n")
    return data, vdir, cost


def _run(tmp_path, data, vdir, *extra):
    return main(["--data", str(data), "--splits", "dev", "--max-families", "3", "--experiments", "e10",
                 "--variants", str(vdir), "--dry-run-mock", "oracle_perfect", "--models", "adaption-qwen3.5-397b",
                 "--raw", str(tmp_path / "raw"), "--out", str(tmp_path / "out"), *extra])


def test_e10_requires_variants(tmp_path, capsys):
    data, _, _ = _data(tmp_path)
    rc = main(["--data", str(data), "--splits", "dev", "--max-families", "3", "--experiments", "e10", "--dry-run"])
    assert rc == 2 and "needs --variants" in capsys.readouterr().out


def test_e10_runs_and_is_reported_with_flip_items_separate(tmp_path, capsys):
    data, vdir, cost = _data(tmp_path)
    assert any(v["variant"]["relation"] == "below" for v in cost)  # the fixture has flip items
    assert _run(tmp_path, data, vdir) == 0
    s = json.loads(next((tmp_path / "out" / "dryrun").rglob("summary.json")).read_text())
    e10 = s["by_model"]["dryrun-adaption-qwen3.5-397b"]["E10"]["detection_controlled"]
    assert e10["n"] > 0 and e10["optimal_rate"]["mean"] == 1
    assert e10["optimal_rate_by_relation"]["below"]["mean"] == 1 and e10["optimal_rate_by_relation"]["below"]["n"] > 0
    assert "Optimal: below (flip items)" in next((tmp_path / "out" / "dryrun").rglob("report.md")).read_text()


def test_e10_flip_selects_only_below_items(tmp_path, capsys):
    data, vdir, cost = _data(tmp_path)
    assert _run(tmp_path, data, vdir, "--e10-items", "flip") == 0
    n_below = sum(v["variant"]["relation"] == "below" for v in cost)
    assert f"E10 cost variants (flip): {n_below} items" in capsys.readouterr().out
    s = json.loads(next((tmp_path / "out" / "dryrun").rglob("summary.json")).read_text())
    byr = s["by_model"]["dryrun-adaption-qwen3.5-397b"]["E10"]["detection_controlled"]["optimal_rate_by_relation"]
    assert byr["equal"]["n"] == 0 and byr["above"]["n"] == 0
