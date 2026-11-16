"""Markdown report and figures, generated only from a summary JSON (never by hand).

Figures: matplotlib PNG, light surface. Series colours are categorical slots 1-3 of
the default validated palette (checked with the palette validator: all checks pass;
slot 3 is below 3:1 contrast, so every figure has a table with the same numbers).
"""

from __future__ import annotations

from pathlib import Path

MODE_COLORS = {"end_to_end": "#2a78d6", "detection_controlled": "#eb6834", "diagnosis_controlled": "#1baf7a"}
MODE_LABEL = {"end_to_end": "End-to-End", "detection_controlled": "Detection-Controlled",
              "diagnosis_controlled": "Diagnosis-Controlled"}
SURFACE = "#fcfcfb"
INK = "#2b2b29"
MUTED = "#6b6b66"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

SYNTHETIC_BANNER = ("> **SYNTHETIC.** These numbers come from deterministic mock agents used as test fixtures. "
                    "They test the pipeline and say nothing about any language model.")


def _ci(c):
    if not isinstance(c, dict):
        return None, None, None
    m = c.get("mean", c.get("value"))
    return m, c.get("lo"), c.get("hi")


def fmt(c) -> str:
    m, lo, hi = _ci(c)
    if m is None:
        return "–"
    return f"{m:.2f}" if lo is None else f"{m:.2f} [{lo:.2f}, {hi:.2f}]"


def num(x) -> str:
    return "–" if x is None else (f"{x:.2f}" if isinstance(x, float) else str(x))


# -- figures ---------------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
                         "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "axes.axisbelow": True})
    return plt


