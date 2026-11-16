"""Study 3 (PREREG_REPAIR.md): can one diagnostic repair call recover extractions that the reader rejects?

Reworded states from train families never sent to a model. Two extraction prompts (F: the model's frozen EOP
prompt; N: the translating prompt v3 of the rewording study), each with and without one repair call. A repair call
is made only for a first answer that the reader rejects; it shows the model its first answer and the reader's
message. The exact planner is unchanged.

    python experiments/run_repair.py --generate
    python experiments/run_repair.py --stage 1 --models KEY --concurrency 8 --max-calls 800 --budget CAP
    python experiments/run_repair.py --stage 2 --models KEY --concurrency 8 --max-calls 800 --budget CAP
    python experiments/run_repair.py --analyze-only --models KEY1,KEY2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_robust import check, variants_of  # noqa: E402
from msep.benchmark.parsing import parse_state  # noqa: E402
from msep.controllers.extraction_v3 import INSTRUCTIONS_V3, extraction_prompt_v3  # noqa: E402
from msep.controllers.llm_extractor import extraction_prompt, extraction_prompt_v2, state_from_extraction  # noqa: E402
from msep.envfile import load_env  # noqa: E402
from msep.eval.bootstrap import cluster_mean_ci, paired_diff_ci  # noqa: E402
from msep.eval.extraction_match import compare  # noqa: E402
from msep.models.config_check import check_all, currency  # noqa: E402
from msep.models.runner import Job, _parse, latest_record, load_models, run_jobs  # noqa: E402
from msep.models.spend import Ledger  # noqa: E402
from run_eop import planned_results, score, summarize  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data/generated/pool_v3/instances.jsonl"
DATA = ROOT / "data/generated/repair_v1/items.jsonl"
FAMILIES, KINDS = 12, ("syntax", "prose")
GEMMA = "adaption-gemma-4-26b-a4b-it-schema"
ARMS = ("F", "N")
RULES_NOTE = ("\nEach entry of \"rules\" must be one formula in the notation above and nothing else: no other words, no "
              "explanation, no trailing text. Use only the handles listed in \"variables\", and Q.")


def first_prompt(arm: str, key: str, text: str) -> str:
    if arm == "N":
        return extraction_prompt_v3(text)
    return extraction_prompt(text) if key == GEMMA else extraction_prompt_v2(text)  # the frozen prompt of each model


def repair_prompt(text: str, first_answer: str, message: str) -> str:
    return (text + "\n\nA first attempt to extract the formal state from the problem above was rejected by an automatic "
            "reader.\n\nFirst attempt:\n" + (first_answer.strip()[:6000] or "(no answer was returned)")
            + "\n\nThe reader's message: " + message + "\n\nWrite the extraction again so that the reader accepts it.\n"
            + INSTRUCTIONS_V3 + RULES_NOTE)


def answer_text(rec: dict) -> str:
    """The answer as text: the function-call arguments if a call was made, otherwise the message text."""
    if rec.get("text"):
        return rec["text"]
    return " ".join(c.get("text", "") for i in (rec.get("raw_response") or {}).get("output") or []
                    if i.get("type") == "message" for c in i.get("content") or [])


def read(rec: dict | None, strict: bool = False) -> tuple[dict | None, str]:
    """The reader's verdict on one answer: (extraction, '') if accepted, (None, message) if rejected.
    strict: only the runner's own reading (function-call text), as in the earlier studies."""
    if rec is None:
        return None, "missing"
    if rec.get("parsed") is not None:
        return rec["parsed"], ""
    if rec.get("status") not in ("ok", "truncated"):
        return None, f"call failed: {rec.get('status')}"
    if strict:
        return None, str(rec.get("parse_error"))
    text = answer_text(rec)
    if not text.strip():
        return None, "no answer text"
    d, err = _parse("extract", text)
    return d, (err or "")


def items() -> list[dict]:
    return [json.loads(l) for l in open(DATA)]


def job1(arm: str, key: str, r: dict) -> Job:
    return Job(f"extract_fx{arm}", r["instance_id"], r["family_id"], "extraction", first_prompt(arm, key, r["prompt_text"]))


