"""Registered EOP comparison (PREREG_EOP.md): A native vs B structured prompt vs C realistic EOP vs D verifier.

Item sets (dev only): v3dev (all 72 families; End-to-End and Detection-Controlled), t1pilot (families 11-30),
t1b (families 31-72). One extraction per state (C, D); B is run per eligible mode.

  A  native   : existing responses (pools plan / plan_t1); no new calls
  B  s1       : structured obligation prompt (models/prompts_s1.py); pools plan_s1 / plan_t1s1
  C  s3       : LLM extraction of the visible state (pools extract / extract_t1) + realistic planner
  D  s2       : B's plan verified on C's extracted state, unnecessary actions removed, nothing added
  U  upper    : planner on the exact rule-based parse (not a mitigation)

The planner sees only the prompt text (through the extraction): never oracle labels, latent world, true
values or unexecuted COMPUTE results (tests/test_eop_driver.py).

    python experiments/run_eop.py --items v3dev,t1b,t1pilot --models M --dry-run
    python experiments/run_eop.py --items v3dev,t1b,t1pilot --models M --budget CAP --max-calls N
    python experiments/run_eop.py --items v3dev,t1b,t1pilot --models M1,M2 --analyze-only
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_t1  # noqa: E402

from msep.controllers.llm_extractor import extraction_prompt, extraction_prompt_v2, state_from_extraction  # noqa: E402
from msep.controllers.realistic_planner import (EpistemicObligationPlanner, ExactObligations,  # noqa: E402
                                                ParserExtractor, SufficiencyChecker)
from msep.envfile import load_env  # noqa: E402
from msep.eval import pilot  # noqa: E402
from msep.eval.bootstrap import cluster_mean_ci, holm, paired_diff_ci  # noqa: E402
from msep.models.config_check import currency  # noqa: E402
from msep.models.prompts import Mode, build_prompt, eligible  # noqa: E402
from msep.models.prompts_s1 import S1_VERSION, s1_prompt  # noqa: E402
from msep.models.runner import Job, _parse, estimate, latest_record, load_models, load_results, run_jobs  # noqa: E402
from msep.models.spend import Ledger  # noqa: E402
from msep.obligations.discharge import discharges  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESOLVABLE = ("INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH")
SETS = {  # name: (A pool, B pool, C pool, modes, is_t1)
    "v3dev": ("plan", "plan_s1", "extract", (Mode.END_TO_END, Mode.DETECTION_CONTROLLED), False),
    "t1pilot": ("plan_t1", "plan_t1s1", "extract_t1", (Mode.END_TO_END,), True),
    "t1b": ("plan_t1", "plan_t1s1", "extract_t1", (Mode.END_TO_END,), True),
    # held-out test split (PREREG_FINAL.md); refused unless --allow-test
    "v3test": ("plan", "plan_s1", "extract", (Mode.END_TO_END, Mode.DETECTION_CONTROLLED), False),
    "t1test": ("plan_t1", "plan_t1s1", "extract_t1", (Mode.END_TO_END,), True),
}
# Amendment 1 (PREREG_EOP.md): condition C' = extraction prompt v2 (explicit JSON layout); D' = B verified on C'
C2_POOL = {"v3dev": "extract_v2", "t1pilot": "extract_t1v2", "t1b": "extract_t1v2",
           "v3test": "extract_v2", "t1test": "extract_t1v2"}


def load_items(name: str, data: Path, t1: Path) -> list[dict]:
    if name == "v3dev":
        return pilot.load_records(data, ("dev",), None)
    if name == "t1pilot":
        return analyze_t1.select_t1(data, t1, ("dev",), 10, 20)
    if name == "t1b":
        return analyze_t1.select_t1(data, t1, ("dev",), 30, None)
    if name == "v3test":
        return pilot.load_records(data, ("test",), None)
    if name == "t1test":
        fams = {r["family_id"] for r in pilot.load_records(data, ("test",), None)}
        return [v for v in (json.loads(l) for l in open(t1)) if v["family_id"] in fams and v["split"] == "test"]
    raise ValueError(name)


def jobs_for(items: list[dict], name: str, cond: str) -> list[Job]:
    _, bpool, cpool, modes, _ = SETS[name]
    out = []
    for r in items:
        rc = r["oracle"]["resource_class"]
        if cond == "s1":
            out += [Job(bpool, r["instance_id"], r["family_id"], m.value, s1_prompt(build_prompt(r["prompt_text"], m, rc)))
                    for m in modes if eligible(m, rc)]
        elif cond == "s3":
            out.append(Job(cpool, r["instance_id"], r["family_id"], "extraction", extraction_prompt(r["prompt_text"])))
        elif cond == "s3v2":
            out.append(Job(C2_POOL[name], r["instance_id"], r["family_id"], "extraction",
                           extraction_prompt_v2(r["prompt_text"])))
    return out


# -- planning from an extraction (C) and verification of B's plan (D) ---------------------------

class _Fixed:
    def __init__(self, state):
        self.state = state

    def extract(self, text):
        return self.state


def _response(state, sufficient: bool, decision, plan) -> tuple[dict | None, str | None]:
    if sufficient:
        resp = {"state_sufficient": True, "resource_class": "ALREADY_SUFFICIENT", "plan": [],
                "decision": "true" if decision else "false"}
    elif plan is None:
        resp = {"state_sufficient": False, "resource_class": "NEITHER", "plan": [], "decision": "defer"}
    else:
        kinds = {state.action_index[n].resource.value for n in plan}
        rc = ("BOTH" if len(kinds) == 2 else "INFORMATION_ONLY" if kinds == {"information"} else
              "COMPUTATION_ONLY" if kinds else "NEITHER")
        resp = {"state_sufficient": False, "resource_class": rc, "decision": "defer",
                "plan": [{"type": "ASK" if state.action_index[n].resource.value == "information" else "COMPUTE",
                          "action": n} for n in plan]}
    resp.update({"stop_after_plan": True, "confidence": 1.0, "short_justification": "epistemic obligation planner"})
    return _parse("plan", json.dumps(resp))


def plan_to_parsed(state, out: dict) -> tuple[dict | None, str | None]:
    if not out.get("supported"):
        return None, "unsupported decision rule"
    return _response(state, out["state_sufficient"], out.get("decision"), out["plan"])


def message_text_results(b_res: list[dict]) -> list[dict]:
    """Amendment 2 (analysis only): when a forced-schema answer made no function call, parse the JSON the model
    wrote in its message text with the standard plan parser. Unchanged where the call was made."""
    out = []
    for r in b_res:
        if r.get("parsed") is None and r.get("parse_error") == "no text":
            txt = " ".join(c.get("text", "") for i in (r.get("raw_response") or {}).get("output") or []
                           if i.get("type") == "message" for c in i.get("content") or [])
            parsed, err = _parse("plan", txt) if txt.strip() else (None, "no text")
            r = {**r, "parsed": parsed, "parse_error": err}
        out.append(r)
    return out


def state_of(ex: dict | None):
    if ex is None or ex.get("parsed") is None:
        return None
    return state_from_extraction(ex["parsed"])


def planned_results(items: list[dict], extractions: dict[str, dict] | None) -> tuple[list[dict], dict]:
    """C (or U when extractions is None): one plan per state, mode-independent."""
    res, stats, secs = [], Counter(), []
    for r in items:
        base = {"instance_id": r["instance_id"], "family_id": r["family_id"], "mode": "end_to_end"}
        try:
            if extractions is None:
                state = ParserExtractor().extract(r["prompt_text"])
            else:
                ex = extractions.get(r["instance_id"])
                if ex is None or ex.get("parsed") is None:
                    stats["extraction_failed" if ex is not None else "extraction_missing"] += 1
                    res.append({**base, "parsed": None, "status": (ex or {}).get("status", "missing")})
                    continue
                state = state_from_extraction(ex["parsed"])
            t0 = time.perf_counter()
            out = EpistemicObligationPlanner(extractor=_Fixed(state)).plan(r["prompt_text"])
            secs.append(time.perf_counter() - t0)
            parsed, err = plan_to_parsed(state, out)
            if err:
                stats["planner_output_unscorable"] += 1
            res.append({**base, "parsed": parsed, "status": "ok"})
        except Exception as e:  # inconsistent extracted state, unknown handle, solver error
            stats[f"planner_error:{type(e).__name__}"] += 1
            res.append({**base, "parsed": None, "status": "planner_error"})
    stats["planner_seconds_mean"] = round(sum(secs) / len(secs), 4) if secs else None
    return res, dict(stats)


def verified_results(b_results: list[dict], extractions: dict[str, dict]) -> tuple[list[dict], dict]:
    """D: prune B's plan with the obligations of C's extracted state; never add actions."""
    out, stats = [], Counter()
    for b in b_results:
        base = {"instance_id": b["instance_id"], "family_id": b["family_id"], "mode": b["mode"]}
        ex = extractions.get(b["instance_id"])
        if b.get("parsed") is None or ex is None or ex.get("parsed") is None:
            stats["b_unparsed" if b.get("parsed") is None else "extraction_failed_or_missing"] += 1
            out.append({**base, "parsed": None, "status": "d_input_missing"})
            continue
        try:
            state = state_from_extraction(ex["parsed"])
            decided = SufficiencyChecker().decided(state)
            if decided is not None:
                parsed, _ = _response(state, True, decided, ())
                stats["decided_emptied" if b["parsed"]["plan"] else "decided_kept_empty"] += 1
            else:
                obs = ExactObligations().identify(state)
                kept = [n for n in b["parsed"]["plan"] if n in state.action_index and
                        any(discharges(state, state.action_index[n], o) for o in obs)]
                stats["actions_removed"] += len(b["parsed"]["plan"]) - len(kept)
                parsed, _ = _response(state, False, None, tuple(kept))
            out.append({**base, "parsed": parsed, "status": "ok"})
        except Exception as e:
            stats[f"verifier_error:{type(e).__name__}"] += 1
            out.append({**base, "parsed": None, "status": "verifier_error"})
    return out, dict(stats)


# -- metrics ------------------------------------------------------------------------------------

def _ok_stop(row: dict, rec: dict) -> bool | None:
    rc = rec["oracle"]["resource_class"]
    if rc == "ALREADY_SUFFICIENT":
        return bool(row.get("valid")) and not row.get("plan_formal") and \
            row.get("decision") == ("true" if rec["true_target_value"] else "false")
    if rc == "NEITHER":
        return bool(row.get("valid")) and row.get("decision") == "defer"
    return None


def score(items_by_id: dict, results: list[dict], eligible_ids: list[str]) -> dict[str, dict]:
    have = {r["instance_id"] for r in results}
    rows = {r["instance_id"]: r for r in pilot.score_plan_results(items_by_id, results) if r["instance_id"] in eligible_ids}
    for i in eligible_ids:
        if i not in have:
            rec = items_by_id[i]
            rows[i] = {"instance_id": i, "family_id": rec["family_id"], "gold_class": rec["oracle"]["resource_class"],
                       "valid": False, "plan_sufficient": False, "plan_optimal": False, "class_correct": False}
    for i, row in rows.items():
        row["stop_ok"] = _ok_stop(row, items_by_id[i])
    return rows


def summarize(rows: dict[str, dict]) -> dict:
    rs = list(rows.values())
    res = [r for r in rs if r["gold_class"] in RESOLVABLE]
    par = [r for r in res if r["valid"]]
    suff = [r for r in par if r.get("plan_sufficient")]
    ci = lambda xs, key: cluster_mean_ci((r["family_id"], bool(r.get(key))) for r in xs)  # noqa: E731
    stop = [r for r in rs if r.get("stop_ok") is not None]
    return {"n_items": len(rs), "n_resolvable": len(res), "unparsed_items": sum(not r["valid"] for r in rs),
            "unparsed_resolvable": len(res) - len(par),
            "optimal_all": ci(res, "plan_optimal"), "sufficient_all": ci(res, "plan_sufficient"),
            "optimal_parsed": ci(par, "plan_optimal"), "sufficient_parsed": ci(par, "plan_sufficient"),
            "unnecessary_action_rate": cluster_mean_ci((r["family_id"], not r.get("plan_minimal")) for r in suff),
            "regret_parsed": cluster_mean_ci((r["family_id"], float(r["regret"])) for r in par if r.get("regret") is not None),
            "class_acc_all": ci(rs, "class_correct"),
            "stop_ok_AS_NEITHER": cluster_mean_ci((r["family_id"], bool(r["stop_ok"])) for r in stop)}


def one_sided_p(pairs, reps=10_000, seed=0) -> float | None:
    by = defaultdict(list)
    for f, a, b in pairs:
        by[f].append(a - b)
    fams = sorted(by)
    if len(fams) < 2:
        return None
    rng = random.Random(seed)
    le = 0
    for _ in range(reps):
        s = [x for f in (rng.choice(fams) for _ in fams) for x in by[f]]
        le += (sum(s) / len(s)) <= 0
    return le / reps


def usage(raw: Path, pool: str, key: str, ids: set[str]) -> dict:
    recs = [r for r in load_results(raw, pool, key) if r["instance_id"] in ids]
    if not recs:
        return {}
    n = len(recs)
    return {"responses": n, "status": dict(Counter(r["status"] for r in recs)),
            "parse_errors": sum(bool(r["parse_error"]) for r in recs),
            "input_tokens_mean": round(sum(r["tokens"]["input_tokens"] for r in recs) / n),
            "output_tokens_mean": round(sum(r["tokens"]["output_tokens"] for r in recs) / n),
            "seconds_mean": round(sum(r["seconds"] for r in recs) / n, 1),
            "cost_total": round(sum(r["cost_usd"] or 0 for r in recs), 4),
            "served_models": dict(Counter(r.get("served_model") for r in recs))}


def analyze_set(name: str, items: list[dict], keys: list[str], raw: Path) -> dict:
    apool, bpool, cpool, modes, is_t1 = SETS[name]
    by_id = {r["instance_id"]: r for r in items}
    ids = set(by_id)
    out = {"items": len(items), "families": len({r["family_id"] for r in items}), "models": {}}
    upper, ustats = planned_results(items, None)
    out["upper_bound_parser_EOP"] = {"pipeline": ustats}
    for mode in modes:
        elig = [i for i, r in by_id.items() if eligible(mode, r["oracle"]["resource_class"])]
        out["upper_bound_parser_EOP"][mode.value] = summarize(score(by_id, upper, elig))
    for k in keys:
        ex = {}
        for r in items:
            rec = latest_record(raw, Job(cpool, r["instance_id"], r["family_id"], "extraction",
                                         extraction_prompt(r["prompt_text"])), k)
            if rec is not None:
                ex[r["instance_id"]] = rec
        c_res, c_stats = planned_results(items, ex)
        ex2 = {}
        for r in items:
            rec = latest_record(raw, Job(C2_POOL[name], r["instance_id"], r["family_id"], "extraction",
                                         extraction_prompt_v2(r["prompt_text"])), k)
            if rec is not None:
                ex2[r["instance_id"]] = rec
        c2_res, c2_stats = planned_results(items, ex2) if ex2 else ([], {})
        m_out = {"usage": {"A": usage(raw, apool, k, ids), "B": usage(raw, bpool, k, ids), "C_extraction": usage(raw, cpool, k, ids),
                           "C2_extraction": usage(raw, C2_POOL[name], k, ids)},
                 "pipeline_C": c_stats, "pipeline_C2": c2_stats}
        for mode in modes:
            elig = [i for i, r in by_id.items() if eligible(mode, r["oracle"]["resource_class"])]
            a_res = [r for r in load_results(raw, apool, k) if r["instance_id"] in ids and r["mode"] == mode.value]
            b_res = [r for r in load_results(raw, bpool, k) if r["instance_id"] in ids and r["mode"] == mode.value]
            d_res, d_stats = verified_results(b_res, ex)
            # missing B answers are D failures too (scored as missing below)
            cm = [{**r, "mode": mode.value} for r in c_res]
            rows = {"A": score(by_id, a_res, elig), "B": score(by_id, b_res, elig),
                    "C": score(by_id, cm, elig), "D": score(by_id, d_res, elig)}
            if any(r.get("parse_error") == "no text" and r.get("status") == "ok" for r in b_res):
                bt_res = message_text_results(b_res)
                rows["Bt"] = score(by_id, bt_res, elig)
                rows["Dt"] = score(by_id, verified_results(bt_res, ex)[0], elig)
            d2_stats = {}
            if ex2:
                d2_res, d2_stats = verified_results(b_res, ex2)
                rows["C2"] = score(by_id, [{**r, "mode": mode.value} for r in c2_res], elig)
                rows["D2"] = score(by_id, d2_res, elig)
            mm = {c: summarize(rws) for c, rws in rows.items() if any(r["valid"] for r in rws.values()) or c == "A"}
            diffs = {}
            for x, y in (("C", "A"), ("C", "B"), ("B", "A"), ("D", "A"), ("C", "D"), ("D", "B"),
                         ("C2", "A"), ("C2", "B"), ("C2", "C"), ("D2", "A"), ("C2", "D2"), ("D2", "B"),
                         ("C", "Bt"), ("Bt", "A"), ("Dt", "A"), ("C", "Dt"), ("Dt", "Bt")):
                if x in mm and y in mm:
                    for key in ("plan_optimal", "plan_sufficient"):
                        pairs = [(rows[x][i]["family_id"], float(bool(rows[x][i].get(key))), float(bool(rows[y][i].get(key))))
                                 for i in elig if by_id[i]["oracle"]["resource_class"] in RESOLVABLE]
                        diffs[f"{x}-{y}|{key}"] = {**paired_diff_ci(pairs), "p_one_sided_le0": one_sided_p(pairs)
                                                   if (y, key, mode.value) == ("A", "plan_optimal", "detection_controlled") and x in ("C", "C2") else None}
                    stop_pairs = [(rows[x][i]["family_id"], float(bool(rows[x][i]["stop_ok"])), float(bool(rows[y][i]["stop_ok"])))
                                  for i in elig if rows[x][i].get("stop_ok") is not None]
                    diffs[f"{x}-{y}|stop_ok"] = paired_diff_ci(stop_pairs)
            m_out[mode.value] = {"conditions": mm, "paired": diffs, "pipeline_D": d_stats, "pipeline_D2": d2_stats}
            if is_t1 and mode is Mode.END_TO_END:
                extra = (("C2", [{**r, "mode": mode.value} for r in c2_res]), ("D2", d2_res)) if ex2 else ()
                m_out[mode.value]["t1_pairs"] = {c: analyze_t1.analyze(analyze_t1.pair_rows(items, res))["all"]
                                                 for c, res in (("A", a_res), ("B", b_res), ("C", cm), ("D", d_res)) + extra
                                                 if res}
        out["models"][k] = m_out
    if name == "v3dev":
        ps = {k: v["detection_controlled"]["paired"].get("C-A|plan_optimal", {}).get("p_one_sided_le0")
              for k, v in out["models"].items()}
        h = holm({k: p for k, p in ps.items() if p is not None})
        out["confirmatory_C_minus_A_optimal_DC"] = {k: {"p": ps[k], "holm_p": h.get(k)} for k in ps}
    if name == "v3test":  # PREREG_FINAL.md F1: frozen EOP configuration per model (C2 where run, else C) minus A
        cmp = {k: ("C2-A" if "C2" in v["detection_controlled"]["conditions"] else "C-A") for k, v in out["models"].items()}
        ps = {k: v["detection_controlled"]["paired"].get(f"{cmp[k]}|plan_optimal", {}).get("p_one_sided_le0")
              for k, v in out["models"].items()}
        h = holm({k: p for k, p in ps.items() if p is not None})
        out["confirmatory_final_EOP_minus_A_optimal_DC"] = {k: {"comparison": cmp[k], "p": ps[k], "holm_p": h.get(k)} for k in ps}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl"))
    ap.add_argument("--t1", default=str(ROOT / "data" / "generated" / "t1_v1" / "pairs.jsonl"))
    ap.add_argument("--items", default="v3dev,t1b,t1pilot")
    ap.add_argument("--models", required=True)
    ap.add_argument("--conditions", default="s3,s1",
                    help="calls to make: s3 (extraction v1), s1 (structured prompt), s3v2 (extraction v2, Amendment 1)")
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "eop_dev"))
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--assumed-output-tokens", type=int, default=4000)
    ap.add_argument("--budget", type=float, default=0.0, help="cap on the cumulative ledger total (credits)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    ap.add_argument("--allow-test", action="store_true", help="held-out test sets (v3test, t1test): final run only")
    a = ap.parse_args(argv)
    load_env(ROOT / ".env")
    sets = [s.strip() for s in a.items.split(",") if s.strip()]
    keys = [k.strip() for k in a.models.split(",")]
    conds = [c.strip() for c in a.conditions.split(",") if c.strip()]
    if any(s.endswith("test") for s in sets) and not a.allow_test:
        print("refusing the test split (frozen final evaluation); pass --allow-test only for that run")
        return 2
    models = load_models(Path(a.models_config))
    raw = Path(a.raw)
    items = {s: load_items(s, Path(a.data), Path(a.t1)) for s in sets}
    print(f"EOP comparison ({S1_VERSION}); sets {[(s, len(v)) for s, v in items.items()]}; conditions {conds}")
    if a.dry_run:
        for k in keys:
            for s in sets:
                for c in conds:
                    print(k, s, c, estimate(jobs_for(items[s], s, c), models[k].get("prices") or {}, a.assumed_output_tokens))
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
                for s in sets:
                    jobs = jobs_for(items[s], s, c)
                    run_jobs(jobs[:1], k, models[k], raw, max_calls=1, ledger=ledger)  # smoke
                    rec = latest_record(raw, jobs[0], k)
                    print(f"smoke {k} {s} {c}: status={rec and rec['status']} parse_error={rec and rec['parse_error']}")
                    if rec is None or rec["status"] == "error":
                        print("smoke failed: skipping this model/set/condition")
                        continue
                    print(k, s, c, run_jobs(jobs, k, models[k], raw, max_calls=a.max_calls, concurrency=a.concurrency,
                                            ledger=ledger))
        print(f"cumulative spend {ledger.spent:.4f} of {a.budget:.4f}")
        return 0
    summary = {s: analyze_set(s, items[s], keys, raw) for s in sets}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "eop_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(f"wrote {out / 'eop_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
