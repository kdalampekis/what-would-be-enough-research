"""Benchmark audit: shortcuts, leakage, balance and label re-verification.

Everything here reads benchmark records only. The shortcut probe uses features
of the *prompt text* (what a model sees), never oracle fields.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from msep.models.prompts import Mode, build_prompt, eligible

CORE_CLASSES = ("ALREADY_SUFFICIENT", "INFORMATION_ONLY", "COMPUTATION_ONLY", "BOTH", "NEITHER")


# -- surface features of the rendered prompt ----------------------------------------

def surface_features(text: str) -> dict:
    actions = re.findall(r"^\s+([A-Z_]+_[FK][0-9_FK]*) \((information|computation), cost (\d+)\)", text, re.M)
    known_line = next((l for l in text.splitlines() if l.startswith("Known so far:")), "")
    known = re.findall(r"\b([FK]\d+) is (true|false)", known_line)
    facts = set(re.findall(r"^\s+(F\d+):", text, re.M))
    comps = set(re.findall(r"^\s+(K\d+):", text, re.M))
    known_f = {h for h, _ in known if h.startswith("F")}
    known_k = {h for h, _ in known if h.startswith("K")}
    rules = re.findall(r"^\s+\d+\. ", text, re.M)
    return {
        "n_ask": sum(1 for _, k, _ in actions if k == "information"),
        "n_compute": sum(1 for _, k, _ in actions if k == "computation"),
        "n_known_world": len(known_f),
        "n_known_computed": len(known_k),
        "n_unknown_world": len(facts - known_f),
        "n_unknown_computed": len(comps - known_k),
        "n_rules": len(rules),
        "total_cost": sum(int(c) for _, _, c in actions),
    }


FEATURE_SETS = {
    "action_counts": ("n_ask", "n_compute"),
    "knowledge_counts": ("n_known_world", "n_known_computed", "n_unknown_world", "n_unknown_computed"),
    "all_counts": ("n_ask", "n_compute", "n_known_world", "n_known_computed", "n_unknown_world",
                   "n_unknown_computed"),
}


def lookup_probe(train: list[dict], test: list[dict], features: tuple[str, ...], label: str = "resource_class") -> dict:
    """Memorise the majority label per feature tuple on train; predict on test.

    A deliberately strong probe for discrete surface features: if it beats the
    majority baseline by much, the class is predictable without reasoning."""
    table: dict = defaultdict(Counter)
    overall = Counter()
    for r in train:
        key = tuple(r["features"][f] for f in features)
        table[key][r[label]] += 1
        overall[r[label]] += 1
    majority = overall.most_common(1)[0][0]
    correct = 0
    for r in test:
        key = tuple(r["features"][f] for f in features)
        pred = table[key].most_common(1)[0][0] if key in table else majority
        correct += pred == r[label]
    base = sum(r[label] == majority for r in test)
    n = max(1, len(test))
    return {"features": list(features), "probe_accuracy": correct / n, "majority_baseline": base / n,
            "majority_class": majority, "n_test": len(test), "distinct_keys": len(table)}


def probe_rows(records: list[dict]) -> list[dict]:
    return [{"split": r["split"], "family_id": r["family_id"], "sibling_type": r["sibling_type"],
             "resource_class": r["oracle"]["resource_class"], "features": surface_features(r["prompt_text"])}
            for r in records]


def shortcut_report(records: list[dict]) -> dict:
    rows = probe_rows(records)
    train = [r for r in rows if r["split"] == "train"]
    dev = [r for r in rows if r["split"] == "dev"]
    insuff_train = [r for r in train if r["resource_class"] != "ALREADY_SUFFICIENT"]
    insuff_dev = [r for r in dev if r["resource_class"] != "ALREADY_SUFFICIENT"]
    out = {"all_classes": {}, "insufficient_only": {}}
    for name, feats in FEATURE_SETS.items():
        out["all_classes"][name] = lookup_probe(train, dev, feats)
        out["insufficient_only"][name] = lookup_probe(insuff_train, insuff_dev, feats)
    return out


# -- leakage, balance, structure -------------------------------------------------------

def split_leakage(records: list[dict]) -> dict:
    fam_splits = defaultdict(set)
    for r in records:
        fam_splits[r["family_id"]].add(r["split"])
    multi = [f for f, s in fam_splits.items() if len(s) > 1]
    text_split = defaultdict(set)
    for r in records:
        text_split[r["prompt_text"]].add(r["split"])
    dup_cross = sum(1 for s in text_split.values() if len(s) > 1)
    return {"families_in_more_than_one_split": len(multi), "identical_prompt_texts_across_splits": dup_cross,
            "families": len(fam_splits)}


def instruction_leakage(records: list[dict]) -> dict:
    """In End-to-End and Detection-Controlled modes, the text added around the state
    must be identical for every class (so it cannot carry the label)."""
    out = {}
    for mode in (Mode.END_TO_END, Mode.DETECTION_CONTROLLED):
        wrappers = set()
        for r in records:
            rc = r["oracle"]["resource_class"]
            if eligible(mode, rc):
                p = build_prompt(r["prompt_text"], mode, rc)
                wrappers.add(p.replace(r["prompt_text"], "<STATE>"))
        out[mode.value] = {"distinct_wrappers": len(wrappers)}
    forbidden = ("decoy", "alias", "distractor", "optimal", "INFORMATION_ONLY", "COMPUTATION_ONLY", "NEITHER",
                 "ALREADY_SUFFICIENT", "sufficient plan")
    hits = Counter()
    for r in records:
        for w in forbidden:
            if w in r["prompt_text"]:
                hits[w] += 1
    out["label_words_in_state_text"] = dict(hits)
    return out


def balance(records: list[dict]) -> dict:
    by_split = defaultdict(Counter)
    for r in records:
        by_split[r["split"]][r["oracle"]["resource_class"]] += 1
    return {s: dict(c) for s, c in by_split.items()}


def computed_value_balance(records: list[dict]) -> dict:
    """True-rate of computed variables per task kind and per role. A strongly skewed
    rate would let a model guess certified results instead of computing them."""
    seen = set()
    stats = defaultdict(Counter)
    for r in records:
        if r["family_id"] in seen:
            continue
        seen.add(r["family_id"])
        for name, task in r["state"]["compute_tasks"].items():
            val = r["true_computed_values"][name]
            stats[f"kind={task['kind']}"][val] += 1
            stats[f"role={name}"][val] += 1
    return {k: {"n": sum(c.values()), "true_rate": c[True] / max(1, sum(c.values()))} for k, c in sorted(stats.items())}


def target_value_balance(records: list[dict]) -> dict:
    by = defaultdict(Counter)
    for r in records:
        by[r["sibling_type"]][r["true_target_value"]] += 1
    return {t: c[True] / max(1, sum(c.values())) for t, c in sorted(by.items())}


def optimal_plan_multiplicity(records: list[dict]) -> dict:
    c = Counter(len(r["oracle"]["optimal_plans"]) for r in records if r["oracle"]["optimal_plans"])
    return {str(k): v for k, v in sorted(c.items())}


# -- checks added after the independent adversarial audit (2026-11-04) -------------------------

def consequent_value_leak(records: list[dict]) -> dict:
    """For implication rules 'if A then B' with B a literal: how often is B true in the
    latent world? 1.0 means the rule text copies the hidden value (a leak)."""
    from msep.benchmark.schemas import instance_from_record
    from msep.world.constraints import Implies, Not, Var
    hits = n = 0
    seen = set()
    for r in records:
        if r["family_id"] in seen:
            continue
        seen.add(r["family_id"])
        inst = instance_from_record(r)
        full = inst.full_assignment()
        for rule in inst.state.rules:
            f = rule.formula
            if isinstance(f, Implies) and isinstance(f.right, (Var, Not)):
                lit_ = f.right
                v = lit_.index if isinstance(lit_, Var) else lit_.arg.index
                val = full[v] if isinstance(lit_, Var) else not full[v]
                hits += val
                n += 1
    return {"implication_rules": n, "consequent_true_in_latent_rate": hits / n if n else None}


def q_rule_position(records: list[dict]) -> dict:
    """Position of the rule defining Q in the rendered list."""
    pos = Counter()
    for r in records:
        for line in r["prompt_text"].splitlines():
            m = re.match(r"\s+(\d+)\. Q if and only if", line)
            if m:
                pos[int(m.group(1))] += 1
    total = sum(pos.values())
    return {"most_common_position_share": (pos.most_common(1)[0][1] / total) if total else None,
            "distinct_positions": len(pos)}


def cost_vs_optimality(records: list[dict]) -> dict:
    """Share of offered actions at each cost that belong to some optimal plan."""
    by = defaultdict(lambda: [0, 0])
    for r in records:
        opt = {a for p in r["oracle"]["optimal_plans"] for a in p}
        for a in r["state"]["info_actions"] + r["state"]["comp_actions"]:
            by[a["cost"]][0] += a["name"] in opt
            by[a["cost"]][1] += 1
    return {str(c): {"offered": t, "optimal_share": k / t} for c, (k, t) in sorted(by.items())}


def heuristic_baselines(records: list[dict]) -> dict:
    """Deterministic shallow heuristics (agents/heuristics.py) scored by the oracle, per sibling type."""
    from msep.agents.heuristics import HEURISTICS, plan_for
    from msep.eval.plan_metrics import score
    from msep.models.schemas import ModelResponse
    out = {}
    for h in HEURISTICS:
        rows = []
        for r in records:
            p = plan_for(h, r["prompt_text"])
            resp = ModelResponse(p["state_sufficient"], p["resource_class"], p["plan"], [], True, p["decision"], None, "")
            s = score(r, resp)
            rows.append((r["sibling_type"], s["class_correct"], s["plan_sufficient"], s["plan_optimal"]))
        n = len(rows)
        by_t = defaultdict(list)
        for t, c, su, o in rows:
            by_t[t].append(o)
        out[h] = {"n": n, "class_accuracy": sum(c for _, c, _, _ in rows) / n,
                  "plan_sufficient": sum(su for _, _, su, _ in rows) / n,
                  "plan_optimal": sum(o for _, _, _, o in rows) / n,
                  "plan_optimal_by_sibling": {t: sum(v) / len(v) for t, v in sorted(by_t.items())}}
    return out


def heuristic_stratum(record: dict, heuristic: str = "h1pp") -> str:
    """'heuristic_easy' if the shallow heuristic gets the class and an optimal plan, else 'heuristic_hard'.
    Deterministic from the prompt text; used to stratify every model result."""
    from msep.agents.heuristics import plan_for
    from msep.eval.plan_metrics import score
    from msep.models.schemas import ModelResponse
    p = plan_for(heuristic, record["prompt_text"])
    s = score(record, ModelResponse(p["state_sufficient"], p["resource_class"], p["plan"], [], True, p["decision"], None, ""))
    return "heuristic_easy" if (s["class_correct"] and (s["plan_optimal"] or record["oracle"]["resource_class"] == "NEITHER"
                                                        and not p["plan"])) else "heuristic_hard"


def mental_shortcuts(records: list[dict]) -> dict:
    """Re-run the adversarial audit's 'compute it in your head' attacks on the certified tasks.

    posterior   sum of log-likelihood ratios rounded to 2 significant digits, compared to the threshold
    modpow      'true unless refuted mod a small prime factor of m'
    primality   best single size threshold on log10(n), fitted on train, scored on dev
    """
    import math
    from msep.world.compute_tasks import task_from_json
    tasks = {}
    for r in records:
        for name, t in r["state"]["compute_tasks"].items():
            key = (r["family_id"], name)
            if key not in tasks:
                tasks[key] = (r["split"], task_from_json(t), r["true_computed_values"][name])

    def sig2(x):
        return 0.0 if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + 1)

    post = [(t, v) for s, t, v in tasks.values() if t.kind == "posterior_above"]
    post_ok = 0
    for t, v in post:
        llr = sig2(math.log10(t.prior / (1 - t.prior))) + sum(sig2(math.log10(a / b)) for a, b in t.likelihoods)
        p = 1 / (1 + 10 ** (-llr))
        post_ok += (p > float(t.threshold)) == v
    mp = [(t, v) for s, t, v in tasks.values() if t.kind == "modpow"]
    small = [p for p in range(2, 200) if all(p % d for d in range(2, int(p ** 0.5) + 1))]
    mp_ok = 0
    for t, v in mp:
        refuted = any(t.m % p == 0 and pow(t.a, t.b, p) != t.r % p for p in small)
        mp_ok += (not refuted) == v
    pr_train = [(math.log10(t.n), v) for s, t, v in tasks.values() if t.kind == "primality" and s == "train"]
    pr_dev = [(math.log10(t.n), v) for s, t, v in tasks.values() if t.kind == "primality" and s == "dev"]
    best = (0.0, None, None)
    for thr, _ in pr_train:
        for direction in (True, False):
            acc = sum(((x >= thr) == direction) == v for x, v in pr_train) / max(1, len(pr_train))
            if acc > best[0]:
                best = (acc, thr, direction)
    dev_acc = (sum(((x >= best[1]) == best[2]) == v for x, v in pr_dev) / len(pr_dev)) if pr_dev and best[1] else None
    base = lambda xs: max(sum(v for _, v in xs), len(xs) - sum(v for _, v in xs)) / max(1, len(xs))  # noqa: E731
    return {
        "posterior_llr2sig_accuracy": post_ok / max(1, len(post)), "posterior_n": len(post),
        "modpow_true_unless_refuted_accuracy": mp_ok / max(1, len(mp)), "modpow_n": len(mp),
        "modpow_majority_baseline": base(mp),
        "primality_size_threshold_dev_accuracy": dev_acc, "primality_dev_n": len(pr_dev),
        "primality_majority_baseline_dev": base(pr_dev),
    }


def hard_subset_composition(records: list[dict]) -> dict:
    """How the pre-registered heuristic_hard subset differs from the full distribution.
    Selection on a baseline's failure is selection on a correlate of difficulty: report
    its composition so differences can be read within class, not only pooled."""
    rows = []
    for r in records:
        st = heuristic_stratum(r)
        o = r["oracle"]
        rows.append({"stratum": st, "class": o["resource_class"], "sibling": r["sibling_type"],
                     "motif": (r.get("notes") or {}).get("motif", "v2"),
                     "plan_size": len(o["optimal_plans"][0]) if o["optimal_plans"] else 0,
                     "n_actions": len(o["actions"]), "prompt_chars": len(r["prompt_text"]),
                     "n_minimal_plans": len(o["minimal_sufficient_plans"])})

    def dist(sel, key):
        c = Counter(x[key] for x in sel)
        n = sum(c.values())
        return {k: round(v / n, 3) for k, v in sorted(c.items())}

    def mean(sel, key):
        return round(sum(x[key] for x in sel) / max(1, len(sel)), 2)
    out = {}
    for name, sel in (("all", rows), ("heuristic_hard", [x for x in rows if x["stratum"] == "heuristic_hard"]),
                      ("heuristic_easy", [x for x in rows if x["stratum"] == "heuristic_easy"])):
        out[name] = {"n": len(sel), "class": dist(sel, "class"), "motif": dist(sel, "motif"),
                     "sibling": dist(sel, "sibling"), "mean_plan_size": mean(sel, "plan_size"),
                     "mean_actions": mean(sel, "n_actions"), "mean_prompt_chars": mean(sel, "prompt_chars"),
                     "mean_minimal_plans": mean(sel, "n_minimal_plans")}
    out["hard_share_by_class"] = {c: round(sum(1 for x in rows if x["class"] == c and x["stratum"] == "heuristic_hard")
                                           / max(1, sum(1 for x in rows if x["class"] == c)), 3)
                                  for c in sorted({x["class"] for x in rows})}
    return out