def job2(arm: str, key: str, r: dict, raw: Path) -> Job | None:
    """The repair job of an item, or None if its first answer was accepted, is missing or failed as a call."""
    rec = latest_record(raw, job1(arm, key, r), key)
    d, msg = read(rec)
    if d is not None or rec is None or msg.startswith("call failed"):
        return None
    return Job(f"extract_fx{arm}r", r["instance_id"], r["family_id"], "extraction",
               repair_prompt(r["prompt_text"], answer_text(rec), msg))


def generate() -> int:
    recs = [json.loads(l) for l in open(POOL)]
    train = sorted({r["family_id"] for r in recs if r["split"] == "train"})
    used = set(train[:60]) | {json.loads(l)["family_id"] for l in open(ROOT / "data/generated/followup_v1/cost.jsonl")}
    fams = [f for f in train if f not in used][:FAMILIES]
    out, n = [], Counter()
    for rec in recs:
        if rec["family_id"] not in fams:
            continue
        for v, blocks in variants_of(rec):
            if v["robust"]["kind"] not in KINDS:
                continue
            c = check(rec, v, blocks)
            assert c["inverse_exact"] and c["names_present"] and c["differs_from_canonical"], v["instance_id"]
            out.append({**v, "canonical_text": rec["prompt_text"]})
            n[v["robust"]["kind"]] += 1
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in out))
    man = {"generator": "repair-v1", "split": "train", "families": fams, "states": len(out) // len(KINDS), "items": len(out),
           "items_by_wording": dict(n), "states_by_class": dict(Counter(r["oracle"]["resource_class"] for r in out
                                                                        if r["robust"]["kind"] == KINDS[0])),
           "sha256": hashlib.sha256(DATA.read_bytes()).hexdigest()}
    (ROOT / "data/repair_v1_manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    print(json.dumps(man, indent=1))
    return 0


# -- analysis ---------------------------------------------------------------------------------------

def analyze_arm(its: list[dict], arm: str, key: str, raw: Path) -> dict:
    by = {r["instance_id"]: r for r in its}
    ref = {r["instance_id"]: parse_state(r["canonical_text"], opaque_tasks=True) for r in its}
    first, final, n = {}, {}, Counter()
    for r in its:
        i = r["instance_id"]
        rec1 = latest_record(raw, job1(arm, key, r), key)
        d1, msg = read(rec1)
        first[i] = d1
        final[i] = d1
        n["first answer accepted by the function-call reading only"] += read(rec1, strict=True)[0] is not None
        if d1 is not None:
            n["first answer accepted"] += 1
            continue
        n[f"first answer rejected: {msg[:44]}"] += 1
        j2 = job2(arm, key, r, raw)
        if j2 is None:
            continue
        n["repair calls due"] += 1
        rec2 = latest_record(raw, j2, key)
        n["repair calls answered"] += rec2 is not None
        final[i] = read(rec2)[0]

    def exact(d, i) -> bool:
        if d is None:
            return False
        try:
            return compare(state_from_extraction(d), ref[i])["exact"]
        except Exception:
            return False

    def stage(ex: dict) -> dict:
        rows = [(by[i]["family_id"], d is not None, exact(d, i)) for i, d in ex.items()]
        res, stats = planned_results(its, {i: {"parsed": d, "status": "ok"} for i, d in ex.items()})
        return {"state_exact": cluster_mean_ci((f, float(e)) for f, _, e in rows),
                "accepted_but_wrong": cluster_mean_ci((f, float(a and not e)) for f, a, e in rows),
                "rejected": cluster_mean_ci((f, float(not a)) for f, a, _ in rows),
                "plan": summarize(score(by, res, list(by))), "pipeline": stats}

    out = {"items": len(its), "counts": dict(n), "first": stage(first), "with_repair": stage(final)}
    pairs = [(by[i]["family_id"], float(exact(final[i], i)), float(exact(first[i], i))) for i in by]
    out["gain_state_exact"] = paired_diff_ci(pairs)
    rej = [i for i in by if first[i] is None]
    out["of_rejected_first_answers"] = {"n": len(rej), "recovered_exact": sum(exact(final[i], i) for i in rej),
                                        "accepted_but_wrong_after_repair": sum(final[i] is not None and not exact(final[i], i) for i in rej),
                                        "still_rejected": sum(final[i] is None for i in rej)}
    out["calls_per_item_with_repair"] = round(1 + n["repair calls due"] / max(1, len(its)), 3)
    return out


def analyze(keys: list[str], raw: Path) -> dict:
    its = items()
    out = {"families": len({r["family_id"] for r in its}), "items": len(its), "models": {}}
    for k in keys:
        out["models"][k] = {arm: {"pooled": analyze_arm(its, arm, k, raw),
                                  **{kind: analyze_arm([r for r in its if r["robust"]["kind"] == kind], arm, k, raw)
                                     for kind in KINDS}} for arm in ARMS}
    return out


def fmt(d) -> str:
    return "n/a" if not isinstance(d, dict) or d.get("mean") is None else f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


def render(s: dict) -> str:
    L = ["# Study 3: one diagnostic repair call for rejected extractions", "",
         f"Generated by `experiments/run_repair.py --analyze-only`. Protocol: `PREREG_REPAIR.md`. {s['items']} reworded items "
         f"from {s['families']} train families. All attempted: a rejected or missing extraction counts as wrong. "
         "F: the model's frozen extraction prompt. N: the translating prompt.", ""]
    for k, m in s["models"].items():
        L += [f"## {k.replace('adaption-', '')}", "",
              "| Prompt | Wording | State exact, first answer | State exact, with repair | Gain | Accepted but wrong, first / with repair | "
              "Rejected, first / with repair | Plan optimal, first / with repair | Calls per item |", "|---|---|---|---|---|---|---|---|---|"]
        for arm in ARMS:
            for part in ("pooled",) + KINDS:
                x = m[arm][part]
                a, b = x["first"], x["with_repair"]
                L.append(f"| {arm} | {part} | {fmt(a['state_exact'])} | {fmt(b['state_exact'])} | {fmt(x['gain_state_exact'])} | "
                         f"{fmt(a['accepted_but_wrong'])} / {fmt(b['accepted_but_wrong'])} | {fmt(a['rejected'])} / {fmt(b['rejected'])} | "
                         f"{fmt(a['plan']['optimal_all'])} / {fmt(b['plan']['optimal_all'])} | {x['calls_per_item_with_repair']} |")
        L.append("")
        for arm in ARMS:
            x = m[arm]["pooled"]
            L += [f"Prompt {arm}, pooled: {x['of_rejected_first_answers']}. Counts: {x['counts']}.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--stage", type=int, choices=(1, 2))
    ap.add_argument("--models", default="")
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "pilot"))
    ap.add_argument("--out", default=str(ROOT / "results" / "aggregate" / "repair"))
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--budget", type=float, default=0.0, help="cap on the cumulative ledger total (credits)")
    ap.add_argument("--analyze-only", action="store_true")
    a = ap.parse_args(argv)
    if a.generate:
        return generate()
    keys = [k.strip() for k in a.models.split(",") if k.strip()]
    raw = Path(a.raw)
    if a.analyze_only:
        s = analyze(keys, raw)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "repair_summary.json").write_text(json.dumps(s, indent=1, default=str))
        (out / "repair_report.md").write_text(render(s))
        print(f"wrote {out / 'repair_summary.json'} and repair_report.md")
        return 0
    if not a.stage or not keys or a.budget <= 0 or a.max_calls <= 0:
        print("pass --stage, --models, --budget (cumulative ledger cap) and --max-calls; no calls made")
        return 2
    load_env(ROOT / ".env")
    models = load_models(Path(a.models_config))
    errs, _ = check_all(models, keys)
    for e in errs:
        print("ERROR", e)
    if errs:
        return 2
    its = items()
    cur = currency(models[keys[0]])
    ledger = Ledger(raw / ("spend_ledger.jsonl" if cur == "usd" else f"spend_ledger_{cur}.jsonl"), a.budget)
    for k in keys:
        for arm in ARMS:
            jobs = [job1(arm, k, r) for r in its] if a.stage == 1 else [j for r in its if (j := job2(arm, k, r, raw)) is not None]
            print(f"stage {a.stage} prompt {arm}: {len(jobs)} jobs; already spent {ledger.spent:.4f}")
            print(k, arm, run_jobs(jobs, k, models[k], raw, max_calls=a.max_calls, concurrency=a.concurrency, ledger=ledger))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
