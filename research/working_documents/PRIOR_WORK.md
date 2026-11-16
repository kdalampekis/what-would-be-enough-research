# PRIOR_WORK.md
# Prior Work, Reuse Boundaries, and Provenance

This project must clearly distinguish **existing user infrastructure** from new sprint work.

---

## 1. Existing repository: STML

STML contains useful formal-reasoning infrastructure and prior experiments.

Relevant reusable ideas / modules include:

- exact finite logical semantics;
- hidden-world generation;
- SAT-based independent referee;
- proof certificates / countermodels;
- proof depth and structural difficulty;
- selective prediction / abstention metrics;
- honesty / coverage / risk-style evaluation;
- threshold-shift experiments.

Prior STML findings include:
- deeper logical problems can reduce accuracy while confidence remains high;
- self-sufficiency / certificate-style checks can outperform raw confidence;
- thresholds may fail under structural distribution shift.

These findings are **background / prior work**, not results of the new project.

### Allowed reuse
- generic solver wrappers;
- world generators where compatible;
- exact logical semantics;
- countermodel generation;
- proof-depth controls;
- utility / abstention metric helpers.

### Not allowed
- presenting old STML experiments as new sprint results;
- silently copying prior result tables;
- using STML's old research question as the new project's novelty.

---

## 2. Existing repository: PathCompiler

PathCompiler contains generic verification / optimization components.

Potentially reusable:
- Z3 backends;
- hard/soft constraint abstractions;
- assumptions and unsat cores;
- satisfiable-model extraction;
- weighted soft constraints / optimization;
- counterexample infrastructure.

Potential relevance:
- exact plan feasibility;
- minimum-cost intervention sets;
- obligation checking.

The new project should not become a PathCompiler product fork.

---

## 3. Epistemic Search

Epistemic Search is explicitly out of scope for this project.

Do not use it as the conceptual basis.

If any small generic utility is reused, disclose it explicitly.

---

## 4. New work required for this project

The following should be considered new project work:

- heterogeneous information/computation action model;
- INFORMATION_ONLY / COMPUTATION_ONLY / BOTH / NEITHER taxonomy;
- Minimal Sufficient Epistemic Plan (MSEP) formalization;
- epistemic-obligation representation;
- exact sufficiency/minimality oracle for mixed plans;
- three-mode evaluation protocol;
- relevant-vs-sufficient matched families;
- BOTH and NEITHER benchmark families;
- plan minimality and stopping metrics;
- Epistemic Obligation Planner mitigation;
- new experiment results.

---

## 5. Reuse disclosure format

For every reused module, document:

- source repository;
- source file;
- what was reused;
- whether code was copied, adapted, or only conceptually reused;
- date / commit hash;
- what changed.

Recommended table:

| New module | Source | Reuse type | Changes |
|---|---|---|---|
| `oracle/logic.py` | STML `stml/logic.py` | adapted | new action-state interface |
| `oracle/solver.py` | PathCompiler solver wrapper | adapted | MSEP constraints |
| `benchmark/world.py` | STML world generator | conceptual/adapted | mixed epistemic actions |

---

## 6. Pre-sprint / sprint provenance

Before the sprint:
- tag the baseline repository state;
- record commit hashes of reused repositories;
- preserve `PRIOR_WORK.md`.

During the sprint:
- keep new benchmark code and experiments in the new repository;
- commit frequently;
- avoid rewriting history.

In the write-up:
- state clearly what existed before;
- state what was implemented during the sprint;
- state which experimental results were generated during the sprint.

---

## 7. Scientific provenance rule

Reused infrastructure is acceptable only if the **new research question, benchmark construction, experimental protocol, and reported results** are clearly attributable to the new project.

The benchmark should be auditable independently of prior repositories.

---

## 8. Reuse record for this repository (2026-11-03)

Prior repositories were cloned read-only and inspected. Code was reused only after it was checked against an independent computation.

| New module | Source | Reuse type | What changed / how it was checked |
|---|---|---|---|
| `src/msep/world/compute_tasks.py` (`SyllogismFollows`) | STML `stml/logic.py`, commit `15646ecab33603a060bd97d9e13561e36781e67e` | adapted (region semantics for the four categorical forms with existential import, about 30 lines) | Rewritten as plain functions over tuples. Used only as one simple computation-task kind in the random oracle-validation instances; since 2026-11-03, benchmark families use the certified tasks instead. Checked against independent brute-force model enumeration: 1,860 random consistent cases before reuse, and again in `tests/test_compute_tasks.py`. |
| `src/msep/oracle/logic.py` | STML `stml/referee.py`, same commit | conceptual only | Same style (pysat CaDiCaL, assumption literals on a persistent solver). No code copied. New two-copy distinguishing-pair encoding. |
| methodology | STML | conceptual | An independent SAT referee that shares no reasoning code with the enumerator, and 100% agreement required. |
| — | PathCompiler, commit `a7251b77bae01f9e0d560120246ffd73aaa547ad` | none | Inspected (TypeScript; solver-neutral term language, Z3 provider, assumptions/unsat cores). Not reused: the project is Python and pysat covers the needs. |
| — | epistemic-search, commit `3206cda687a738c181ea3508461c0975a7ad6fa4` | **none; will not be reused** | Out of scope (section 3). It was cloned and read once on 2026-11-03, before it was ruled out. Decided 2026-11-03: no code or design from it is used. Phase 2 statistics (`eval/bootstrap.py`) are written independently here, to avoid any provenance ambiguity. |

STML's own test suite passed at the inspected commit (`tests/test_core.py`, 24 tests). No STML or PathCompiler experiment results are used or reported here.

Everything else in `src/msep/` was written new for this project.
