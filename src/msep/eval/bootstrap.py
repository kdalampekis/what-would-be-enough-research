"""Statistics for the pilot: family-clustered bootstrap, exact McNemar, classification metrics.

Written for this project (no code reused from other repositories).
Clusters are benchmark families: siblings are not independent, so resampling
is over families, never over rows.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Hashable, Iterable


def _quantile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (pos - lo) * (xs[hi] - xs[lo])


def cluster_mean_ci(items: Iterable[tuple[Hashable, float]], reps: int = 2000, seed: int = 0,
                    level: float = 0.95) -> dict:
    """Mean of item values with a percentile CI from resampling clusters (ratio of sums)."""
    by: dict = defaultdict(list)
    for c, v in items:
        by[c].append(float(v))
    clusters = [(sum(v), len(v)) for v in by.values()]
    n = sum(k for _, k in clusters)
    if n == 0:
        return {"mean": None, "lo": None, "hi": None, "n": 0, "clusters": 0}
    mean = sum(s for s, _ in clusters) / n
    if len(clusters) < 2:
        return {"mean": mean, "lo": None, "hi": None, "n": n, "clusters": len(clusters)}
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        sample = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        draws.append(sum(s for s, _ in sample) / sum(k for _, k in sample))
    a = (1 - level) / 2
    return {"mean": mean, "lo": _quantile(draws, a), "hi": _quantile(draws, 1 - a), "n": n, "clusters": len(clusters)}


def paired_diff_ci(pairs: Iterable[tuple[Hashable, float, float]], reps: int = 2000, seed: int = 0,
                   level: float = 0.95) -> dict:
    """Mean of (a - b) over matched pairs, CI by resampling clusters."""
    return cluster_mean_ci(((c, a - b) for c, a, b in pairs), reps, seed, level)


def mcnemar_exact(pairs: Iterable[tuple[bool, bool]]) -> dict:
    """Exact two-sided McNemar test on paired binary outcomes (a, b)."""
    b = c = 0
    for x, y in pairs:
        if x and not y:
            b += 1
        elif y and not x:
            c += 1
    n = b + c
    if n == 0:
        return {"a_only": b, "b_only": c, "p_value": 1.0}
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return {"a_only": b, "b_only": c, "p_value": min(1.0, 2 * tail)}


def confusion(gold: list[str], pred: list[str], labels: list[str]) -> dict:
    m = {g: {p: 0 for p in labels + ["INVALID"]} for g in labels}
    for g, p in zip(gold, pred):
        m[g][p if p in labels else "INVALID"] += 1
    return m


def macro_f1(gold: list[str], pred: list[str], labels: list[str]) -> float:
    f1s = []
    for lab in labels:
        tp = sum(g == lab and p == lab for g, p in zip(gold, pred))
        fp = sum(g != lab and p == lab for g, p in zip(gold, pred))
        fn = sum(g == lab and p != lab for g, p in zip(gold, pred))
        if tp + fp + fn == 0:
            continue
        f1s.append(2 * tp / (2 * tp + fp + fn))
    return sum(f1s) / len(f1s) if f1s else 0.0


def balanced_accuracy(gold: list[str], pred: list[str], labels: list[str]) -> float:
    recalls = []
    for lab in labels:
        idx = [i for i, g in enumerate(gold) if g == lab]
        if idx:
            recalls.append(sum(pred[i] == lab for i in idx) / len(idx))
    return sum(recalls) / len(recalls) if recalls else 0.0


def cluster_stat_ci(rows: list[tuple[Hashable, str, str]], stat, labels: list[str], reps: int = 1000,
                    seed: int = 0, level: float = 0.95) -> dict:
    """CI for a classification statistic (macro-F1, balanced accuracy) by family resampling."""
    by: dict = defaultdict(list)
    for c, g, p in rows:
        by[c].append((g, p))
    keys = list(by)
    gold = [g for _, g, _ in rows]
    pred = [p for _, _, p in rows]
    point = stat(gold, pred, labels) if rows else None
    if len(keys) < 2:
        return {"value": point, "lo": None, "hi": None}
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        sample = [x for _ in keys for x in by[keys[rng.randrange(len(keys))]]]
        draws.append(stat([g for g, _ in sample], [p for _, p in sample], labels))
    a = (1 - level) / 2
    return {"value": point, "lo": _quantile(draws, a), "hi": _quantile(draws, 1 - a)}


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values (family-wise error control)."""
    items = sorted(pvalues.items(), key=lambda kv: (kv[1], kv[0]))
    m = len(items)
    out, running = {}, 0.0
    for rank, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        out[k] = running
    return out


def paired_cluster_permutation(pairs, reps: int = 5000, seed: int = 0) -> dict:
    """Paired sign-flip permutation test on cluster sums of (a - b). Two-sided.
    For continuous paired outcomes (e.g. regret under two modes) where McNemar does not apply."""
    by: dict = defaultdict(float)
    n = 0
    for c, a, b in pairs:
        by[c] += float(a) - float(b)
        n += 1
    sums = list(by.values())
    if not sums:
        return {"mean_difference": None, "p_value": None, "clusters": 0}
    obs = abs(sum(sums))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(reps):
        stat = abs(sum(s if rng.random() < 0.5 else -s for s in sums))
        extreme += stat >= obs - 1e-12
    return {"mean_difference": sum(sums) / n, "p_value": (extreme + 1) / (reps + 1), "clusters": len(sums)}


def cohens_h(p1: float, p2: float) -> float:
    """Effect size for a difference between two proportions."""
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


def calibration(items) -> dict:
    """Brier score and 10-bin expected calibration error for (confidence, correct) pairs."""
    items = [(float(c), bool(y)) for c, y in items if c is not None]
    if not items:
        return {"n": 0, "brier": None, "ece": None}
    brier = sum((c - y) ** 2 for c, y in items) / len(items)
    bins = defaultdict(list)
    for c, y in items:
        bins[min(9, int(c * 10))].append((c, y))
    ece = sum(len(b) / len(items) * abs(sum(c for c, _ in b) / len(b) - sum(y for _, y in b) / len(b))
              for b in bins.values())
    return {"n": len(items), "brier": brier, "ece": ece}
