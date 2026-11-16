"""E0: oracle validation. No LLM calls.

Compares the independent exact paths on random instances and on generated
benchmark families, and writes results/oracle_validation.{json,md}.
Any disagreement is a blocker: the script exits non-zero.

    python experiments/e0_oracle_validation.py --small 10000 --medium 2000 --families 200
"""

from __future__ import annotations

import argparse
import itertools
import json
import platform
import random
import subprocess
import sys
import time
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pysat

from msep.actions.computation import ComputationAction
from msep.benchmark.families import generate_family
from msep.benchmark.template_v3 import generate_family_v3
from msep.controllers import obligation_planner
from msep.obligations.extraction import extract
from msep.oracle import probability, solver
from msep.oracle.brute_force import BruteForce
from msep.oracle.sufficiency import Composition, ResourceClass, canonical, composition, plan_cost
from msep.world.constraints import evaluate
from msep.world.generator import RandomConfig, random_instance
from msep.world.state import Instance, LatentWorld, LogicalEntailment, PosteriorThreshold

ROOT = Path(__file__).resolve().parents[1]
MEDIUM = RandomConfig(min_world=3, max_world=6, max_computed=4, max_rules=7, max_actions=9, p_posterior=0.2)


class Checks:
    def __init__(self):
        self.passed = Counter()
        self.failed = Counter()
        self.skipped = Counter()
        self.failures: list[dict] = []

    def check(self, name: str, ok: bool, ctx: dict) -> None:
        if ok:
            self.passed[name] += 1
        else:
            self.failed[name] += 1
            if len(self.failures) < 50:
                self.failures.append({"check": name, **ctx})

    def skip(self, name: str) -> None:
        self.skipped[name] += 1


def consistent_worlds(state):
    true_c = state.true_computed_values()
    wv = state.world_vars()
    for bits in itertools.product((False, True), repeat=len(wv)):
        w = dict(zip(wv, bits))
        if any(w[i] != v for i, v in state.evidence):
            continue
        if all(evaluate(r.formula, {**w, **true_c}) for r in state.rules):
            yield LatentWorld(tuple(sorted(w.items())))


