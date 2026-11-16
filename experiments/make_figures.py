"""Figures for the report and the README, drawn from the analysis summaries (no analysis here: plotting only).

    python experiments/make_figures.py --eop results/aggregate/final_test/eop/eop_summary.json --set v3test --label test
    python experiments/make_figures.py --robust results/aggregate/robust_dev/robust_summary.json
Writes PNG (200 dpi) and SVG into figures/.

Encoding: one colour per condition, fixed across all figures, plus a marker shape, so identity never rests on
colour alone. Palette validated for colour-vision deficiency (first three categorical slots, all pairs);
the model-free parser baseline is drawn in neutral grey. Points are rates with 95% family-clustered
bootstrap intervals; the y axis always runs from 0 to 1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
# condition -> (label, colour, marker, filled)
COND = {
    "A": ("A  Native", "#2a78d6", "o", True),
    "B": ("B  Structured prompt", "#eb6834", "s", True),
    "V": ("V  Verifier only", "#eb6834", "s", False),
    "C1": ("C  EOP as registered (prompt v1)", "#1baf7a", "D", False),
    "EOP": ("EOP  Extract + plan", "#1baf7a", "D", True),
    "EOPN": ("EOP-N  Translating prompt", "#1baf7a", "D", False),
    "P": ("P  Parser + planner (no model)", "#7a7974", "X", True),
}
MODELS = {"adaption-qwen3.5-397b": "qwen3.5-397b", "adaption-qwen3.8-27b": "qwen3.8-27b",
          "adaption-deepseek-v4-flash": "deepseek-v4-flash", "adaption-gemma-4-26b-a4b-it-schema": "gemma-4-26b +schema"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "axes.titlesize": 9.5,
                     "axes.titleweight": "bold", "svg.fonttype": "none"})


def _axis(ax, title: str, first: bool) -> None:
    ax.set_title(title, loc="left", color=INK)
    ax.set_ylim(-0.03, 1.06)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    if not first:
        ax.tick_params(labelleft=False)


def _point(ax, x: float, d: dict | None, cond: str, label: str | None = None) -> None:
    """label: None, or where to write the value: "right", "left" or "above"."""
    if not d or d.get("mean") is None:
        return
    _, colour, marker, filled = COND[cond]
    ax.plot([x, x], [d["lo"], d["hi"]], color=colour, linewidth=1.4, solid_capstyle="round", zorder=2)
    ax.plot([x], [d["mean"]], marker=marker, markersize=7.5 if filled else 6.2, color=colour if filled else SURFACE,
            markeredgecolor=colour if not filled else SURFACE, markeredgewidth=1.6 if not filled else 1.2, zorder=3)
    if label:
        xy, ha = {"right": ((7, -3), "left"), "left": ((-7, -3), "right"), "above": ((0, 7), "center")}[label]
        ax.annotate(f"{d['mean']:.2f}", (x, d["mean"]), xytext=xy, textcoords="offset points", fontsize=7.5,
                    color=INK2, ha=ha)


def _legend(fig, conds: list[str]) -> None:
    handles = [plt.Line2D([], [], linestyle="", marker=COND[c][2], markersize=7.5,
                          color=COND[c][1] if COND[c][3] else SURFACE, markeredgecolor=COND[c][1],
                          markeredgewidth=1.6, label=COND[c][0]) for c in conds]
    fig.legend(handles=handles, loc="upper center", ncol=len(conds), frameon=False, bbox_to_anchor=(0.5, 0.955),
               fontsize=8.5, handletextpad=0.3, columnspacing=1.6)


def _save(fig, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out / f"{name}.png")


def _eop_conditions(m: dict, mode: str) -> dict:
    """Map a model's summary to the plotted conditions: EOP is C2 where it was run, else C; B falls back to Bt."""
    c = m[mode]["conditions"]
    e = "C2" if "C2" in c else "C"
    v = {"C2": "D2", "C": "D"}[e]
    # C1: the registered condition C, shown separately only where an amended C' (C2) also exists
    return {"A": c.get("A"), "B": c.get("B") or c.get("Bt"), "V": c.get(v) or c.get("Dt"), "EOP": c.get(e),
            "C1": c.get("C") if e == "C2" else None, "C1_all_failed": e == "C2" and "C" not in c}


