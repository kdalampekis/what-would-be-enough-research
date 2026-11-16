"""Rebuild report.md and figures from a saved summary.json (no recomputation, no model calls).

    python experiments/make_report.py --summary results/synthetic/summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from msep.eval.report import write_report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", default=None, help="defaults to the summary's directory")
    ap.add_argument("--title", default=None)
    a = ap.parse_args()
    s = json.loads(Path(a.summary).read_text())
    out = Path(a.out) if a.out else Path(a.summary).parent
    write_report(s, out, title=a.title or ("SYNTHETIC offline run (mock agents)" if "SYNTHETIC" in s else "Model results"))
    print(f"wrote {out / 'report.md'}")


if __name__ == "__main__":
    main()
