"""Fill the generated blocks of paper/report.md and paper/extended_report.md from the result files.
Copying and formatting only: no analysis. A block is everything between `<!-- BEGIN name -->` and `<!-- END name -->`.

    python paper/fill_report.py
"""

from __future__ import annotations

import contextlib
import io
import json
import re
from pathlib import Path

import appendix_e

HERE = Path(__file__).resolve().parent
AGG = HERE.parent / "results" / "aggregate"
NAMES = {"adaption-qwen3.5-397b": "qwen3.5-397b", "adaption-qwen3.8-27b": "qwen3.8-27b",
         "adaption-deepseek-v4-flash": "deepseek-v4-flash", "adaption-gemma-4-26b-a4b-it-schema": "gemma-4-26b +schema"}


def sections(text: str) -> dict[str, str]:
    return {p.split("\n", 1)[0]: p.split("\n", 1)[1] for p in re.split(r"^### ", text, flags=re.M)[1:]}


def table(sec: str) -> str:
    return "\n".join(l for l in sec.splitlines() if l.startswith("|"))


def rows(head: list[str], body: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in body])


def ci(d, signed: bool = False) -> str:
    s = "+" if signed else ""
    return f"{d['mean']:{s}.2f} [{d['lo']:{s}.2f}, {d['hi']:{s}.2f}]"


def pv(p) -> str:
    return "n/a" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def clarity_table(fu: dict) -> str:
    out = []
    for k, m in fu["clarity"]["models"].items():
        g = m["groups"]["all_attempted"]
        a, r = g["AS all"]["acts"], g["AS all"]["recertifies"]
        prem = sum(g[c]["premature_stop"]["changed_W1_only"] - g[c]["premature_stop"]["changed_W0_only"] for c in ("COMPUTATION_ONLY", "BOTH"))
        out.append([NAMES[k], ci(a["W0"]), ci(a["W1"]), ci(a["W1_minus_W0"], True), pv(fu["clarity"]["primary_holm_p"].get(k)),
                    f"{r['W0']['mean']:.2f} → {r['W1']['mean']:.2f}", f"{prem:+d} of 120"])
    return rows(["Model", "Acts, original wording", "Acts, clarified wording", "Change", "Holm p",
                 "Re-runs a known computation", "Premature stops on states that need action, change"], out)


def cost_table(fu: dict) -> str:
    out = []
    for k, m in fu["cost"]["models"].items():
        f = m["flip_pairs"]
        o = f["below_item_outcomes"]
        out.append([NAMES[k], ci(f["optimal_above"]), ci(f["optimal_below"]), ci(f["above_minus_below"], True),
                    pv(fu["cost"]["primary_holm_p"].get(k)), f"{m['by_relation']['below']['sufficient']['mean']:.2f}",
                    f"{o.get('optimal', 0)} / {o.get('kept the plan that was cheapest before the price change', 0)} / "
                    f"{o.get('another sufficient plan that is not the cheapest', 0)} / "
                    f"{o.get('insufficient plan', 0) + o.get('no usable answer', 0)}"])
    return rows(["Model", "Cheapest plan, price just above", "Cheapest plan, price just below", "Above − below", "Holm p",
                 "Sufficient, below", "Below items: cheapest / kept old plan / other sufficient / insufficient or none"], out)


def repair_table(rp: dict, sup: dict) -> str:
    out = []
    for k, m in rp["models"].items():
        for arm, label in (("F", "frozen"), ("N", "translating")):
            x = m[arm]["pooled"]
            a, b, r = x["first"], x["with_repair"], x["of_rejected_first_answers"]
            rise = sup[f"{k} | {arm}"]["rise_in_accepted_but_wrong_with_repair"]
            out.append([NAMES[k], label, f"{a['state_exact']['mean']:.2f} → {b['state_exact']['mean']:.2f}", ci(x["gain_state_exact"], True),
                        f"{a['accepted_but_wrong']['mean']:.2f} → {b['accepted_but_wrong']['mean']:.2f} ({ci(rise, True)})",
                        f"{a['plan']['optimal_all']['mean']:.2f} → {b['plan']['optimal_all']['mean']:.2f}",
                        f"{r['recovered_exact']} / {r['accepted_but_wrong_after_repair']} / {r['still_rejected']} of {r['n']}"])
    return rows(["Model", "First prompt", "Exact state: first → with repair", "Gain", "Accepted but wrong: first → with repair (rise)",
                 "Optimal plan: first → with repair", "Rejected first answers: recovered / wrong / still rejected"], out)


