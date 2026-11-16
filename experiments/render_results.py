"""Compact tables for the report and the README, read from the summary files. Formatting only: no analysis.

    python experiments/render_results.py > results/aggregate/final_test/RESULTS_TABLES.md
    python experiments/render_results.py --test DIR --robust DIR      # other locations
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "results" / "aggregate"
MODELS = {"adaption-qwen3.5-397b": "qwen3.5-397b", "adaption-qwen3.8-27b": "qwen3.8-27b",
          "adaption-deepseek-v4-flash": "deepseek-v4-flash", "adaption-gemma-4-26b-a4b-it-schema": "gemma-4-26b +schema"}
DC, E2E = "detection_controlled", "end_to_end"


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def get(d, *path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def m2(d) -> str:
    """Mean only."""
    v = d.get("mean") if isinstance(d, dict) else d
    return "n/a" if v is None else f"{v:.2f}"


def ci(d, signed: bool = False) -> str:
    if not isinstance(d, dict) or d.get("mean") is None:
        return "n/a"
    lo, hi = d.get("lo", d.get("lo95")), d.get("hi", d.get("hi95"))
    s = "+" if signed else ""
    return f"{d['mean']:{s}.2f} [{lo:{s}.2f}, {hi:{s}.2f}]"


def pv(p) -> str:
    return "n/a" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def eop_key(conds: dict) -> str | None:
    return "C2" if "C2" in conds else "C" if "C" in conds else None


def table(head: list[str], rows: list[list[str]]) -> list[str]:
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows] + [""]


def native(v3: dict | None, eop: dict | None, label: str) -> list[str]:
    rows = []
    for k, name in MODELS.items():
        b, a = get(v3, "by_model", k), get(eop, "models", k)
        if not b and not a:
            continue
        rows.append([name, ci(get(b, "E2", "detection_accuracy")),
                     ci(get(a, E2E, "conditions", "A", "sufficient_all")), ci(get(a, DC, "conditions", "A", "optimal_all")),
                     ci(get(b, "E8", DC, "correct_defer")), ci(get(b, "E1", "b_end_to_end_on_sufficient_states", "proposes_any_action"))])
    return [f"### Native planning, {label}", "",
            "All attempted. Detection: says correctly whether the state is sufficient (End-to-End). Sufficient and "
            "optimal: resolvable states. Defer: empty plan and \"defer\" on NEITHER states. Acts when sufficient: "
            "proposes an action on an ALREADY_SUFFICIENT state.", ""] + table(
        ["Model", "Detection (E2E)", "Plan sufficient (E2E)", "Plan optimal (DC)", "Defers on NEITHER (DC)",
         "Acts when sufficient (E2E)"], rows)


def stopping(v3: dict | None, t1: dict | None, label: str) -> list[str]:
    """One table for the main text: the stopping measures of the native answer."""
    rows = []
    for k, name in MODELS.items():
        b, m = get(v3, "by_model", k), get(t1, "models", k)
        if not b and not m:
            continue
        t = get(m, "T_OI_1") or {}
        rows.append([name, ci(get(b, "E8", DC, "correct_defer")),
                     m2(get(b, "E1", "b_end_to_end_on_sufficient_states", "proposes_any_action")),
                     "n/a" if not m else f"{ci(get(m, 'O1_into_AS'))} (n={get(m, 'n_into_AS')})",
                     "n/a" if not m else f"{'yes' if t.get('supported') else 'no'} ({pv(t.get('holm_p'))})"])
    return [f"### Stopping, {label}", "",
            "Native answer, all attempted. Defers: empty plan "
            "and \"defer\" when no available action can settle the question. Acts: proposes any action on a state that "
            "is already sufficient, from the start or after one edit. Last column: registered test T-OI-1, one-sided, "
            "Holm across models.", ""] + table(
        ["Model", "Defers on NEITHER (DC)", "Acts when sufficient from the start (E2E)",
         "Acts when one edit made it sufficient (E2E)", "Above 0.05? (Holm p)"], rows)


def conditions(eop: dict | None, label: str, mode: str = DC) -> list[str]:
    rows = []
    conf = get(eop, "confirmatory_final_EOP_minus_A_optimal_DC") or {}
    up = get(eop, "upper_bound_parser_EOP", mode, "optimal_all")
    for k, name in MODELS.items():
        c = get(eop, "models", k, mode, "conditions")
        if not c:
            continue
        e = eop_key(c)
        b = "B" if "B" in c else "Bt"
        d = {"C2": "D2", "C": "D"}.get(e)
        d = d if d in c else "Dt"
        p = get(eop, "models", k, mode, "paired") or {}
        rows.append([name, ci(get(c, "A", "optimal_all")), ci(get(c, b, "optimal_all")) + (" (text)" if b == "Bt" and b in c else ""),
                     ci(get(c, d, "optimal_all")), f"{ci(get(c, e, 'optimal_all'))} ({'v1' if e == 'C' else 'v2'})",
                     m2(up), ci(p.get(f"{e}-A|plan_optimal"), True), pv(get(conf, k, "holm_p")) if mode == DC else ""])
    return [f"### Conditions, {label}, {mode.replace('_', '-')}", "",
            "Optimal-plan rate on resolvable states, all attempted, 95% family-clustered bootstrap interval. EOP uses the "
            "frozen extraction prompt of each model (v2; gemma +schema: registered v1).", ""] + table(
        ["Model", "A native", "B structured", "Verifier only", "EOP", "P parser", "EOP − A", "Holm p (one-sided)"], rows)


def conditions_main(eop: dict | None, label: str) -> list[str]:
    """The conditions table for the main text: means only, interval on the difference. Full intervals: conditions()."""
    rows = []
    conf = get(eop, "confirmatory_final_EOP_minus_A_optimal_DC") or {}
    up = get(eop, "upper_bound_parser_EOP", DC, "optimal_all")
    for k, name in MODELS.items():
        c = get(eop, "models", k, DC, "conditions")
        if not c:
            continue
        e = eop_key(c)
        b = "B" if "B" in c else "Bt"
        p = get(eop, "models", k, DC, "paired") or {}
        rows.append([name, m2(get(c, "A", "optimal_all")), m2(get(c, b, "optimal_all")), m2(get(c, e, "optimal_all")), m2(up),
                     ci(p.get(f"{e}-A|plan_optimal"), True), pv(get(conf, k, "holm_p"))])
    return [f"### Main-text conditions, {label}, detection-controlled", "",
            "Optimal-plan rate on resolvable states, all attempted. Intervals for every cell are in the full table below.", ""
            ] + table(["Model", "A native", "B structured", "EOP", "P parser", "EOP − A", "Holm p (one-sided)"], rows)


def headline(v3: dict | None, eop: dict | None, t1: dict | None, label: str) -> list[str]:
    """The one table of the submission report: plan quality by condition and the two stopping measures."""
    rows = []
    up = get(eop, "upper_bound_parser_EOP", DC, "optimal_all")
    for k, name in MODELS.items():
        c = get(eop, "models", k, DC, "conditions")
        if not c:
            continue
        e = eop_key(c)
        b = "B" if "B" in c else "Bt"
        p = get(eop, "models", k, DC, "paired") or {}
        m = get(t1, "models", k)
        rows.append([name, m2(get(c, "A", "optimal_all")), m2(get(c, b, "optimal_all")), m2(get(c, e, "optimal_all")), m2(up),
                     ci(p.get(f"{e}-A|plan_optimal"), True),
                     m2(get(v3, "by_model", k, "E8", DC, "correct_defer")),
                     "n/a" if not m else ci(get(m, "O1_into_AS"))])
    return [f"### Headline table, {label}", "",
            "Columns 2-5: optimal-plan rate on resolvable states, Detection-Controlled, all attempted. Defers: on NEITHER "
            "states. Acts: proposes an action on a state that one edit made sufficient (n=169). Test p-values: tables below.", ""] + table(
        ["Model", "Native", "Structured prompt", "EOP", "Parser", "EOP − native", "Defers when nothing helps",
         "Acts on newly sufficient states"], rows)


def registered_c(eop_dev: dict | None) -> list[str]:
    rows = []
    for k, name in MODELS.items():
        c = get(eop_dev, "models", k, DC, "conditions")
        if c:
            rows.append([name, m2(get(c, "A", "optimal_all")), m2(get(c, "C", "optimal_all")), m2(get(c, "C2", "optimal_all")),
                         f"{get(c, 'C', 'unparsed_items')}/{get(c, 'C', 'n_items')}"])
    return ["### EOP as registered and as amended, development split, Detection-Controlled", ""] + table(
        ["Model", "A native", "Registered EOP (prompt v1)", "Amended EOP (prompt v2)", "No usable extraction (registered)"], rows)


def over_intervention(dev: dict | None, test: dict | None) -> list[str]:
    rows = []
    for k, name in MODELS.items():
        r = [name]
        for s in (dev, test):
            m = get(s, "models", k)
            o = get(m, "O1_into_AS")
            t = get(m, "T_OI_1") or {}
            hp = t.get("holm_p")
            r += ["n/a" if not m else f"{ci(o)} (n={get(m, 'n_into_AS')})", "n/a" if not m else m2(get(m, "O1_native_AS")),
                  "n/a" if not m else f"{'yes' if t.get('supported') else 'no'} ({pv(hp)})"]
        rows.append(r)
    return ["### Over-intervention on states that one edit made sufficient (End-to-End)", "",
            "Share of such states on which the model proposes any action. Beside it: the same rate on states that were "
            "sufficient from the start. Registered test T-OI-1: rate above 0.05, one-sided, Holm across models.", ""] + table(
        ["Model", "Dev: after the edit", "Dev: sufficient from the start", "Dev: above 0.05? (Holm p)",
         "Test: after the edit", "Test: sufficient from the start", "Test: above 0.05? (Holm p)"], rows)


def rewording(rb: dict | None) -> list[str]:
    if not rb:
        return []
    out = ["### Rewording study (development families, End-to-End, all attempted)", "",
           "Optimal-plan rate on resolvable states. State exact: the extracted state equals the true state.", ""]
    tests = rb.get("registered_test_EOP_minus_A_optimal_pooled", {})
    for k, name in MODELS.items():
        m = get(rb, "models", k)
        if not m:
            continue
        c = m["canonical"]
        rows = [["canonical", m2(get(c, "A", "optimal_all")), m2(get(c, "B", "optimal_all")), m2(get(c, "EOP", "optimal_all")),
                 m2(get(c, "EOP_extraction", "exact")), "", "", m2(get(c, "P", "optimal_all")), ""]]
        for kind, km in m["kinds"].items():
            cc = km["conditions"]
            rows.append([kind, m2(get(cc, "A", "optimal_all")), m2(get(cc, "B", "optimal_all")), m2(get(cc, "EOP", "optimal_all")),
                         m2(get(km, "extraction", "EOP", "exact")), m2(get(cc, "EOPN", "optimal_all")),
                         m2(get(km, "extraction", "EOPN", "exact")), m2(get(cc, "P", "optimal_all")),
                         ci(get(km, "paired", "EOP-A|plan_optimal"), True)])
        out += [f"**{name}**", ""] + table(["Wording", "A native", "B structured", "EOP", "EOP state exact", "EOP-N",
                                           "EOP-N state exact", "P parser", "EOP − A"], rows)
        po = m.get("pooled_optimal", {})
        out += [f"Pooled over the four wordings: EOP − A {ci(po.get('EOP-A'), True)}, Holm p {pv(get(tests, k, 'holm_p'))}; "
                f"EOP-N − A {ci(po.get('EOPN-A'), True)}; EOP − P {ci(po.get('EOP-P'), True)}.", ""]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default=str(AGG / "final_test"))
    ap.add_argument("--robust", default=str(AGG / "robust_dev"))
    a = ap.parse_args(argv)
    test = Path(a.test)
    eop_t, eop_d = load(test / "eop" / "eop_summary.json") or {}, load(AGG / "eop_dev" / "eop_summary.json") or {}
    lines = ["# Result tables", "", "Generated by `experiments/render_results.py` from the summary files. Formatting only.", ""]
    v3_t, t1_t = load(test / "v3" / "pilot_test" / "summary.json"), load(test / "t1" / "t1_test_summary.json")
    lines += headline(v3_t, eop_t.get("v3test"), t1_t, "held-out test split (63 families)")
    lines += stopping(v3_t, t1_t, "held-out test split (63 families)")
    lines += conditions_main(eop_t.get("v3test"), "held-out test split")
    lines += native(v3_t, eop_t.get("v3test"), "held-out test split (63 families)")
    lines += native(load(AGG / "v3dev" / "pilot_dev" / "summary.json"), eop_d.get("v3dev"), "development split (72 families)")
    lines += conditions(eop_t.get("v3test"), "held-out test split")
    lines += conditions(eop_t.get("v3test"), "held-out test split", E2E)
    lines += conditions(eop_d.get("v3dev"), "development split")
    lines += registered_c(eop_d.get("v3dev"))
    lines += over_intervention(load(AGG / "t1b_dev" / "t1b_summary.json"), t1_t)
    lines += rewording(load(Path(a.robust) / "robust_summary.json"))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
