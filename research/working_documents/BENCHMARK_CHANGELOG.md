# Benchmark changelog

Every change to benchmark content (generator, rendering, tasks, oracle) is listed here, with the reason. After the v3 freeze, only objective bug fixes are allowed; each needs a new freeze record (`experiments/freeze_benchmark.py --write`) and an entry here. **No change may be made to raise or lower model scores.** No model had been run when any of these changes was made.

| Date | Version | Change | Reason (how found) |
|---|---|---|---|
| 2026-11-03 | v1 | First families; certified computation tasks replace trivial ones | Review: trivial tasks could be done in the head |
| 2026-11-04 | v2 | Randomised redundant actions, distractors, decoy noise | Own audit: count probe 86–90% |
| 2026-11-04 | v3 | New template: random motifs, class-independent sibling sampling, random implication signs, seeded rule order, version-2 certified tasks | Independent adversarial audit: v2 solved 100% by reading Q's rule; value, position and cost leaks; mental shortcuts |
| 2026-11-04 | v3 | Parenthesise complex left sides of biconditionals in rendering | Rendering round-trip check: ambiguous nested parity (no effect on v2 bytes) |
| 2026-11-04 | **v3.0 FROZEN** | Freeze record `data/FREEZE_v3.json` (code commit 2b496e7) | Readiness review |
