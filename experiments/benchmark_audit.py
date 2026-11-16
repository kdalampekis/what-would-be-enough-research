"""Benchmark audit: shortcuts, leakage, balance, label re-verification. No model calls.

    python experiments/benchmark_audit.py --pool data/generated/pool_v2/instances.jsonl \
        --compare data/generated/pool_v1/instances.jsonl

The test split is never used for the shortcut probe (train -> dev only).
Writes results/benchmark_audit.{json,md}.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from msep.benchmark import audit
from msep.benchmark.schemas import instance_from_record
from msep.oracle.brute_force import BruteForce

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> list[dict]:
    return [json.loads(l) for l in open(path)]


def verify_labels(records: list[dict]) -> dict:
    bad = []
    for r in records:
        st = instance_from_record(r).state
        b = BruteForce(st).analyze()
        stored = r["oracle"]
        ok = (b.resource_class(st).value == stored["resource_class"]
              and b.optimal_cost == stored["optimal_cost"]
              and sorted(map(list, b.optimal_plans)) == sorted(stored["optimal_plans"]))
        if not ok:
            bad.append(r["instance_id"])
    return {"checked": len(records), "mismatches": len(bad), "examples": bad[:10]}


def verify_rendering(records: list[dict]) -> dict:
    """parse(prompt_text) must give a state with the same oracle labels (ASSUMPTIONS A11)."""
    from msep.benchmark.parsing import parse_state
    from msep.oracle import minimal_plan
    bad = []
    for r in records:
        res = minimal_plan.solve(parse_state(r["prompt_text"]))
        alias = r["rendering"]["action_alias"]
        want = sorted(tuple(sorted(alias[x] for x in p)) for p in r["oracle"]["optimal_plans"])
        if (res.resource_class.value != r["oracle"]["resource_class"] or res.analysis.optimal_cost != r["oracle"]["optimal_cost"]
                or sorted(res.analysis.optimal_plans) != want):
            bad.append(r["instance_id"])
    return {"checked": len(records), "mismatches": len(bad), "examples": bad[:10]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--compare", default=None, help="an earlier pool, for before/after shortcut numbers")
    ap.add_argument("--variants", default=None, help="directory of variant JSONL files to spot-check")
    ap.add_argument("--variant-stride", type=int, default=20)
    ap.add_argument("--out", default=str(ROOT / "results"))
    a = ap.parse_args()
    all_recs = load(a.pool)
    nontest = [r for r in all_recs if r["split"] != "test"]
    report = {
        "pool": a.pool,
        "shortcut_probe": audit.shortcut_report(nontest),
        "split_leakage": audit.split_leakage(all_recs),
        "instruction_leakage": audit.instruction_leakage(all_recs),
        "class_balance_by_split": audit.balance(all_recs),
        "computed_value_balance": audit.computed_value_balance(all_recs),
        "target_true_rate_by_sibling": audit.target_value_balance(all_recs),
        "optimal_plan_multiplicity": audit.optimal_plan_multiplicity(all_recs),
        "label_reverification_brute_force": verify_labels(all_recs),
        "rendering_roundtrip": verify_rendering(all_recs),
        "consequent_value_leak": audit.consequent_value_leak(all_recs),
        "q_rule_position": audit.q_rule_position(nontest),
        "cost_vs_optimality": audit.cost_vs_optimality(nontest),
        "heuristic_baselines_dev": audit.heuristic_baselines([r for r in all_recs if r["split"] == "dev"]),
        "mental_shortcuts": audit.mental_shortcuts(nontest),
        "hard_subset_composition_dev": audit.hard_subset_composition([r for r in all_recs if r["split"] == "dev"]),
    }
    if a.variants:
        sample = []
        for f in sorted(Path(a.variants).glob("*.jsonl")):
            sample += [json.loads(l) for k, l in enumerate(open(f)) if k % a.variant_stride == 0]
        report["variants_label_reverification"] = verify_labels(sample)
        report["variants_rendering_roundtrip"] = verify_rendering(sample)
    if a.compare:
        old = [r for r in load(a.compare) if r["split"] != "test"]
        report["shortcut_probe_before"] = audit.shortcut_report(old)
        report["compare_pool"] = a.compare
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmark_audit.json").write_text(json.dumps(report, indent=1))
    (out / "benchmark_audit.md").write_text(markdown(report))
    checks = {k: v for k, v in report.items() if isinstance(v, dict) and "mismatches" in v}
    for k, v in checks.items():
        print(f"{k}: {v['checked']} checked, {v['mismatches']} mismatches")
    return 0 if all(v["mismatches"] == 0 for v in checks.values()) else 1


def markdown(r: dict) -> str:
    L = ["# Benchmark audit", "", f"Pool: `{r['pool']}`. No model was called. The shortcut probe is trained "
         "on the train split and evaluated on the dev split; the test split is not used.", ""]
    L += ["## 1. Shortcut probe", "",
          "A lookup-table classifier memorises the majority resource class for each tuple of surface "
          "features of the prompt (counts of offered ASK/COMPUTE actions and of known/unknown world and "
          "computed variables). If it beats the majority baseline by a wide margin, the class can be read "
          "off the prompt without reasoning about relevance or sufficiency.", "",
          "| Scope | Features | Comparison pool | This pool | Majority baseline |", "|---|---|---|---|---|"]
    before = r.get("shortcut_probe_before")
    for scope in ("insufficient_only", "all_classes"):
        for name, v in r["shortcut_probe"][scope].items():
            b = before[scope][name]["probe_accuracy"] if before else None
            L.append(f"| {scope} | {name} | {'–' if b is None else f'{b:.1%}'} | {v['probe_accuracy']:.1%} | "
                     f"{v['majority_baseline']:.1%} |")
    L += ["", "**Residual.** The class is defined by which *relevant* variables are unknown, so counts of known "
          "variables by kind keep some signal even with randomised distractors. This probe is reported as a "
          "surface-feature baseline alongside every E3 result; a model's diagnosis accuracy should be read "
          "against it, not against chance.", ""]
    s = r["split_leakage"]
    L += ["## 2. Leakage", "",
          f"- Families in more than one split: {s['families_in_more_than_one_split']} (of {s['families']})",
          f"- Identical prompt texts across splits: {s['identical_prompt_texts_across_splits']}",
          f"- Distinct instruction wrappers per mode (must be 1): "
          f"{ {k: v['distinct_wrappers'] for k, v in r['instruction_leakage'].items() if isinstance(v, dict) and 'distinct_wrappers' in v} }",
          f"- Label or role words in state text: {r['instruction_leakage']['label_words_in_state_text'] or 'none'}", ""]
    L += ["## 3. Balance", "", "Resource class by split:", ""]
    for sp, c in r["class_balance_by_split"].items():
        L.append(f"- {sp}: {c}")
    L += ["", "True rate of computed variables (a skewed rate would let a model guess certified results):", ""]
    for k, v in r["computed_value_balance"].items():
        L.append(f"- {k}: {v['true_rate']:.2f} (n = {v['n']})")
    L += ["", f"True rate of the target, by sibling type: "
          f"{ {k: round(v, 2) for k, v in r['target_true_rate_by_sibling'].items()} }", ""]
    lv = r["label_reverification_brute_force"]
    L += ["## 4. Labels", "",
          f"- Brute-force re-verification of class, optimal cost and every optimal plan: {lv['checked']} instances, "
          f"{lv['mismatches']} mismatches.",
          f"- Number of optimal plans per resolvable instance: {r['optimal_plan_multiplicity']}. Scoring accepts "
          "any plan that is sufficient at optimal cost, not only the listed ones (tested in `tests/test_scoring_ties.py`).", ""]
    L += ["## 4a. Leaks found by the independent adversarial audit", "",
          f"- Implication rules whose consequent is true in the latent world: "
          f"{r['consequent_value_leak']['consequent_true_in_latent_rate']:.2f} of {r['consequent_value_leak']['implication_rules']} "
          "(1.00 = the rule text copies hidden values; about 0.5-0.75 is the unavoidable information in a true rule).",
          f"- Rule defining Q: most common position holds {r['q_rule_position']['most_common_position_share']:.0%} of "
          f"instances across {r['q_rule_position']['distinct_positions']} positions.",
          f"- Optimal share by action cost: { {c: round(v['optimal_share'], 2) for c, v in r['cost_vs_optimality'].items()} }", "",
          "## 4b. Shallow heuristic baselines (dev; deterministic, no model)", "",
          "| Heuristic | Class accuracy | Plan sufficient | Plan optimal |", "|---|---|---|---|"]
    for h, v in r["heuristic_baselines_dev"].items():
        L.append(f"| {h} | {v['class_accuracy']:.1%} | {v['plan_sufficient']:.1%} | {v['plan_optimal']:.1%} |")
    L += ["", "h1 reads only the rule defining Q; h1p adds aliases and NEITHER when an action is missing; h1pp also "
          "expands definitions one level. Model results must be read against these, and are also reported on the "
          "subset where h1pp fails (`heuristic_hard`).", ""]
    if "mental_shortcuts" in r:
        ms = r["mental_shortcuts"]
        L += ["## 4c. Can the certified computations be done in the head?", "",
              f"- Posterior by rounded log-likelihood sums: {ms['posterior_llr2sig_accuracy']:.1%} correct "
              f"(n = {ms['posterior_n']}).",
              f"- Modular exponentiation, 'true unless refuted by a small factor of m': "
              f"{ms['modpow_true_unless_refuted_accuracy']:.1%} (majority baseline {ms['modpow_majority_baseline']:.1%}, "
              f"n = {ms['modpow_n']}).",
              f"- Primality from the size of n (threshold fitted on train): "
              f"{(ms['primality_size_threshold_dev_accuracy'] or 0):.1%} on dev "
              f"(majority baseline {ms['primality_majority_baseline_dev']:.1%}, n = {ms['primality_dev_n']}).",
              "- 3-SAT near the threshold: no shortcut found by the audit.", ""]
    hc = r.get("hard_subset_composition_dev")
    if hc:
        L += ["## 4d. Composition of the pre-registered heuristic_hard subset (dev)", "",
              "Selecting on a baseline's failure selects on a correlate of difficulty. Compare within class, never "
              "pooled across subsets.", "",
              "| Subset | n | Classes | Motifs | Mean optimal-plan size | Mean actions | Mean prompt chars |",
              "|---|---|---|---|---|---|---|"]
        for k in ("all", "heuristic_hard", "heuristic_easy"):
            v = hc[k]
            L.append(f"| {k} | {v['n']} | {v['class']} | {v['motif']} | {v['mean_plan_size']} | {v['mean_actions']} | "
                     f"{v['mean_prompt_chars']} |")
        L += ["", f"Share of each class that is heuristic_hard: {hc['hard_share_by_class']}.", ""]
    rr = r["rendering_roundtrip"]
    L += [f"- Rendering round-trip (state rebuilt from the prompt text alone, then re-solved): {rr['checked']} "
          f"instances, {rr['mismatches']} mismatches. The prompt carries everything the oracle uses.", ""]
    if "variants_label_reverification" in r:
        v1, v2 = r["variants_label_reverification"], r["variants_rendering_roundtrip"]
        L += ["## 5. Variants (E10–E12), deterministic sample", "",
              f"- Brute-force label re-verification: {v1['checked']} variants, {v1['mismatches']} mismatches.",
              f"- Rendering round-trip: {v2['checked']} variants, {v2['mismatches']} mismatches.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