def validate_state(state, checks: Checks, ctx: dict, rng: random.Random) -> dict:
    bf = BruteForce(state)
    b = bf.analyze()
    logical = isinstance(state.decision_rule, LogicalEntailment)
    rclass = b.resource_class(state)

    # 1. plan oracle agreement
    if logical:
        s = solver.analyze(state)
        if s.minimal_truncated:
            checks.skip("minimal_plans_solver_vs_brute")
            checks.check("optimal_plans_solver_vs_brute",
                         s.optimal_cost == b.optimal_cost and (s.extras.get("optimal_truncated") or
                                                                s.optimal_plans == b.optimal_plans), ctx)
        else:
            checks.check("plan_analysis_solver_vs_brute", s.key() == b.key(), ctx)
        checks.check("resource_class_solver_vs_brute", s.resource_class(state) == rclass, ctx)
        # 2. obligations
        obs, trunc = extract(state)
        if trunc:
            checks.skip("obligations_sat_vs_brute")
        else:
            checks.check("obligations_sat_vs_brute",
                         sorted(sorted(o.variables) for o in obs) == sorted(sorted(x) for x in bf.obligation_sets()), ctx)
            checks.check("no_obligations_iff_sufficient", (len(obs) == 0) == b.already_sufficient, ctx)
            # 3. obligation planner
            out = obligation_planner.plan(state)
            if b.optimal_cost is None:
                checks.check("planner_neither", out.plan is None, ctx)
            else:
                checks.check("planner_optimal_cost", (out.cost or 0) == b.optimal_cost
                             and canonical(out.plan) in b.optimal_plans, ctx)
        # 4. random plans
        names = [a.name for a in state.actions]
        for _ in range(5):
            plan = canonical(n for n in names if rng.random() < 0.5)
            checks.check("random_plan_sufficiency_sat_vs_brute",
                         solver.plan_sufficient(state, plan) == bf.plan_sufficient(plan), ctx)
        # 7. tau = 1 posterior reproduces the logical rule
        wv = state.world_vars()
        post_state = replace(state, decision_rule=PosteriorThreshold(Fraction(1)),
                             prior=tuple((i, Fraction(1, 2)) for i in wv))
        checks.check("posterior_tau1_equals_logical", BruteForce(post_state).analyze().key() == b.key(), ctx)
        # 11. NEITHER: full plan insufficient
        if rclass is ResourceClass.NEITHER:
            checks.check("neither_full_plan_insufficient", not bf.plan_sufficient(names), ctx)
    else:
        p = probability.analyze(state)
        checks.check("plan_analysis_wmc_vs_brute", p.key() == b.key(), ctx)
        checks.check("resource_class_wmc_vs_brute", p.resource_class(state) == rclass, ctx)
        # 8. posterior values
        bp = bf.posteriors()
        conv = {tuple(sorted((i, bool((g >> i) & 1)) for i in state.computed_vars() if i not in state.known)): v
                for g, v in bp.items()}
        checks.check("posteriors_wmc_vs_brute", probability.posteriors(state) == conv, ctx)
        if rclass is ResourceClass.NEITHER:
            checks.check("neither_no_sufficient_plan", not b.extras["sufficient_plans"], ctx)

    # 6. minimality and cost (brute)
    suff = b.extras["sufficient_plans"]
    for plan in b.optimal_plans:
        checks.check("optimal_plan_sufficient", bf.plan_sufficient(plan), ctx)
        checks.check("optimal_plan_inclusion_minimal",
                     all(not bf.plan_sufficient(tuple(y for y in plan if y != x)) for x in plan), ctx)
        checks.check("optimal_plan_cheapest", all(plan_cost(state, q) >= plan_cost(state, plan) for q in suff), ctx)
    # 10. BOTH
    if rclass is ResourceClass.BOTH:
        checks.check("both_every_optimal_plan_mixed",
                     all(composition(state, p) is Composition.BOTH for p in b.optimal_plans), ctx)
        info_only = [a.name for a in state.info_actions]
        comp_only = [a.name for a in state.comp_actions]
        nec = b.necessity(state)
        if nec["information_necessary"] and nec["computation_necessary"]:
            checks.check("both_single_resource_insufficient",
                         not bf.plan_sufficient(info_only) and not bf.plan_sufficient(comp_only), ctx)
    # 9. leakage
    worlds = list(consistent_worlds(state))
    checks.check("latent_world_exists", bool(worlds), ctx)
    for a in state.comp_actions:
        outs = {tuple(sorted(Instance(state, w).execute(a.name).items())) for w in worlds}
        checks.check("computation_outcome_world_invariant", len(outs) == 1, ctx)
    return {"class": rclass.value, "n_vars": state.n, "n_actions": len(state.actions),
            "rule": state.decision_rule.kind}


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--small", type=int, default=10000)
    ap.add_argument("--medium", type=int, default=2000)
    ap.add_argument("--families", type=int, default=200)
    ap.add_argument("--families-v3", type=int, default=100)
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    checks = Checks()
    t0 = time.time()
    suites = {}
    for suite, n, cfg, base_seed in (("random_small", args.small, RandomConfig(), 0),
                                     ("random_medium", args.medium, MEDIUM, 1_000_000)):
        classes, sizes, rules = Counter(), Counter(), Counter()
        for k in range(n):
            seed = base_seed + k
            inst = random_instance(random.Random(seed), cfg)
            info = validate_state(inst.state, checks, {"suite": suite, "seed": seed}, random.Random(seed))
            classes[info["class"]] += 1
            sizes[(info["n_vars"], info["n_actions"])] += 1
            rules[info["rule"]] += 1
        suites[suite] = {"instances": n, "classes": dict(classes), "decision_rules": dict(rules),
                         "max_vars": max(v for v, _ in sizes), "max_actions": max(a for _, a in sizes),
                         "mean_vars": sum(v * c for (v, _), c in sizes.items()) / n,
                         "mean_actions": sum(a * c for (_, a), c in sizes.items()) / n}
    # families
    fam_classes, fam_types, attempts = Counter(), Counter(), []
    for seed in range(args.families):
        fam = generate_family(seed)
        attempts.append(fam.attempts)
        for sib in fam.siblings:
            ctx = {"suite": "families", "family_seed": seed, "sibling": sib.sibling_type}
            info = validate_state(sib.instance.state, checks, ctx, random.Random(seed))
            checks.check("family_label_oracle_vs_brute",
                         info["class"] == sib.oracle.resource_class.value, ctx)
            checks.check("family_plans_oracle_vs_brute",
                         BruteForce(sib.instance.state).analyze().key() == sib.oracle.analysis.key(), ctx)
            fam_classes[info["class"]] += 1
            fam_types[sib.sibling_type] += 1
    v3_types = Counter()
    for seed in range(args.families_v3):
        fam = generate_family_v3(seed)
        for sib in fam.siblings:
            ctx = {"suite": "families_v3", "family_seed": seed, "sibling": sib.sibling_type}
            info = validate_state(sib.instance.state, checks, ctx, random.Random(seed))
            checks.check("family_v3_label_oracle_vs_brute", info["class"] == sib.oracle.resource_class.value, ctx)
            checks.check("family_v3_plans_oracle_vs_brute",
                         BruteForce(sib.instance.state).analyze().key() == sib.oracle.analysis.key(), ctx)
            v3_types[sib.sibling_type] += 1
    suites["families_v3"] = {"families": args.families_v3, "instances": sum(v3_types.values()),
                             "sibling_types": dict(v3_types)}
    suites["families"] = {"families": args.families, "instances": sum(fam_types.values()),
                          "classes": dict(fam_classes), "sibling_types": dict(fam_types),
                          "mean_attempts_per_family": sum(attempts) / max(1, len(attempts))}
    elapsed = time.time() - t0
    total_fail = sum(checks.failed.values())
    report = {
        "experiment": "E0 oracle validation",
        "status": "PASS" if total_fail == 0 else "FAIL",
        "git_commit": git_commit(),
        "python": platform.python_version(),
        "pysat": pysat.__version__,
        "seconds": round(elapsed, 1),
        "suites": suites,
        "checks": {name: {"passed": checks.passed[name], "failed": checks.failed[name],
                          "skipped": checks.skipped[name]}
                   for name in sorted(set(checks.passed) | set(checks.failed) | set(checks.skipped))},
        "total_checks": sum(checks.passed.values()) + total_fail,
        "total_failed": total_fail,
        "failures": checks.failures,
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "oracle_validation.json").write_text(json.dumps(report, indent=2))
    (out / "oracle_validation.md").write_text(markdown(report))
    print(f"{report['status']}: {report['total_checks']} checks, {total_fail} failed, {elapsed:.0f}s")
    return 0 if total_fail == 0 else 1


