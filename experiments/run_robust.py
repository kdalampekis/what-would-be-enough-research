"""Linguistic robustness study (PREREG_ROBUST.md): the same dev states, worded in four other ways.

Items: data/generated/robust_v1/items.jsonl (18 dev families, 137 states, 4 variants each). End-to-End only.

  A      native prompt on the variant text                      pool plan_rb
  B      structured obligation prompt (S1) on the variant text  pool plan_rbs1
  EOP    frozen extraction (v2; gemma +schema: v1 under schema) pools extract_rbv2 / extract_rb, then the planner
  EOP-N  normalising extraction prompt v3, then the planner     pool extract_rbv3
  P      the benchmark's deterministic parser + planner         no model

Canonical reference: the same 137 states in their canonical wording, from the dev runs (no new calls).

    python experiments/run_robust.py --models M --dry-run
    python experiments/run_robust.py --models M --budget CAP --max-calls N
    python experiments/run_robust.py --models M1,M2 --analyze-only
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_eop import RESOLVABLE, message_text_results, one_sided_p, planned_results, score, summarize, usage  # noqa: E402

from msep.benchmark.parsing import parse_state  # noqa: E402
from msep.benchmark.rephrase import KINDS  # noqa: E402
from msep.controllers.extraction_v3 import EXTRACTION_VERSION_V3, extraction_prompt_v3  # noqa: E402
from msep.controllers.llm_extractor import extraction_prompt, extraction_prompt_v2, state_from_extraction  # noqa: E402
from msep.envfile import load_env  # noqa: E402
from msep.eval import pilot  # noqa: E402
from msep.eval.bootstrap import cluster_mean_ci, holm, paired_diff_ci  # noqa: E402
from msep.eval.extraction_match import compare  # noqa: E402
from msep.models.config_check import currency  # noqa: E402
from msep.models.prompts import Mode, build_prompt  # noqa: E402
from msep.models.prompts_s1 import s1_prompt  # noqa: E402
from msep.models.runner import Job, estimate, latest_record, load_models, load_results, run_jobs  # noqa: E402
from msep.models.spend import Ledger  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
E2E = Mode.END_TO_END
GEMMA = "adaption-gemma-4-26b-a4b-it-schema"
# condition -> (pool, prompt function of the state text)
EXTRACT = {"s3": ("extract_rb", extraction_prompt), "s3v2": ("extract_rbv2", extraction_prompt_v2),
           "s3v3": ("extract_rbv3", extraction_prompt_v3)}
CANON_EXTRACT = {"s3": ("extract", extraction_prompt), "s3v2": ("extract_v2", extraction_prompt_v2)}


def frozen(key: str) -> str:
    """The frozen EOP extraction condition of a model (PREREG_FINAL.md section 3)."""
    return "s3" if key == GEMMA else "s3v2"


def jobs_for(items: list[dict], cond: str) -> list[Job]:
    out = []
    for r in items:
        base = build_prompt(r["prompt_text"], E2E, r["oracle"]["resource_class"])
        if cond == "a":
            out.append(Job("plan_rb", r["instance_id"], r["family_id"], E2E.value, base))
        elif cond == "s1":
            out.append(Job("plan_rbs1", r["instance_id"], r["family_id"], E2E.value, s1_prompt(base)))
        else:
            pool, fn = EXTRACT[cond]
            out.append(Job(pool, r["instance_id"], r["family_id"], "extraction", fn(r["prompt_text"])))
    return out


def extractions(items: list[dict], pool: str, fn, key: str, raw: Path) -> dict[str, dict]:
    ex = {}
    for r in items:
        rec = latest_record(raw, Job(pool, r["instance_id"], r["family_id"], "extraction", fn(r["prompt_text"])), key)
        if rec is not None:
            ex[r["instance_id"]] = rec
    return ex


def match_stats(items: list[dict], ex: dict[str, dict], ref_text: dict[str, str]) -> dict:
    """Extracted state against the canonical state of the same item (all attempted: missing/invalid = wrong)."""
    c, rows = Counter(), []
    for r in items:
        rec, ok = ex.get(r["instance_id"]), False
        if rec is None:
            c["missing"] += 1
        elif rec.get("parsed") is None:
            c["invalid"] += 1
            c[f"invalid:{str(rec.get('parse_error'))[:40]}"] += 1
        else:
            try:
                m = compare(state_from_extraction(rec["parsed"]), parse_state(ref_text[r["instance_id"]], opaque_tasks=True))
                ok = m["exact"]
                for f in ("variables", "rules", "known", "actions"):
                    c[f"wrong_{f}"] += m[f] is not True
            except Exception as e:
                c[f"invalid:{type(e).__name__}"] += 1
                c["invalid"] += 1
        rows.append((r["family_id"], float(ok)))
    return {"exact": cluster_mean_ci(rows), "counts": dict(c)}


def analyze(items: list[dict], base: list[dict], keys: list[str], raw: Path) -> dict:
    base_by = {r["instance_id"]: r for r in base}
    base_ids = list(base_by)
    ref_text = {r["instance_id"]: base_by[r["robust"]["of"]]["prompt_text"] for r in items}
    ref_text.update({i: r["prompt_text"] for i, r in base_by.items()})
    by_kind = {k: [r for r in items if r["robust"]["kind"] == k] for k in KINDS}
    out = {"families": len({r["family_id"] for r in base}), "base_items": len(base), "extraction_v3": EXTRACTION_VERSION_V3,
           "models": {}, "parser_P": {}}

    def rows_for(recs: list[dict], results: list[dict]) -> dict:
        by = {r["instance_id"]: r for r in recs}
        return score(by, results, list(by))

    canon_p = rows_for(base, planned_results(base, None)[0])
    out["parser_P"]["canonical"] = summarize(canon_p)
    p_rows = {}
    for kind, recs in by_kind.items():
        p_res, p_stats = planned_results(recs, None)
        p_rows[kind] = rows_for(recs, p_res)
        exact = []
        for r in recs:
            try:
                ok = compare(parse_state(r["prompt_text"], opaque_tasks=True), parse_state(ref_text[r["instance_id"]], opaque_tasks=True))["exact"]
            except Exception:
                ok = False
            exact.append((r["family_id"], float(ok)))
        out["parser_P"][kind] = {**summarize(p_rows[kind]), "pipeline": p_stats, "state_exact": cluster_mean_ci(exact)}

    def paired(x: dict, y: dict, ids_x: list[str], to_y, key: str, pool_p: list | None = None) -> dict:
        pairs = [(x[i]["family_id"], float(bool(x[i].get(key))), float(bool(y[to_y(i)].get(key))))
                 for i in ids_x if x[i]["gold_class"] in RESOLVABLE] if key != "stop_ok" else \
                [(x[i]["family_id"], float(bool(x[i]["stop_ok"])), float(bool(y[to_y(i)]["stop_ok"])))
                 for i in ids_x if x[i].get("stop_ok") is not None]
        if pool_p is not None:
            pool_p += pairs
        return paired_diff_ci(pairs)

    pvals = {}
    for k in keys:
        fz = frozen(k)
        m = {"frozen_extraction": fz, "usage": {}, "canonical": {}, "kinds": {}}
        a_can = [r for r in load_results(raw, "plan", k) if r["instance_id"] in base_by and r["mode"] == E2E.value]
        b_can = [r for r in load_results(raw, "plan_s1", k) if r["instance_id"] in base_by and r["mode"] == E2E.value]
        bt = any(r.get("parse_error") == "no text" and r.get("status") == "ok" for r in b_can)
        if bt:
            b_can = message_text_results(b_can)
        ex_can = extractions(base, *CANON_EXTRACT[fz], k, raw)
        can = {"A": rows_for(base, a_can), "B": rows_for(base, b_can),
               "EOP": rows_for(base, planned_results(base, ex_can)[0]), "P": canon_p}
        m["canonical"] = {c: summarize(rw) for c, rw in can.items()}
        m["canonical"]["EOP_extraction"] = match_stats(base, ex_can, ref_text)
        m["B_from_message_text"] = bt
        pooled = {c: [] for c in ("EOP-A", "EOPN-A", "EOP-B", "EOP-P")}
        for kind, recs in by_kind.items():
            ids = [r["instance_id"] for r in recs]
            of = lambda i: i.rsplit("-rb-", 1)[0]  # noqa: E731
            a_res = [r for r in load_results(raw, "plan_rb", k) if r["instance_id"] in ids]
            b_res = [r for r in load_results(raw, "plan_rbs1", k) if r["instance_id"] in ids]
            if bt or any(r.get("parse_error") == "no text" and r.get("status") == "ok" for r in b_res):
                b_res = message_text_results(b_res)
            ex = extractions(recs, *EXTRACT[fz], k, raw)
            ex3 = extractions(recs, *EXTRACT["s3v3"], k, raw)
            e_res, e_stats = planned_results(recs, ex)
            n_res, n_stats = planned_results(recs, ex3)
            rows = {"A": rows_for(recs, a_res), "B": rows_for(recs, b_res), "EOP": rows_for(recs, e_res),
                    "EOPN": rows_for(recs, n_res), "P": p_rows[kind]}
            km = {"conditions": {c: summarize(rw) for c, rw in rows.items()},
                  "extraction": {"EOP": match_stats(recs, ex, ref_text), "EOPN": match_stats(recs, ex3, ref_text)},
                  "pipeline": {"EOP": e_stats, "EOPN": n_stats}, "paired": {}}
            for key in ("plan_optimal", "plan_sufficient", "stop_ok"):
                for c in ("A", "B", "EOP", "P"):
                    km["paired"][f"{c}: variant-canonical|{key}"] = paired(rows[c], can[c], ids, of, key)
                km["paired"][f"EOPN: variant-canonical EOP|{key}"] = paired(rows["EOPN"], can["EOP"], ids, of, key)
                same = lambda i: i  # noqa: E731
                for x, y in (("EOP", "A"), ("EOPN", "A"), ("EOP", "B"), ("EOP", "P"), ("EOPN", "EOP"), ("B", "A")):
                    pp = pooled.get(f"{x}-{y}") if key == "plan_optimal" else None
                    km["paired"][f"{x}-{y}|{key}"] = paired(rows[x], rows[y], ids, same, key, pp)
            m["kinds"][kind] = km
        m["pooled_optimal"] = {c: {**paired_diff_ci(p), "n": len(p)} for c, p in pooled.items()}
        pvals[k] = one_sided_p(pooled["EOP-A"])
        m["usage"] = {c: usage(raw, pool, k, {r["instance_id"] for r in items})
                      for c, pool in (("A", "plan_rb"), ("B", "plan_rbs1"), ("EOP", EXTRACT[fz][0]), ("EOPN", "extract_rbv3"))}
        out["models"][k] = m
    h = holm({k: p for k, p in pvals.items() if p is not None})
    out["registered_test_EOP_minus_A_optimal_pooled"] = {k: {"p": pvals[k], "holm_p": h.get(k)} for k in pvals}
    return out


def render(s: dict) -> str:
    f = lambda d: "n/a" if not d or d.get("mean") is None else f"{d['mean']:.2f}"  # noqa: E731
    g = lambda d: "n/a" if not d or d.get("mean") is None else f"{d['mean']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]"  # noqa: E731
    lines = ["# Linguistic robustness (dev, 18 families, 137 states, End-to-End)", "",
             "All attempted; unparsed, invalid or failed = incorrect. Optimal-plan rate on resolvable states; "
             "`state` = extracted state exactly equal to the canonical state.", ""]
    for k, m in s["models"].items():
        lines += [f"## {k} (frozen extraction: {m['frozen_extraction']})", "",
                  "| wording | A native | B structured | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P parser optimal | EOP − A | EOP variant − canonical |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        c = m["canonical"]
        lines.append(f"| canonical | {f(c['A']['optimal_all'])} | {f(c['B']['optimal_all'])} | {f(c['EOP']['optimal_all'])} | "
                     f"{f(c['EOP_extraction']['exact'])} | | | {f(c['P']['optimal_all'])} | | |")
        for kind, km in m["kinds"].items():
            cc = km["conditions"]
            lines.append(f"| {kind} | {f(cc['A']['optimal_all'])} | {f(cc['B']['optimal_all'])} | {f(cc['EOP']['optimal_all'])} | "
                         f"{f(km['extraction']['EOP']['exact'])} | {f(cc['EOPN']['optimal_all'])} | {f(km['extraction']['EOPN']['exact'])} | "
                         f"{f(cc['P']['optimal_all'])} | {g(km['paired']['EOP-A|plan_optimal'])} | "
                         f"{g(km['paired']['EOP: variant-canonical|plan_optimal'])} |")
        t = s["registered_test_EOP_minus_A_optimal_pooled"][k]
        lines += ["", f"Pooled over the four wordings: EOP − A {g(m['pooled_optimal']['EOP-A'])}, one-sided p {t['p']}, "
                      f"Holm p {t['holm_p']}; EOP-N − A {g(m['pooled_optimal']['EOPN-A'])}; EOP − P {g(m['pooled_optimal']['EOP-P'])}.", ""]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--items", default=str(ROOT / "data" / "generated" / "robust_v1" / "items.jsonl"))
    ap.add_argument("--models", required=True)
    ap.add_argument("--conditions", default="frozen,s3v3,a,s1",
                    help="calls to make, in order: frozen (the model's frozen extraction), s3v3, a, s1")
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "robust_dev"))
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--assumed-output-tokens", type=int, default=4000)
    ap.add_argument("--budget", type=float, default=0.0, help="cap on the cumulative ledger total (credits)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    a = ap.parse_args(argv)
    load_env(ROOT / ".env")
    items = [json.loads(l) for l in open(a.items)]
    if any(r["split"] != "dev" for r in items):
        print("robustness items must be dev items")
        return 2
    keys = [k.strip() for k in a.models.split(",")]
    models = load_models(Path(a.models_config))
    raw = Path(a.raw)
    conds = [c.strip() for c in a.conditions.split(",") if c.strip()]
    print(f"robustness study: {len(items)} variant items; conditions {conds}")
    if a.dry_run:
        for k in keys:
            for c in conds:
                c = frozen(k) if c == "frozen" else c
                print(k, c, estimate(jobs_for(items, c), models[k].get("prices") or {}, a.assumed_output_tokens))
        return 0
    if not a.analyze_only:
        if a.budget <= 0 or a.max_calls <= 0:
            print("pass --budget (cumulative ledger cap) and --max-calls; no calls made")
            return 2
        cur = currency(models[keys[0]])
        ledger = Ledger(raw / ("spend_ledger.jsonl" if cur == "usd" else f"spend_ledger_{cur}.jsonl"), a.budget)
        print(f"budget {a.budget:.4f}; already spent {ledger.spent:.4f}")
        for k in keys:
            for c in conds:
                c = frozen(k) if c == "frozen" else c
                print(k, c, run_jobs(jobs_for(items, c), k, models[k], raw, max_calls=a.max_calls,
                                     concurrency=a.concurrency, ledger=ledger))
        print(f"cumulative spend {ledger.spent:.4f} of {a.budget:.4f}")
        return 0
    ids = {r["robust"]["of"] for r in items}
    base = [r for r in pilot.load_records(Path(a.data), ("dev",), None) if r["instance_id"] in ids]
    summary = analyze(items, base, keys, raw)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "robust_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    (out / "robust_report.md").write_text(render(summary))
    print(f"wrote {out / 'robust_summary.json'} and robust_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