def grouped_bars(path: Path, title: str, models: list[str], series: dict[str, dict[str, dict]], ylabel: str):
    """series: mode -> model -> ci dict. One bar group per model, one bar per mode."""
    plt = _plt()
    import numpy as np
    modes = [m for m in MODE_COLORS if m in series]
    fig, ax = plt.subplots(figsize=(max(5.5, 0.9 * len(models) + 2), 3.4))
    width = 0.8 / max(1, len(modes))
    x = np.arange(len(models))
    for k, mode in enumerate(modes):
        vals, err_lo, err_hi = [], [], []
        for mdl in models:
            m, lo, hi = _ci(series[mode].get(mdl))
            vals.append(m if m is not None else 0)
            err_lo.append((m - lo) if (m is not None and lo is not None) else 0)
            err_hi.append((hi - m) if (m is not None and hi is not None) else 0)
        ax.bar(x + (k - (len(modes) - 1) / 2) * width, vals, width * 0.92, color=MODE_COLORS[mode],
               label=MODE_LABEL[mode], yerr=[err_lo, err_hi], error_kw={"ecolor": INK, "elinewidth": 0.8, "capsize": 2})
    ax.set_xticks(x, [m.replace("mock-", "") for m in models], rotation=30, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, ncol=len(modes), loc="upper left", bbox_to_anchor=(0, -0.32))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def confusion_grid(path: Path, title: str, mats: dict[str, dict]):
    plt = _plt()
    import numpy as np
    labels = ["INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER"]
    short = ["INFO", "COMP", "BOTH", "NEITHER"]
    cols_lab = labels + ["ALREADY_SUFFICIENT", "INVALID"]
    n = len(mats)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.4 * ncols, 2.9 * nrows), squeeze=False)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("seq", [SURFACE] + SEQ)
    for ax, (name, m) in zip(axes.flat, mats.items()):
        arr = np.array([[m.get(g, {}).get(p, 0) for p in cols_lab] for g in labels], dtype=float)
        rows = arr.sum(axis=1, keepdims=True)
        frac = np.divide(arr, rows, out=np.zeros_like(arr), where=rows > 0)
        ax.imshow(frac, cmap=cmap, vmin=0, vmax=1)
        for i in range(len(labels)):
            for j in range(len(cols_lab)):
                ax.text(j, i, f"{frac[i, j]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if frac[i, j] > 0.55 else INK)
        ax.set_xticks(range(len(cols_lab)), short + ["ALREADY", "INVALID"], rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(labels)), short, fontsize=7)
        ax.set_title(name.replace("mock-", ""), fontsize=9)
        ax.grid(False)
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.suptitle(title, x=0.01, ha="left", fontsize=10)
    fig.supxlabel("predicted", fontsize=8)
    fig.supylabel("gold", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def shift_dots(path: Path, title: str, data: dict[str, dict[str, tuple]]):
    """data: axis -> model -> (in-distribution, shifted). Paired dots joined by a line."""
    plt = _plt()
    axes_names = [a for a in ("width", "depth", "skin") if a in data]
    fig, axs = plt.subplots(1, len(axes_names), figsize=(4.0 * len(axes_names), 3.2), squeeze=False, sharey=True)
    for ax, axis in zip(axs[0], axes_names):
        groups: dict[float, list[str]] = {}
        for mdl, (a, b) in data[axis].items():
            if a is None or b is None:
                continue
            # one colour: position on x already says in-distribution vs shifted
            ax.plot([0, 1], [a, b], color=MUTED, linewidth=1)
            ax.scatter([0, 1], [a, b], color=MODE_COLORS["end_to_end"], s=36, zorder=3, edgecolor=SURFACE, linewidth=1.5)
            groups.setdefault(round(b, 2), []).append(mdl.replace("mock-", ""))
        # one label per distinct end value, names joined, nudged apart when values are close
        last = None
        for y in sorted(groups):
            ty = y if last is None or y - last >= 0.06 else last + 0.06
            ax.annotate(", ".join(groups[y]), (1.04, ty), fontsize=6.5, va="center", color=MUTED)
            last = ty
        ax.set_xticks([0, 1], ["in-distribution", "shifted"])
        ax.set_xlim(-0.2, 2.9)
        ax.set_ylim(-0.05, 1.05)
        ax.set_title(axis, fontsize=9)
    axs[0][0].set_ylabel("plan sufficient (Detection-Controlled)")
    fig.suptitle(title, x=0.01, ha="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# -- report ------------------------------------------------------------------------------------

def write_report(summary: dict, out: Path, title: str) -> None:
    out = Path(out)
    figs = out / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    models = list(summary["by_model"])
    S = summary["by_model"]
    synthetic = any(S[m].get("synthetic") for m in models) or "SYNTHETIC" in summary
    if any(m.startswith("heuristic-") for m in models):
        L_note = ("> `heuristic-*` rows are real deterministic baselines (no language model, text only); `policy-*` rows "
                  "are fixed visible-only intervention policies (always answer / ask everything / compute everything / "
                  "abstain). "
                  "`mock-*` rows are synthetic fixtures.")
    else:
        L_note = None
    L = [f"# {title}", ""]
    if synthetic:
        L += [SYNTHETIC_BANNER, ""]
    if L_note:
        L += [L_note, ""]
    L += [f"Split(s): {', '.join(summary.get('splits', []))} · families: {summary.get('families')} · "
          f"generated from `summary.json` by `msep.eval.report`.", "",
          "Every number names its mode. End-to-End mixes detection with planning and is never read as a "
          "planning failure. Intervals are 95% family-clustered bootstrap.", ""]
    if summary.get("agent_descriptions"):
        L += ["## Agents", ""] + [f"- `{k}`: {v}" for k, v in summary["agent_descriptions"].items()] + [""]

    # Figure 1: plan sufficiency by mode
    series = {"end_to_end": {}, "detection_controlled": {}, "diagnosis_controlled": {}}
    psm = {m: S[m].get("plan_sufficiency_by_mode") for m in models}
    for m in models:
        s = S[m]
        if psm[m]:  # same basis in every mode: all answers, unparsed = failure
            for mode in series:
                series[mode][m] = psm[m][mode]["all_answers"]
        else:  # summaries written before plan_sufficiency_by_mode existed
            if "E3" in s:
                series["end_to_end"][m] = s["E3"]["end_to_end"]["h2_plan_sufficient"]
                series["detection_controlled"][m] = s["E3"]["detection_controlled"]["h2_plan_sufficient"]
            if "E6" in s:
                series["diagnosis_controlled"][m] = s["E6"]["diagnosis_controlled"]["plan_sufficient"]
    grouped_bars(figs / "plan_sufficiency_by_mode.png", "Plan sufficiency on resolvable states, by mode (all answers)",
                 models, series, "plan sufficient")
    L += ["## Plan sufficiency by mode (resolvable states)", "", "![](figures/plan_sufficiency_by_mode.png)", "",
          "Two bases, the same in every mode. **All answers:** an unparsed or truncated answer counts as a failure. "
          "**Parsed only:** unparsed answers are left out; the number left out is shown as `unparsed/n`. A gap between "
          "the two means output-format or truncation failures, not planning failures.", "",
          "| Agent / model | E2E all | E2E parsed | DC all | DC parsed | DxC all | DxC parsed | unparsed/n (E2E, DC, DxC) |",
          "|---|---|---|---|---|---|---|---|"]
    for m in models:
        if psm[m]:
            p = psm[m]
            L.append(f"| {m} | " + " | ".join(f"{fmt(p[md]['all_answers'])} | {fmt(p[md]['parsed_only'])}"
                                             for md in ("end_to_end", "detection_controlled", "diagnosis_controlled"))
                     + " | " + ", ".join(f"{p[md]['unparsed']}/{p[md]['n']}"
                                         for md in ("end_to_end", "detection_controlled", "diagnosis_controlled")) + " |")
        else:
            L.append(f"| {m} | {fmt(series['end_to_end'].get(m))} | – | {fmt(series['detection_controlled'].get(m))} | – | "
                     f"{fmt(series['diagnosis_controlled'].get(m))} (parsed only) | – | – |")

    # Figure 2: diagnosis vs planning (H2), Detection-Controlled
    diag = {"detection_controlled": {m: S[m]["E3"]["detection_controlled"]["h2_class_correct"] for m in models if "E3" in S[m]}}
    L += ["", "## Diagnosis vs planning (H2), Detection-Controlled", "",
          "| Agent / model | Class correct | Plan sufficient | Plan sufficient given class correct | McNemar p |",
          "|---|---|---|---|---|"]
    for m in models:
        if "E3" in S[m]:
            r = S[m]["E3"]["detection_controlled"]
            L.append(f"| {m} | {fmt(r['h2_class_correct'])} | {fmt(r['h2_plan_sufficient'])} | "
                     f"{fmt(r['h2_plan_sufficient_given_class_correct'])} | {r['h2_mcnemar']['p_value']:.3g} |")

    # E3 diagnosis + surface baseline
    L += ["", "## E3 Resource diagnosis", "", "| Agent / model | Mode | Accuracy | Macro-F1 | Balanced acc. | Surface-feature baseline (all counts) |",
          "|---|---|---|---|---|---|"]
    for m in models:
        if "E3" not in S[m]:
            continue
        base = S[m]["E3"].get("surface_feature_baseline", {}).get("all_counts", {}).get("probe_accuracy")
        for mode in ("detection_controlled", "end_to_end"):
            r = S[m]["E3"][mode]
            L.append(f"| {m} | {MODE_LABEL[mode]} | {fmt(r['accuracy'])} | {fmt(r['macro_f1'])} | "
                     f"{fmt(r['balanced_accuracy'])} | {num(base)} |")
    mats = {m: S[m]["E3"]["detection_controlled"]["confusion"] for m in models if "E3" in S[m]}
    if mats:
        confusion_grid(figs / "confusion_detection_controlled.png", "Resource-class confusion, Detection-Controlled", mats)
        L += ["", "![](figures/confusion_detection_controlled.png)"]

    # E7
    e7 = {m: S[m]["E7"]["detection_controlled"]["per_class"] for m in models if "E7" in S[m]}
    if e7:
        grouped = {"detection_controlled": {}}
        L += ["", "## E7 BOTH vs single-resource (Detection-Controlled)", "",
              "| Agent / model | INFORMATION_ONLY | COMPUTATION_ONLY | BOTH | BOTH plans using one resource |", "|---|---|---|---|---|"]
        for m, pc in e7.items():
            r = S[m]["E7"]["detection_controlled"]
            L.append(f"| {m} | {fmt(pc['INFORMATION_ONLY']['plan_sufficient'])} | {fmt(pc['COMPUTATION_ONLY']['plan_sufficient'])} | "
                     f"{fmt(pc['BOTH']['plan_sufficient'])} | {fmt(r['both_single_resource_plans'])} |")

    # E5
    L += ["", "## E5 Relevance vs sufficiency (judgments)", "",
          "| Agent / model | Accuracy, sufficient plans | Accuracy, relevant-insufficient plans | Pairs both correct | McNemar p |",
          "|---|---|---|---|---|"]
    for m in models:
        if "E5" in S[m]:
            j = S[m]["E5"]["a_judgment"]
            L.append(f"| {m} | {fmt(j['accuracy_sufficient_candidates'])} | {fmt(j['accuracy_relevant_insufficient_candidates'])} | "
                     f"{fmt(j['pair_both_correct'])} | {j['mcnemar']['p_value']:.3g} |")

    # E1, E2, E4, E6, E8, E9 compact
    L += ["", "## E1, E2, E4, E6, E8, E9", "",
          "| Agent / model | E1 base decision acc. | E2 detection acc. (E2E) | E2 over-answering | E4 exact match (DxC) | "
          "E6 optimal given sufficient (DC) | E8 correct defer (DC) | E9 premature stop (DC) | E9 continued after ex-post sufficiency (DC; compare with oracle) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m in models:
        s = S[m]
        L.append("| " + " | ".join([
            m,
            fmt(s.get("E1", {}).get("a_base_decision_accuracy")),
            fmt(s.get("E2", {}).get("detection_accuracy")),
            fmt(s.get("E2", {}).get("over_answering")),
            fmt(s.get("E4", {}).get("diagnosis_controlled", {}).get("exact_match")),
            fmt(s.get("E6", {}).get("detection_controlled", {}).get("optimal_given_sufficient")),
            fmt(s.get("E8", {}).get("detection_controlled", {}).get("correct_defer")),
            fmt(s.get("E9", {}).get("detection_controlled", {}).get("premature_stop")),
            fmt(s.get("E9", {}).get("detection_controlled", {}).get("continued_after_expost_sufficiency")),
        ]) + " |")

    # E10, E11
    if any("E10" in S[m] for m in models):
        L += ["", "## E10 Cost sensitivity (Detection-Controlled)", "",
              "Oracle expectation: the swept action is chosen when it is cheaper than its rival, not when dearer.", "",
              "Only 'below' items change which plan is cheapest relative to the base item; a cost-blind policy "
              "that keeps the base plan scores 1 on 'equal'/'above' and 0 on 'below'.", "",
              "| Agent / model | Optimal rate (pooled) | Optimal: below (flip items) | Optimal: equal | Optimal: above | "
              "Chose swept action: below / equal / above | Sweeps optimal at every cost |", "|---|---|---|---|---|---|---|"]
        for m in models:
            if "E10" in S[m]:
                r = S[m]["E10"]["detection_controlled"]
                rel = r["chose_swept_action_by_cost_relation"]
                byr = r.get("optimal_rate_by_relation", {})
                L.append(f"| {m} | {fmt(r['optimal_rate'])} | {fmt(byr.get('below'))} | {fmt(byr.get('equal'))} | "
                         f"{fmt(byr.get('above'))} | {num(rel.get('below'))} / {num(rel.get('equal'))} / "
                         f"{num(rel.get('above'))} | {num(r['sweeps_optimal_at_every_cost'])} |")
    if any("E11" in S[m] for m in models):
        L += ["", "## E11 Risk sensitivity (End-to-End; posterior-threshold stress test, not core benchmark)", "",
              "| Agent / model | tau | Oracle: answering justified | Agent answers | Detection correct |", "|---|---|---|---|---|"]
        for m in models:
            for tau, r in S[m].get("E11", {}).get("end_to_end", {}).items():
                L.append(f"| {m} | {tau} | {num(r['oracle_answer_justified_rate'])} | {num(r['model_answers_rate'])} | "
                         f"{num(r['detection_correct'])} |")

    # E12
    if any("E12" in S[m] for m in models):
        data = {}
        L += ["", "## E12 Structural shift (Detection-Controlled, resolvable states)", "",
              "| Agent / model | Axis | Pairs | In-distribution plan sufficient | Shifted | Paired drop [CI] | McNemar p |",
              "|---|---|---|---|---|---|---|"]
        for m in models:
            for axis, r in S[m].get("E12", {}).get("detection_controlled", {}).items():
                data.setdefault(axis, {})[m] = (r["in_distribution_plan_sufficient"], r["shifted_plan_sufficient"])
                L.append(f"| {m} | {axis} | {r['pairs']} | {num(r['in_distribution_plan_sufficient'])} | "
                         f"{num(r['shifted_plan_sufficient'])} | {fmt(r['paired_drop_plan_sufficient'])} | "
                         f"{r['mcnemar_plan_sufficient']['p_value']:.3g} |")
        if data:
            shift_dots(figs / "shift_detection_controlled.png", "Plan sufficiency under structural shift", data)
            L += ["", "![](figures/shift_detection_controlled.png)"]

    # mode validation
    if any("mode_decomposition" in S[m] for m in models):
        keys = ["e2e_success", "e2e_fail_detection_wrong", "e2e_fail_but_dc_success",
                "dc_fail_but_dxc_success (diagnosis-attributable)", "fail_in_all_modes (planning)"]
        L += ["", "## Mode decomposition (same instances across modes; resolvable states)", "",
              "An End-to-End failure that disappears in Detection-Controlled is attributed to detection/framing; a "
              "Detection-Controlled failure that disappears in Diagnosis-Controlled to diagnosis; only failures in all "
              "three modes are planning failures. Only instances whose answers parsed in all three modes are used; "
              "the number excluded is in the last column.", "",
              "| Agent / model | " + " | ".join(keys) + " | excluded (unparsed in some mode) |",
              "|---|" + "---|" * (len(keys) + 1)]
        for m in models:
            d = S[m].get("mode_decomposition", {})
            L.append(f"| {m} | " + " | ".join(fmt(d.get(k)) for k in keys)
                     + f" | {d.get('excluded_unparsed_in_some_mode', '–')} |")
        L += ["", "## Instruction compliance and hierarchical metrics", "",
              "| Agent / model | DC: claims sufficient (contradicts prompt) | DxC: class differs from given | "
              "A_D | A_G | A_P (DC) | A_P' (DxC) | A_S | A_E2E |", "|---|---|---|---|---|---|---|---|---|"]
        for m in models:
            c = S[m].get("instruction_compliance", {})
            h = S[m].get("hierarchical", {})
            hv = [fmt(h.get(k)) for k in ("A_D detection (E2E)", "A_G diagnosis given insufficiency (DC)",
                                          "A_P plan optimal given correct diagnosis (DC)", "A_P' plan optimal given class (DxC)",
                                          "A_S sufficiency judgment (E5)", "A_E2E fully correct behaviour (E2E)")]
            L.append(f"| {m} | {fmt(c.get('dc_claims_state_sufficient'))} | {fmt(c.get('dxc_class_differs_from_given'))} | "
                     + " | ".join(hv) + " |")
        L += ["", "## Strata: shallow-heuristic difficulty and template", "",
              "`heuristic_hard` = instances where the text-only h1pp baseline fails. A model's advantage over shallow "
              "reading shows only there.", "",
              "| Agent / model | Stratum | Instances | DC class correct | DC plan sufficient | DC plan optimal |",
              "|---|---|---|---|---|---|"]
        for m in models:
            for group in ("by_heuristic_stratum", "by_template"):
                for st, v in S[m].get(group, {}).items():
                    L.append(f"| {m} | {st} | {v['n_instances']} | {fmt(v['dc_class_correct'])} | "
                             f"{fmt(v['dc_plan_sufficient'])} | {fmt(v['dc_plan_optimal'])} |")
        L += ["", "## Calibration (stated confidence vs plan sufficiency)", "",
              "| Agent / model | Mode | n | Brier | ECE |", "|---|---|---|---|---|"]
        for m in models:
            for mode, c in S[m].get("calibration", {}).items():
                L.append(f"| {m} | {MODE_LABEL[mode]} | {c['n']} | {num(c['brier'])} | {num(c['ece'])} |")

    # model vs shallow heuristic (same instances)
    if any("versus_h1pp" in S[m] for m in models):
        L += ["", "## Model vs shallow heuristic h1pp (same instances, plan optimal on resolvable states)", "",
              "| Model | Mode | Model minus h1pp [CI] | McNemar p |", "|---|---|---|---|"]
        for m in models:
            for mode, v in S[m].get("versus_h1pp", {}).items():
                L.append(f"| {m} | {MODE_LABEL[mode]} | {fmt(v['plan_optimal_model_minus_baseline'])} | "
                         f"{v['plan_optimal_mcnemar']['p_value']:.3g} |")

    # full breakdown: stratum x mode x class
    if any("breakdown" in S[m] for m in models):
        L += ["", "## Breakdown: stratum x mode x resource class (plan optimal on resolvable states)", "",
              "Full v3 is primary; heuristic_hard is a pre-registered stress test (it contains no NEITHER items, so "
              "compare within class).", "",
              "| Agent / model | Stratum | Mode | Class | n | Class correct | Plan sufficient | Plan optimal |",
              "|---|---|---|---|---|---|---|---|"]
        for m in models:
            for st, modes in S[m].get("breakdown", {}).items():
                for mode, classes in modes.items():
                    for cls, v in classes.items():
                        L.append(f"| {m} | {st} | {MODE_LABEL[mode]} | {cls} | {v['n']} | {fmt(v['class_correct'])} | "
                                 f"{fmt(v['plan_sufficient'])} | {fmt(v['plan_optimal'])} |")

    # confirmatory family, taxonomy, usage
    L += ["", "## Confirmatory tests (Holm-adjusted; see PROTOCOL.md §4)", "",
          "| Agent / model | Test | p | Holm p |", "|---|---|---|---|"]
    for m in models:
        c = S[m].get("confirmatory", {})
        for k, p in c.get("raw_p", {}).items():
            L.append(f"| {m} | {k} | {p:.3g} | {c['holm_adjusted_p'][k]:.3g} |")
    L += ["", "## Error taxonomy (first failing stage)", ""]
    for m in models:
        L.append(f"- {m}: {S[m].get('error_taxonomy')}")
    L += ["", "## Ceiling / floor flags", ""]
    for m in models:
        flags = S[m].get("ceiling_floor") or []
        L.append(f"- {m}: " + (", ".join(f"{f['metric']} {f['kind']} ({f['mean']:.2f})" for f in flags) or "none"))
    L += ["", "## Usage", ""]
    for m in models:
        u = S[m].get("usage", {}).get("all", {})
        L.append(f"- {m}: {u.get('requests')} requests, parse errors {num(u.get('parse_error_rate'))}, "
                 f"refusals {num(u.get('refusal_rate'))}, truncations {num(u.get('truncation_rate'))}, "
                 + (f"cost ${u.get('cost_usd_total', 0):.4f}" if u.get("currency", "usd") == "usd"
                    else f"cost {u.get('cost_usd_total', 0):.4f} {u.get('currency')}")
                 + (f"; served models {u['served_models']}" if u.get("served_models") else ""))
    if synthetic:
        L += ["", SYNTHETIC_BANNER]
    (out / "report.md").write_text("\n".join(L) + "\n")
