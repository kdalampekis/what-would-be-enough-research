"""Render an EOP summary (run_eop.py --analyze-only) as markdown tables. No analysis: formatting only.

    python experiments/render_eop.py results/aggregate/final_test/eop/eop_summary.json
"""

from __future__ import annotations

import json
import sys


def f(d, key="mean"):
    return "n/a" if not d or d.get(key) is None else f"{d[key]:.2f}"


def g(d):
    return "n/a" if not d or d.get("mean") is None else f"{d['mean']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]"


def main(path: str) -> None:
    s = json.load(open(path))
    for name, st in s.items():
        print(f"## {name}: {st['items']} items, {st['families']} families\n")
        modes = [m for m in ("detection_controlled", "end_to_end") if m in next(iter(st["models"].values()))]
        for mode in modes:
            print(f"### {mode} — optimal / sufficient (all attempted, resolvable); stop = correct stopping on "
                  f"ALREADY_SUFFICIENT and NEITHER\n")
            print("| model | A native | B structured | EOP | verifier only | P parser | EOP − A (optimal) | EOP − B | EOP − verifier | "
                  "stop A → EOP | unparsed A / B / EOP |")
            print("|---|---|---|---|---|---|---|---|---|---|---|")
            up = st["upper_bound_parser_EOP"][mode]
            for k, m in st["models"].items():
                c, p = m[mode]["conditions"], m[mode]["paired"]
                e = "C2" if "C2" in c else "C"
                b = "B" if "B" in c else "Bt"
                d = {"C2": "D2", "C": "D"}[e] if {"C2": "D2", "C": "D"}[e] in c else "Dt"
                cell = lambda x: "n/a" if x not in c else f"{f(c[x]['optimal_all'])} / {f(c[x]['sufficient_all'])}"  # noqa: E731
                un = lambda x: "n/a" if x not in c else f"{c[x]['unparsed_items']}/{c[x]['n_items']}"  # noqa: E731
                print(f"| {k.replace('adaption-', '')} | {cell('A')} | {cell(b)}{' (Bt)' if b == 'Bt' else ''} | {cell(e)} ({e}) | "
                      f"{cell(d)} ({d}) | {f(up['optimal_all'])} / {f(up['sufficient_all'])} | {g(p.get(f'{e}-A|plan_optimal'))} | "
                      f"{g(p.get(f'{e}-{b}|plan_optimal'))} | {g(p.get(f'{e}-{d}|plan_optimal'))} | "
                      f"{f(c['A']['stop_ok_AS_NEITHER'])} → {f(c.get(e, {}).get('stop_ok_AS_NEITHER'))} | {un('A')} / {un(b)} / {un(e)} |")
            print()
        for key in ("confirmatory_C_minus_A_optimal_DC", "confirmatory_final_EOP_minus_A_optimal_DC"):
            if key in st:
                print(f"**{key}:** " + "; ".join(f"{k.replace('adaption-', '')}: {v}" for k, v in st[key].items()) + "\n")
        print("Extraction calls and failures: " + "; ".join(
            f"{k.replace('adaption-', '')}: v2 {m['pipeline_C2'] or '-'} | v1 {m['pipeline_C'] or '-'}" for k, m in st["models"].items()) + "\n")
        if any("t1_pairs" in m.get("end_to_end", {}) for m in st["models"].values()):
            print("T1 pair joint accuracy (both items of a pair correct), End-to-End:\n")
            for k, m in st["models"].items():
                tp = m["end_to_end"].get("t1_pairs", {})
                print(f"- {k.replace('adaption-', '')}: " + ", ".join(f"{c} {json.dumps({kk: vv for kk, vv in v.items() if 'joint' in kk})[:160]}" for c, v in tp.items()))
            print()


if __name__ == "__main__":
    main(sys.argv[1])