def followup_glance(fu: dict, rp: dict) -> str:
    out = []
    for k, name in NAMES.items():
        c, m, r = fu["cost"]["models"].get(k), fu["clarity"]["models"].get(k), rp["models"].get(k)
        if not (c or m or r):
            continue
        a = m["groups"]["all_attempted"]["AS all"]["acts"] if m else None
        x = r["F"]["pooled"] if r else None
        out.append([name,
                    "not run" if not c else f"{c['flip_pairs']['optimal_above']['mean']:.2f} / {c['flip_pairs']['optimal_below']['mean']:.2f}",
                    "not run" if not a else f"{a['W0']['mean']:.2f} → {a['W1']['mean']:.2f}",
                    "not run" if not x else f"{x['first']['state_exact']['mean']:.2f} → {x['with_repair']['state_exact']['mean']:.2f}"])
    return rows(["Model", "Cost: cheapest plan, price above / below", "Clarity: acts, original → clarified wording",
                 "Repair: exact state, first → with repair"], out)


def followup_appendix() -> str:
    fu = (AGG / "followup" / "followup_report.md").read_text()
    rp = (AGG / "repair" / "repair_report.md").read_text()
    out = []
    for text, title in ((fu, "Studies 1 and 2"), (rp, "Study 3")):
        body = text.split("\n", 1)[1]
        body = re.sub(r"^### ", "**", body, flags=re.M)
        body = re.sub(r"^## ", "#### ", body, flags=re.M)
        body = re.sub(r"^(\*\*[^\n|]*[^*\n])$", r"\1**", body, flags=re.M).replace("adaption-", "")
        body = "\n".join(l for l in body.splitlines() if "class_correct" not in l)
        out += [f"### C.{len(out) // 3 + 1} {title}", "", body.strip(), ""]
    return "\n".join(out).rstrip()


def main() -> int:
    res = sections((AGG / "final_test" / "RESULTS_TABLES.md").read_text())
    by = lambda start: next(v for k, v in res.items() if k.startswith(start))  # noqa: E731
    fu = json.loads((AGG / "followup" / "followup_summary.json").read_text())
    rp = json.loads((AGG / "repair" / "repair_summary.json").read_text())
    sup = json.loads((AGG / "repair" / "repair_supplement.json").read_text())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        appendix_e.main([])
    extra = ["### E.4 Development split beside the held-out split", ""]
    for start in ("Native planning, development", "Conditions, development", "Over-intervention"):
        title = next(k for k in res if k.startswith(start))
        extra += [f"#### {title}", "", by(start).strip(), ""]
    blocks = {"table-headline": table(by("Headline table")),
              "table-followup": followup_glance(fu, rp),
              "table-clarity": clarity_table(fu), "table-cost": cost_table(fu), "table-repair": repair_table(rp, sup),
              "appendix-followup": followup_appendix(),
              "table-stopping": table(by("Stopping, held-out")),
              "table-conditions": table(by("Main-text conditions, held-out")),
              "appendix-e": buf.getvalue().rstrip() + "\n\n" + "\n".join(extra).rstrip()}
    for name in ("report.md", "extended_report.md"):
        p = HERE / name
        s = p.read_text()
        done = []
        for block, body in blocks.items():
            pat = re.compile(rf"(<!-- BEGIN {block} -->\n).*?(<!-- END {block} -->)", re.S)
            if pat.search(s):
                s = pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), s)
                done.append(block)
        p.write_text(s)
        print(f"{name}: filled {', '.join(done)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
