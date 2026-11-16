# Protocol amendments and deviations

This document lists every recorded change to a registered protocol and every deviation from one, in time order. For each it gives the date and time, what changed, why, and which results it affects. Times are UTC and come from git commit timestamps (`git log --date=iso`) and from the marker lines of the run logs in `results/raw/`. The commits of the sprint carry the author's local offset (UTC−8, Los Angeles); this document converts them to UTC. Registrations and freeze records are described in [evaluation_protocol.md](evaluation_protocol.md) §8. The repository's own summary of this material is [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §5 and §6, and [paper/report.md](../paper/report.md) Appendix B. No change listed here altered a prompt, an item, a planner, a scoring rule or a model setting after the first response of the data it covers, except where stated.

## 1. Registry

| # | When (UTC) | Commit | Change | Kind |
|---|---|---|---|---|
| 1 | 2026-11-14 00:08 | `1c0883e` | PROTOCOL.md amended to name the models actually used | amendment |
| 2 | 2026-11-14 11:36 | `e1fb301`, `4947810`; re-freeze `9714740`, `6ff8d16` (11:37) | PREREG_EOP Amendment 1: extraction prompt v2, conditions C′ and D′ | amendment, development-informed |
| 3 | 2026-11-14 13:32 | `cbe64c0`, `58315e7` | PREREG_EOP Amendment 2: analysis-only conditions Bt and Dt | amendment, analysis only |
| 4 | 2026-11-14 20:04 | `a13f9b7`, `d00ada4` | PREREG_FINAL §8: changes to frozen files before any test response | registered change |
| 5 | 2026-11-14 20:20 | `ba04b37`, `35b983b` | PREREG_ROBUST: one wording fix before the freeze | before freeze |
| 6 | 2026-11-14 20:05–20:41 | logs | Held-out and rewording chains restarted with other concurrency | scheduling |
| 7 | 2026-11-14 23:28 | `acd2207` | Network guard pauses and resumes runs while the provider is unreachable | operational |
| 8 | 2026-11-15 19:57–22:26 | `c3aed44`, `98e045d`, `2863f90` | Provider outage; manual pause and resume; held-out results first viewed with one run incomplete | deviation |
| 9 | 2026-11-15 | report | Seven gemma calls failed all three attempts | deviation, small |
| 10 | 2026-11-15 21:03 | `fd8145c` | Studies 1 and 2 registered after the held-out results were viewed | standing of new studies |
| 11 | 2026-11-15 22:27 – 2026-11-16 00:56 | logs | Follow-up and repair chains restarted with more workers; fill passes | scheduling |
| 12 | 2026-11-16 00:13 | `2935522` | Study 3 registered; message-text reading rule; third arm not run | standing, reading rule |
| 13 | 2026-11-16 01:12 | `1b6af3b` | Supplement script for one registered interval of Study 3 | analysis addition |
| 14 | various | – | Known defects in analysis outputs | defects |
| 15 | various | – | Dating discrepancies | records |

## 2. Before the held-out run

**1. PROTOCOL.md, models amendment.** The amendment names the four provider-hosted models and their settings ([PROTOCOL.md](../experiments/preregistrations/PROTOCOL.md), header). Why: the proprietary models listed in PROTOCOL.md §3 were not run ([docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §1). The header still reads "Not frozen", and the §12 steps (status line, recorded commit, tag) were not done; "the repository has no git tag". The file is pinned unchanged in `data/FREEZE_FINAL.json` (EXPERIMENT_INDEX §5). Affects: form only.

**2. PREREG_EOP Amendment 1.** What: new conditions C′ and D′ with extraction prompt v2, which is the v1 text plus the exact JSON layout. "Nothing else changes: same planner, verifier, scoring, items, modes, models and settings" ([PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md), Amendment 1). Why: "a pipeline check (extraction validity and planner errors only, no outcome metrics) showed that most extractions from providers without schema enforcement were invalid"; the models "extracted the correct content … in other JSON layouts". Timing: "before any C/D outcome was scored", but after seeing development data. Affects: the registered dev test stays C − A and is reported as registered (supported for gemma only; [paper/report.md](../paper/report.md) Appendix B, Table B1). C′ is development-informed on dev. It became the frozen EOP configuration of three models on held-out data, which is therefore a prospective test of an amended method ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §3). The amendment quotes interim counts (deepseek-v4-flash 525 of 538 invalid); the final file has 533 of 545 (EXPERIMENT_INDEX §5). The freeze record was written twice within two minutes, the second time after the C′ pools were renamed (EXPERIMENT_INDEX §6). `data/FREEZE_EOP.json` no longer verifies, by design.

**3. PREREG_EOP Amendment 2.** What: Bt "parses the JSON from the model's own message text with the standard plan parser … only where no function call was made"; Dt is Bt verified on C's extraction. No new calls. Why: under the structured prompt gemma +schema "wrote its reasoning and then the JSON answer as message text and made no function call in all 1,018 v3 dev responses, although the call was forced" ([PREREG_EOP.md](../experiments/preregistrations/PREREG_EOP.md), Amendment 2). Affects: gemma's structured-prompt and verifier rows only; registered B and D are reported unchanged. `data/FREEZE_EOP_A1.json` no longer verifies.

**4. PREREG_FINAL §8.** What: in `experiments/run_eop.py`, the test item sets behind `--allow-test`, a one-sided p for C′ − A, and a block for test F1; new analysis files (`experiments/analyze_final.py`, `src/msep/eval/extraction_match.py`, chain scripts). "No change to prompts, planning, verification or scoring" ([PREREG_FINAL.md](../experiments/preregistrations/PREREG_FINAL.md) §8). Made before any test response. Affects: no outcome; `data/FREEZE_EOP_A2.json` no longer verifies. The registration also differs from the earlier draft `HELDOUT_PLAN.md`: EOP on test is C′ for three models and C for gemma +schema; the parser is a baseline; T-OI-2 is descriptive; the EOP test is F1 (EXPERIMENT_INDEX §6).

**5. PREREG_ROBUST wording fix.** "One wording fix (parentheses around a negated compound statement) was made before the freeze, after the audit; all variants were regenerated and re-validated" (EXPERIMENT_INDEX §6). Affects: none after freezing.

**6. Scheduling restarts, 2026-11-14.** Held-out chains: all four started 20:05; qwen3.5-397b restarted at concurrency 24 at 20:17; gemma +schema paused at 20:17, resumed at concurrency 3 at 20:37 and restarted at concurrency 10 at 20:41. Rewording chains: gemma started 20:37 and restarted at concurrency 6 at 20:41 ([results/raw/final_chain_adaption-gemma-4-26b-a4b-it-schema.log](../results/raw/final_chain_adaption-gemma-4-26b-a4b-it-schema.log); EXPERIMENT_INDEX §6). Why: a shared limit of "about 25" concurrent requests (same log). Affects: timing only; cached jobs are never re-requested ([evaluation_protocol.md](evaluation_protocol.md) §6).

## 3. During the held-out run

**7. Network guard.** Committed 2026-11-14 23:28 with the message "pause run processes while the provider is unreachable, resume after (logged; no protocol change)" (`acd2207`). The log [results/raw/network_guard.log](../results/raw/network_guard.log) records two pauses of eight processes on 2026-11-15 (00:29:19 to 00:29:40, and 00:30:58 to 00:50:39). Why: a paused call cannot use up its three registered attempts while the network is down. The extended report adds: "The laptop that drove the experiments slept once and lost its connection more than once" ([paper/extended_report.md](../paper/extended_report.md) Appendix A). Affects: no prompt, item or setting.

**8. Provider outage, manual pause, and the first view of held-out results.**

| Time (UTC, 2026-11-15) | Event | Source |
|---|---|---|
| 19:57 | Provider answers every deepseek-v4-flash call with an error ("504 Gateway Time-out", then "502") | [INTERIM_NOTE.md](../results/aggregate/final_test/INTERIM_NOTE.md) |
| 20:22:42 | deepseek run paused by hand, "owner's instruction" | network_guard.log |
| 20:23:06 | Note committed fixing the rule for the missing calls, "before any held-out summary was produced or opened" | `c3aed44`; INTERIM_NOTE.md |
| 20:23 | Frozen analyses run on the incomplete data | commit message of `98e045d` |
| 20:32 | Interim held-out and rewording results committed | `98e045d` |
| 20:39 | Report sections drafted from the interim results | `639285d` |
| 20:54:41 | Run resumed by hand to test the provider; it answered at 20:55:30 | network_guard.log |
| 22:26:37 | deepseek held-out chain done, 7,759 of 7,759, before the 00:00 cut-off | network_guard.log; [final_chain_adaption-deepseek-v4-flash.log](../results/raw/final_chain_adaption-deepseek-v4-flash.log) |
| 22:28–22:35 | gemma chain run once more, giving its open calls their last attempt (rule 2 of the note) | final_chain_adaption-gemma-4-26b-a4b-it-schema.log |
| 22:46 | Final held-out and rewording results committed | `2863f90` |

At the first view the state was: qwen3.5 and qwen3.8 complete, gemma 7,751 of 7,759 calls answered, deepseek 6,740 of 7,759 (INTERIM_NOTE.md). Why the analysis was run then: "The project owner decided to look at the results now instead of waiting. This departs from PREREG_FINAL.md, which says the held-out results are analysed once, after every chain has finished" (same file). The note fixed in advance that the run would be resumed unchanged, that the frozen analysis would be re-run on complete data if it finished by 2026-11-16 00:00, and that "the interim numbers are not used to change any prompt, method, analysis or choice of what to report".

Interim against final: "Between the two analyses only deepseek's rows changed (native optimal-plan rate 0.73 with 108 unanswered items, then 0.98)" ([paper/report.md](../paper/report.md) Appendix B). The diff of [RESULTS_TABLES.md](../results/aggregate/final_test/RESULTS_TABLES.md) between `98e045d` and `2863f90` agrees: apart from layout, only deepseek rows changed. Its EOP − native difference went from +0.27 [+0.18, +0.38] to +0.02 [+0.01, +0.04] (Holm p < 0.001, then 0.004), and, in the over-intervention table, its test rate of acting on states sufficient from the start went from 0.25 to 0.00. In the rewording summary only the planner timing fields changed. Affects: every reported held-out number is from the complete data.

**9. Seven gemma calls.** "Seven calls, all of gemma, failed all three registered attempts and count as wrong. Every call of the other three models has an answer" ([paper/report.md](../paper/report.md) Appendix B). The interim note listed eight open gemma calls; the last-attempt pass of row 8 accounts for the difference (retrospective interpretation). On the development split, one gemma Diagnosis-Controlled response is missing and dropped from the denominator (400, not 401), and one gemma native T1B response is missing and counted as a failure (EXPERIMENT_INDEX §5).

## 4. Follow-up studies

**10. Studies 1 and 2 registered after the held-out results were viewed.** [PREREG_FOLLOWUP.md](../experiments/preregistrations/PREREG_FOLLOWUP.md) was committed with its freeze at 2026-11-15 21:03:18 (`fd8145c`). It states: "They were **proposed after the held-out results had been viewed** (first viewed 2026-11-15 20:23 UTC …). They are motivated by those results." Both use fresh train families. Affects: their tier; they are new evidence, not part of the original confirmation ([paper/report.md](../paper/report.md) §3.5).

**11. Chain restarts and fill passes.** All by hand, scheduling only, each with the reason written in the log.

| Chain | Time (UTC) | Change | Log |
|---|---|---|---|
| Study 1, qwen3.5-397b | 2026-11-15 22:27:49 | 9 workers instead of 5, "capacity freed by the end of the deepseek run" | [followup_chain_clarity_adaption-qwen3.5-397b.log](../results/raw/followup_chain_clarity_adaption-qwen3.5-397b.log) |
| Study 2, qwen3.8-27b | 2026-11-15 23:35:26 | 8 workers instead of 4 | [followup_chain_cost_adaption-qwen3.8-27b.log](../results/raw/followup_chain_cost_adaption-qwen3.8-27b.log) |
| Study 2, qwen3.5-397b | 2026-11-16 00:25:25 | 16 workers instead of 8 | [followup_chain_cost_adaption-qwen3.5-397b.log](../results/raw/followup_chain_cost_adaption-qwen3.5-397b.log) |
| Study 3, deepseek-v4-flash | 2026-11-16 00:54:13 | 16 workers instead of 5, "capacity freed by the end of Studies 1 and 2" | [repair_chain_adaption-deepseek-v4-flash.log](../results/raw/repair_chain_adaption-deepseek-v4-flash.log) |
| Study 1, gemma +schema | 2026-11-16 00:54:13 | fill pass: 871 jobs done, 1 error | [followup_chain_clarity_adaption-gemma-4-26b-a4b-it-schema.log](../results/raw/followup_chain_clarity_adaption-gemma-4-26b-a4b-it-schema.log) |
| Study 2, gemma +schema | 2026-11-16 00:56:15 | fill pass: 778 jobs done, 2 errors | [followup_chain_cost_adaption-gemma-4-26b-a4b-it-schema.log](../results/raw/followup_chain_cost_adaption-gemma-4-26b-a4b-it-schema.log) |

The chain script allows "two passes here, one fill pass if needed" ([experiments/chain_followup.sh](../experiments/chain_followup.sh)). The registered analysis of Studies 1 and 2 was "run once, 2026-11-16 00:57 UTC" (commit `35b07aa`). Affects: none on outcomes.

**12. Study 3 and its reading rule.** [PREREG_REPAIR.md](../experiments/preregistrations/PREREG_REPAIR.md) was committed with its freeze at 2026-11-16 00:13:31 (`2935522`) as an "exploratory follow-up, proposed after the held-out and rewording results had been viewed". It fixes one reading rule: "when a forced-schema answer contains no function call, the reader is given the message text instead." Why: "In the rewording study such answers were counted as empty; inspection of those raw records on 2026-11-16 showed that gemma had written its answer as message text." It calls this "the same kind of rule as Amendment 2". The count under the function-call-only reading is reported beside it: 29 of gemma's 174 first answers with prompt N would be accepted instead of 143 ([results/aggregate/repair/repair_report.md](../results/aggregate/repair/repair_report.md), "Counts"). Affects: Study 3 numbers for gemma. The rewording study was not re-scored, so its EOP-N figures for gemma understate that prompt ([paper/report.md](../paper/report.md) §4.4). A planned third arm with source-grounded, typed extraction "is **not run**", because it would touch frozen code (PREREG_REPAIR §0).

**13. Supplement for one registered interval.** PREREG_REPAIR §3 calls repair harmful "if the accepted-but-wrong rate rises with repair and the interval of that rise excludes 0". The frozen analysis printed the two rates but not the interval of their difference. [experiments/repair_supplement.py](../experiments/repair_supplement.py) computes it; it was "written after the frozen analysis had been run; it reads the same records through the same functions and changes nothing else" (module docstring). Output: [repair_supplement.json](../results/aggregate/repair/repair_supplement.json), committed with the Study 3 results at 2026-11-16 01:12 (`1b6af3b`). Affects: the harm reading of Study 3 (gemma: +0.09 [+0.03, +0.15] with the frozen prompt).

## 5. Known defects in analysis outputs

From [docs/EXPERIMENT_INDEX.md](../docs/EXPERIMENT_INDEX.md) §5. None changes a registered outcome.

| Defect | Effect |
|---|---|
| E5 fields `decoy_selected`, `decoy_only_plan` look for v2 action names and are 0.00 on v3 for every agent | Not to be read |
| The v3 dev report prints dev H2–H4 p values under "Confirmatory tests" | On dev they are exploratory |
| One gemma DxC response missing on dev (400 of 401); one gemma native T1B response missing (counted as failure) | Handled differently from each other |
| PROTOCOL.md "Not frozen"; §12 steps not done | Form only |
| Structured prompt, qwen3.5 dev: 252 of 1,018 unparsed, first reported as 225 | Corrected in place |
| "Every parsed C and C′ plan is optimal" too strong (registered C is 0.977 for qwen3.8) | Corrected in place |
| Exact-match check of dev extractions not stored in the EOP output | Rests on the gate report |
| No p value for C′ − A in the dev file | Intervals only |
| T1 "edit-tracking failure" rule met near ceiling by construction | Not evidence of a failure |
| Planned analyses absent: Cohen's h; H2–H4 on `heuristic_hard`; paired DC − E2E; redundant vs dearer split | Not reported |
| Condition labels differ between code (S2) and PREREG_EOP (S3) | Naming only |
| Amendment 1 quotes interim invalid counts (525 of 538) | Final: 533 of 545 |
| Stale documents (ROADMAP_MATRIX, CLAIMS, HELDOUT_PLAN) | Superseded |

## 6. Dating discrepancies

- **Commit offsets.** The pre-sprint commits and some commits of 2026-11-13 carry +0000; the other sprint commits carry −0800. The report states: "Times in this report are UTC. The author worked in Los Angeles (UTC−8): the follow-up studies and the final analyses, dated 2026-11-16 in UTC, fall on 2026-11-15 local time" ([paper/report.md](../paper/report.md) Appendix B).
- **Registration headers.** PREREG_T1B and PREREG_EOP date themselves 2026-11-14 (UTC); their commits are 2026-11-13 23:53 and 23:58 UTC (EXPERIMENT_INDEX §6). "The commit times are the authoritative ones" ([paper/extended_report.md](../paper/extended_report.md) Appendix C).
- **INTERIM_NOTE.md** says "Written 2026-11-15, 20:25 UTC"; it was committed at 20:23:06 UTC (`c3aed44`). The commit time is the earlier and authoritative one.
- **PREREG_REPAIR.md** says "Written on 2026-11-16, about 00:20 UTC"; it was committed at 00:13:31 UTC, and the Study 3 chains started at 00:17:53 ([repair_chain_adaption-gemma-4-26b-a4b-it-schema.log](../results/raw/repair_chain_adaption-gemma-4-26b-a4b-it-schema.log)). The header time is approximate; the commit precedes the first call.
- **PREREG_FOLLOWUP.md** says "about 21:00 UTC"; committed 21:03:18 UTC, chains started 21:03:31.
- **Recovery time.** The extended report says the provider "recovered at 20:54 UTC"; the log shows a resume by hand at 20:54:41 and the first answer at 20:55:30.
- **Freeze status.** EXPERIMENT_INDEX §6 re-checked the freeze records on 2026-11-14. A verification of `FREEZE_FOLLOWUP` and `FREEZE_REPAIR` is not recorded in the repository.