DESCRIPTIONS = {
    "plan_analysis_solver_vs_brute": "SAT/MaxSAT refinement vs enumeration: empty-plan sufficiency, optimal cost, all optimal plans, all inclusion-minimal plans",
    "optimal_plans_solver_vs_brute": "As above, for instances where minimal-plan enumeration hit its cap (optimal plans only)",
    "resource_class_solver_vs_brute": "Resource class, SAT/MaxSAT vs enumeration",
    "obligations_sat_vs_brute": "Obligation sets (minimal distinguishing variable sets), SAT vs enumeration",
    "no_obligations_iff_sufficient": "No obligations exactly when the current state is sufficient",
    "planner_optimal_cost": "Obligation planner returns an optimal plan",
    "planner_neither": "Obligation planner defers exactly on NEITHER",
    "random_plan_sufficiency_sat_vs_brute": "Sufficiency of random plans, SAT vs enumeration",
    "posterior_tau1_equals_logical": "Posterior rule with tau = 1 reproduces the logical rule (enumeration)",
    "plan_analysis_wmc_vs_brute": "Posterior rule: weighted model counting vs enumeration, full plan analysis",
    "resource_class_wmc_vs_brute": "Posterior rule: resource class, WMC vs enumeration",
    "posteriors_wmc_vs_brute": "Posterior rule: exact posteriors per uncomputed completion, WMC vs enumeration",
    "optimal_plan_sufficient": "Every optimal plan is sufficient",
    "optimal_plan_inclusion_minimal": "Removing any action from an optimal plan makes it insufficient",
    "optimal_plan_cheapest": "No sufficient plan is cheaper than an optimal plan",
    "both_every_optimal_plan_mixed": "BOTH: every optimal plan has an information and a computation action",
    "both_single_resource_insufficient": "BOTH (both necessary): all information actions alone and all computation actions alone are insufficient",
    "neither_full_plan_insufficient": "NEITHER (logical): even the full action set is insufficient",
    "neither_no_sufficient_plan": "NEITHER (posterior): no action set is sufficient",
    "latent_world_exists": "Some latent world is consistent with the instance",
    "computation_outcome_world_invariant": "Computation outcomes are identical in every consistent world (no leakage)",
    "family_label_oracle_vs_brute": "Family instances: stored class equals enumeration",
    "family_plans_oracle_vs_brute": "Family instances: stored plan labels equal enumeration",
    "family_v3_label_oracle_vs_brute": "Template v3 instances: stored class equals enumeration",
    "family_v3_plans_oracle_vs_brute": "Template v3 instances: stored plan labels equal enumeration",
}


