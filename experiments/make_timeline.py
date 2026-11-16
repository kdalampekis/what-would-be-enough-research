"""Research timeline figure: milestones from the commit history and the registrations. A history figure, not a result.

    python experiments/make_timeline.py            # writes figures/research_timeline.png and .svg
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
# (period, label). Dates are commit or registration dates in UTC; see research/research_decisions.md.
BEFORE = [("2026-11-03", "Literature timeline,\nresearch gap, formal\nproblem, exact oracle"),
          ("2026-11-04", "Shortcut audit:\nbenchmark v2 discarded,\nv3 built and frozen")]
DURING = [("2026-11-13", "First model runs;\nstrong models near\nceiling; counterfactual\npairs registered"),
          ("2026-11-14", "Over-intervention\nfollow-up; EOP as\nregistered fails on\nlayout; amended"),
          ("2026-11-14", "Held-out protocol\nand rewording study\nfrozen"),
          ("2026-11-15", "Held-out and\nrewording results;\nparser baseline"),
          ("2026-11-15/16", "Three follow-up\nstudies: clarity, cost,\nextraction repair"),
          ("2026-11-16", "Final findings\nand report")]


def main() -> int:
    items = [(d, t, "#6b7280") for d, t in BEFORE] + [(d, t, "#1f6feb") for d, t in DURING]
    fig, ax = plt.subplots(figsize=(13, 3.1), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    n = len(items)
    ax.plot([0, n - 1], [0, 0], color="#c9ccd1", lw=2, zorder=1)
    for i, (d, t, c) in enumerate(items):
        ax.scatter([i], [0], s=90, color=c, zorder=3, edgecolor="#fcfcfb", linewidth=2)
        ax.text(i, 0.16, d, ha="center", va="bottom", fontsize=8.5, color="#374151", fontweight="bold")
        ax.text(i, -0.2, t, ha="center", va="top", fontsize=8.3, color="#111827", linespacing=1.25)
    ax.axvline(len(BEFORE) - 0.5, color="#9ca3af", lw=1, ls=(0, (4, 3)))
    ax.text(0.5, 0.62, "Before the sprint (no model called)", ha="center", fontsize=9.5, color="#6b7280", fontweight="bold")
    ax.text(len(BEFORE) + (len(DURING) - 1) / 2, 0.62, "During the sprint, 2026-11-13 to 2026-11-15 (analysis and writing into 2026-11-16 UTC)",
            ha="center", fontsize=9.5, color="#1f6feb", fontweight="bold")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(-0.95, 0.85)
    ax.axis("off")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(ROOT / "figures" / f"research_timeline.{ext}", facecolor=fig.get_facecolor())
    print("wrote figures/research_timeline.png and .svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
