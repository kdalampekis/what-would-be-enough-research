# Note written before the first look at held-out results

Written 2026-11-15, 20:25 UTC, and committed before any held-out summary was produced or opened.

## State of the runs

| Model | Calls with an answer | Of |
|---|---|---|
| qwen3.5-397b | 7,759 | 7,759 |
| qwen3.8-27b | 7,759 | 7,759 |
| gemma-4-26b +schema | 7,751 | 7,759 |
| deepseek-v4-flash | 6,740 | 7,759 |

Total 30,009 of 31,036 (96.7%). Seven of the eight chains finished. The eighth, the held-out test chain of
deepseek-v4-flash, was still in its first pass on the last step of the priority order (structured prompt on the
counterfactual pairs), with its second pass (retries of calls that failed once, 482 of them in the first step,
native planning) still to come.

## Why the analysis is run now

From 19:57 UTC the provider answered every deepseek-v4-flash call with an error (first "504 Gateway Time-out",
then "502: Model provider request failed"). About 190 calls failed in a row and none succeeded. The run was
paused by hand at 20:22 UTC so that calls that cannot succeed do not use up their three registered attempts.
The pause is logged in `results/raw/network_guard.log`.

The project owner decided to look at the results now instead of waiting. This departs from PREREG_FINAL.md, which
says the held-out results are analysed once, after every chain has finished. The frozen analysis scripts are used
unchanged.

## Rule for the missing deepseek-v4-flash calls, fixed before looking

1. The deepseek-v4-flash run is resumed, with the same commands and settings, as soon as the provider answers again.
   Nothing about it depends on what the results look like.
2. If its remaining calls finish by 2026-11-16 00:00 UTC, the frozen analysis is run again on the complete data and
   those are the reported results. The 8 open gemma-4-26b calls get their last attempt in the same pass.
3. If they do not, time has run out. The registered rule applies: the last step in the priority order (structured
   prompt on the counterfactual pairs) is dropped for all models alike. For the other steps, deepseek-v4-flash is
   reported with the calls it has, and the report states for each step how many are missing.
4. The interim numbers are not used to change any prompt, method, analysis or choice of what to report.
5. The report says that the results were first viewed with one model incomplete, and gives both sets of numbers
   if they differ.