def markdown(r: dict) -> str:
    lines = [f"# Oracle validation (E0)", "",
             f"**Status: {r['status']}** — {r['total_checks']} checks, {r['total_failed']} failed.", "",
             f"Commit `{r['git_commit']}` · Python {r['python']} · pysat {r['pysat']} · {r['seconds']} s", "",
             "No language model was called. Paths compared: brute-force enumeration (formula evaluation, no SAT), "
             "SAT/MaxSAT refinement (CNF, CaDiCaL + RC2), SAT obligation extraction + MaxSAT hitting set "
             "(obligation planner), and weighted model counting (posterior rule).", "",
             "## Instances", "", "| Suite | Instances | Classes | Decision rules | Mean vars / actions | Max vars / actions |",
             "|---|---|---|---|---|---|"]
    for name, s in r["suites"].items():
        if name in ("families", "families_v3"):
            continue
        cls = ", ".join(f"{k} {v}" for k, v in sorted(s["classes"].items()))
        rules = ", ".join(f"{k} {v}" for k, v in sorted(s["decision_rules"].items()))
        lines.append(f"| {name} | {s['instances']} | {cls} | {rules} | {s['mean_vars']:.1f} / {s['mean_actions']:.1f} "
                     f"| {s['max_vars']} / {s['max_actions']} |")
    f = r["suites"]["families"]
    lines += ["", f"Families: {f['families']} families, {f['instances']} instances "
              f"(mean {f['mean_attempts_per_family']:.2f} base samples per accepted family).", "",
              "| Sibling type | Instances |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in f["sibling_types"].items()]
    f3 = r["suites"].get("families_v3")
    if f3:
        lines += ["", f"Template v3: {f3['families']} families, {f3['instances']} instances.", "",
                  "| Sibling type (v3) | Instances |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in f3["sibling_types"].items()]
    lines += ["", "## Checks", "", "| Check | Passed | Failed | Skipped | What it compares |", "|---|---|---|---|---|"]
    for name, c in r["checks"].items():
        lines.append(f"| `{name}` | {c['passed']} | {c['failed']} | {c['skipped']} | {DESCRIPTIONS.get(name, '')} |")
    lines += ["", "Skipped = the SAT enumeration of minimal plans or obligations hit its cap (512); "
              "those instances are compared on optimal plans only.", ""]
    if r["failures"]:
        lines += ["## Failures (first 50)", "", "```json", json.dumps(r["failures"], indent=2), "```"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
