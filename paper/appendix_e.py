"""Assemble the body of Appendix E (extended results) from the generated result files. Copying only: no analysis.

    python paper/appendix_e.py > appendix_e.md
    python paper/appendix_e.py --test DIR --robust DIR      # other locations
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

AGG = Path(__file__).resolve().parents[1] / "results" / "aggregate"
# sections of the generated held-out report that go into the appendix, in order
V3 = ["Plan sufficiency by mode", "Diagnosis vs planning", "E3 ", "E7 ", "E5 ", "E1, E2", "Mode decomposition",
      "Confirmatory tests", "Usage"]


def sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    return {p.split("\n", 1)[0]: p.split("\n", 1)[1] for p in parts}


def clean(body: str) -> str:
    # dropped: figure links, mock rows, and the raw dump of the F1 p-values (they are in the main-text table)
    body = "\n".join(l for l in body.splitlines()
                     if not l.startswith(("![", "| mock-", "**confirmatory")))
    body = re.sub(r"^#+ ", "**", body, flags=re.M)  # sub-headings inside a section become bold lines
    body = re.sub(r"^(\*\*[^\n|]*[^*\n])$", r"\1**", body, flags=re.M)
    # a bootstrap p-value printed as 0.0 means none of the 10,000 resamples reached zero (run_eop.one_sided_p)
    body = re.sub(r"\bp 0\.0(?=[,;])", "p < 0.0001", body)
    return body.replace("adaption-", "").strip()


def block(title: str, body: str) -> list[str]:
    return [f"#### {title.replace('adaption-', '')}", "", clean(body), ""]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default=str(AGG / "final_test"))
    ap.add_argument("--robust", default=str(AGG / "robust_dev"))
    a = ap.parse_args(argv)
    test, out = Path(a.test), []
    v3 = sections((test / "v3" / "pilot_test" / "report.md").read_text())
    out += ["### E.1 Held-out test split: the registered measures", ""]
    for want in V3:
        for title, body in v3.items():
            if title.startswith(want):
                if want == "Confirmatory tests":  # the registered tests concern the four models; baseline rows are left out
                    body = "\n".join(l for l in body.splitlines() if not l.startswith(("| heuristic-", "| policy-")))
                out += block(title, body)
    out += ["### E.2 Held-out test split: conditions on every item set", ""]
    out += ["Tables only. Extraction failure counts and pair-level accuracy are in "
            "`results/aggregate/final_test/eop/eop_tables.md`.", ""]
    for title, body in sections((test / "eop" / "eop_tables.md").read_text()).items():
        out += block(title, "\n".join(l for l in body.splitlines() if not l.strip() or l[0] in "|#"))
    rb = (Path(a.robust) / "robust_report.md").read_text()
    out += ["### E.3 Rewording study", "", clean(rb.split("\n", 1)[1].split("\n## ", 1)[0]), ""]
    for title, body in sections(rb).items():
        out += block(title, body)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