def fig_conditions(summary: dict, set_name: str, label: str, out: Path) -> None:
    st = summary[set_name]
    keys = [k for k in MODELS if k in st["models"]]
    fig, axes = plt.subplots(1, len(keys), figsize=(2.55 * len(keys), 3.3), sharey=True)
    all_conds = {k: _eop_conditions(st["models"][k], "detection_controlled") for k in keys}
    show_c1 = any(c["C1"] for c in all_conds.values())
    order = ["A", "B", "V", *(["C1"] if show_c1 else []), "EOP", "P"]
    for ax, k in zip(axes, keys):
        conds = all_conds[k]
        conds["P"] = st["upper_bound_parser_EOP"]["detection_controlled"]
        for i, c in enumerate(order):
            _point(ax, i, (conds[c] or {}).get("optimal_all"), c, label={"A": "left", "EOP": "above"}.get(c))
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(["C" if c == "C1" else c for c in order], fontsize=8)
        ax.set_xlim(-1.15, len(order) - 0.4)
        _axis(ax, MODELS[k], ax is axes[0])
    axes[0].set_ylabel("Optimal-plan rate")
    fig.suptitle(f"Optimal plans by condition ({label} split, {st['families']} families, Detection-Controlled, "
                 f"all attempted)", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    _legend(fig, order)
    fig.subplots_adjust(top=0.78, wspace=0.06)
    _save(fig, out, f"conditions_{label}")


def fig_stopping(summary: dict, v3: str, t1: str | None, label: str, out: Path) -> None:
    panels = [(v3, "end_to_end", "Benchmark states")]
    if t1 and t1 in summary:
        panels.append((t1, "end_to_end", "Counterfactual-pair states"))
    keys = [k for k in MODELS if k in summary[v3]["models"]]
    fig, axes = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 3.1), sharey=True, squeeze=False)
    for ax, (s, mode, title) in zip(axes[0], panels):
        for i, k in enumerate(keys):
            conds = _eop_conditions(summary[s]["models"][k], mode)
            a, e = (conds["A"] or {}).get("stop_ok_AS_NEITHER"), (conds["EOP"] or {}).get("stop_ok_AS_NEITHER")
            if a and e and a.get("mean") is not None and e.get("mean") is not None:
                ax.plot([i - 0.12, i + 0.12], [a["mean"], e["mean"]], color=GRID, linewidth=2, zorder=1)
            _point(ax, i - 0.12, a, "A", label="left")
            _point(ax, i + 0.12, e, "EOP")
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([MODELS[k].replace(" +schema", "").replace("-", "\n", 1) for k in keys], fontsize=8)
        ax.set_xlim(-0.6, len(keys) - 0.4)
        _axis(ax, title, ax is axes[0][0])
    axes[0][0].set_ylabel("Correct stopping rate")
    fig.suptitle(f"Correct stopping on states that need no action or that no action can resolve ({label} split, "
                 f"End-to-End)", x=0.01, ha="left", fontsize=10, fontweight="bold")
    _legend(fig, ["A", "EOP"])
    fig.subplots_adjust(top=0.74, wspace=0.05)
    _save(fig, out, f"stopping_{label}")


def fig_robustness(summary: dict, out: Path) -> None:
    keys = [k for k in MODELS if k in summary["models"]]
    kinds = ["canonical", "lexical", "syntax", "reorder", "prose"]
    order = ["A", "B", "EOP", "EOPN", "P"]
    offs = {c: (i - 2) * 0.16 for i, c in enumerate(order)}
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 6.2), sharey=True, sharex=True)
    for ax, k in zip(axes.flat, keys):
        m = summary["models"][k]
        for j, kind in enumerate(kinds):
            src = m["canonical"] if kind == "canonical" else m["kinds"][kind]["conditions"]
            for c in order:
                if kind == "canonical" and c == "EOPN":
                    continue
                _point(ax, j + offs[c], (src.get(c) or {}).get("optimal_all"), c)
            if j:
                ax.axvline(j - 0.5, color=GRID, linewidth=0.8)
        ax.set_xticks(range(len(kinds)))
        ax.set_xticklabels(["Canonical", "Lexical", "Syntax", "Reorder", "Prose"])
        ax.set_xlim(-0.55, len(kinds) - 0.45)
        _axis(ax, MODELS[k], ax in axes[:, 0])
    for ax in axes[:, 0]:
        ax.set_ylabel("Optimal-plan rate")
    fig.suptitle(f"The same {summary['base_items']} states, reworded four ways (dev, {summary['families']} families, "
                 f"End-to-End, all attempted)", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    _legend(fig, order)
    fig.subplots_adjust(top=0.87, wspace=0.04, hspace=0.22)
    _save(fig, out, "robustness")


def fig_extraction(summary: dict, out: Path) -> None:
    """Share of extracted states exactly equal to the true state, by wording."""
    keys = [k for k in MODELS if k in summary["models"]]
    kinds = ["canonical", "lexical", "syntax", "reorder", "prose"]
    fig, axes = plt.subplots(1, len(keys), figsize=(2.55 * len(keys), 3.0), sharey=True)
    for ax, k in zip(axes, keys):
        m = summary["models"][k]
        for j, kind in enumerate(kinds):
            if kind == "canonical":
                _point(ax, j, m["canonical"]["EOP_extraction"]["exact"], "EOP")
            else:
                _point(ax, j - 0.13, m["kinds"][kind]["extraction"]["EOP"]["exact"], "EOP")
                _point(ax, j + 0.13, m["kinds"][kind]["extraction"]["EOPN"]["exact"], "EOPN")
            _point(ax, j + (0.0 if kind == "canonical" else 0.0) + 0.36,
                   summary["parser_P"][kind].get("state_exact") or {"mean": 1.0, "lo": 1.0, "hi": 1.0}, "P")
        ax.set_xticks(range(len(kinds)))
        ax.set_xticklabels(["Canonical", "Lexical", "Syntax", "Reorder", "Prose"], fontsize=7.5, rotation=35, ha="right",
                           rotation_mode="anchor")
        ax.set_xlim(-0.5, len(kinds) - 0.2)
        _axis(ax, MODELS[k], ax is axes[0])
    axes[0].set_ylabel("Extracted state exactly right")
    fig.suptitle("Does the extracted formal state equal the true state? (dev, by wording)", x=0.01, ha="left",
                 fontsize=10.5, fontweight="bold")
    _legend(fig, ["EOP", "EOPN", "P"])
    fig.subplots_adjust(top=0.76, wspace=0.06)
    _save(fig, out, "extraction")


def fig_architecture(out: Path) -> None:
    """How the conditions differ, and where the evaluation oracle sits (it never feeds the controller)."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(10.4, 4.5))
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 45)
    ax.axis("off")
    blue, orange, green, grey = COND["A"][1], COND["B"][1], COND["EOP"][1], COND["P"][1]

    def box(x, y, w, h, text, edge=INK2, fill=SURFACE, size=8.2, weight="normal"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.1", linewidth=1.1,
                                    edgecolor=edge, facecolor=fill))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK, fontweight=weight,
                linespacing=1.25)

    def arrow(x1, y1, x2, y2, colour=INK2, style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=9, linewidth=1.2,
                                     color=colour, linestyle=ls, shrinkA=0, shrinkB=0))

    # controller lane
    ax.text(0.5, 43.4, "What the agent sees and does", fontsize=9.5, fontweight="bold", color=INK)
    box(0.5, 27, 15, 12, "Problem text\n(rules, known\nvalues, priced\nactions)", fill="#f1f0ec")
    box(22, 35.5, 26, 5.2, "A  Native: the model answers", edge=blue)
    box(22, 28.6, 26, 5.2, "B  Structured prompt: the model lists\nobligations first, then answers", edge=orange, size=7.4)
    box(22, 19.2, 17, 7.4, "EOP: the model only\nextracts the state\n(JSON)", edge=green)
    box(22, 12.2, 17, 5.2, "P  Parser (no model)", edge=grey)
    box(45, 13.2, 14, 12.4, "Formal state\nas extracted", fill="#f1f0ec")
    box(64, 13.2, 20, 12.4, "Exact planner\n1. Is Q already decided?\n2. List obligations\n3. Cheapest set of actions\n   that covers them", edge=green, size=7.8)
    box(89, 27, 14.5, 12, "Plan\n(or stop,\nor defer)", fill="#f1f0ec", weight="bold")
    for y in (38.1, 31.2):
        arrow(15.9, 33, 21.6, y)
        arrow(48.4, y, 88.6, 34.5 if y > 35 else 32.5)
    arrow(15.9, 30, 21.6, 22.9)
    arrow(15.9, 28.5, 21.6, 14.8)
    arrow(39.4, 22.9, 44.6, 21)
    arrow(39.4, 14.8, 44.6, 17)
    arrow(59.4, 19.4, 63.6, 19.4)
    arrow(84.4, 19.4, 95, 26.6)
    # oracle lane
    ax.plot([0.5, 103.5], [9.6, 9.6], color=GRID, linewidth=1.2)
    ax.text(0.5, 7.4, "How answers are scored (never visible to the agent or the planner)", fontsize=9.5,
            fontweight="bold", color=INK)
    box(0.5, 0.4, 20, 5.4, "True formal state\n(from the generator)", fill="#f1f0ec", size=7.8)
    box(27, 0.4, 30, 5.4, "Exact oracle: SAT / MaxSAT,\nre-verified by brute force", size=7.8)
    box(63, 0.4, 21, 5.4, "Labels: class, all\noptimal plans, cost", fill="#f1f0ec", size=7.8)
    box(89, 0.4, 14.5, 5.4, "Score", weight="bold")
    arrow(20.9, 3.1, 26.6, 3.1)
    arrow(57.4, 3.1, 62.6, 3.1)
    arrow(84.4, 3.1, 88.6, 3.1)
    arrow(96.2, 26.6, 96.2, 6.2, ls=(0, (4, 3)))
    _save(fig, out, "architecture")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eop", help="eop_summary.json")
    ap.add_argument("--set", default="v3test", help="item set for the conditions figure (v3dev or v3test)")
    ap.add_argument("--t1-set", default=None, help="T1 item set for the stopping figure (t1b or t1test)")
    ap.add_argument("--label", default="test")
    ap.add_argument("--robust", help="robust_summary.json")
    ap.add_argument("--architecture", action="store_true", help="draw the conditions-and-oracle diagram")
    ap.add_argument("--out", default=str(ROOT / "figures"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.eop:
        s = json.load(open(a.eop))
        fig_conditions(s, a.set, a.label, out)
        fig_stopping(s, a.set, a.t1_set, a.label, out)
    if a.architecture:
        fig_architecture(out)
    if a.robust:
        s = json.load(open(a.robust))
        fig_robustness(s, out)
        fig_extraction(s, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
