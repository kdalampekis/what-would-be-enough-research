# Speaker script (about 3.5 minutes)

For `paper/presentation.pptx`. Numbers are from `paper/report.md` and the result files it cites.

## Slide 1. Title

Hello. Our project asks one question: when an agent cannot answer yet, can it tell what would be enough to settle the question, and when to stop?

## Slide 2. The question

Take a simple case. An experiment run is approved only if the protocol is current and a checksum matches. The agent can ask a person, cost three; run the checksum, cost one; or request an audit, cost five. If it already knows the protocol is out of date, it needs nothing: the answer is no. If it knows nothing, it should ask and run the checksum, cost four. If nobody can be asked, it should defer. Doing too little is reckless. Doing too much wastes time and attention.

## Slide 3. MSEP and the oracle

We made this exact. A state has rules, known values and priced actions. A plan is sufficient if every possible result settles the question, and optimal if it is also the cheapest. An exact solver finds every cheapest plan, and a brute-force check agreed on all 228,199 labels. The benchmark has 300 problem families.

## Slide 4. Held-out results

Our first surprise: the strong models are good. On held-out families, three of four models find a cheapest sufficient plan on 93 to 98 percent of solvable states. The weakest, gemma, manages 42 percent. Most of our registered hypotheses about where models fail were not supported.

## Slide 5. Stopping and the wording artifact

One strong model seemed to keep acting on 20 percent of states that were already settled. We traced most of that to our own text: it said computed values were "not yet known" while also listing some as known. With clearer wording, the rate fell from 14 to 3 percent. Gemma's failure is real: it still acted on 59 percent, never deferred, and ignored prices.

## Slide 6. EOP, the parser and rewording

Then we tried a fix. The model only extracts the formal state, and an exact planner chooses the actions. It scores 99 to 100 percent. But a simple parser with no model scores 100 percent too. So we reworded the problems. The parser collapsed. The qwen models still extracted correctly. Deepseek and gemma broke on some wordings.

## Slide 7. Repair and silent errors

So the bottleneck moved from planning to translation. We tried one repair call. For gemma, exact states rose from 21 to 78 percent. But accepted wrong states also rose, from 7 to 16 percent. In a new offline analysis, exploratory and done after seeing these results, we planned on each accepted wrong state. Most still gave the right plan. Three of 174 gave something worse: an immediate, confident wrong answer. A parser accepting an answer does not mean the answer is right.

## Slide 8. Conclusion and next direction

Our conclusion: exact formal planning gives reliable plans, but only when the formal state faithfully represents the task. Wording, benchmark ambiguity and silent errors limit reliability end to end. The next step is translation that can show it is faithful: citing sources, independent checks, several translations that must agree, and abstaining when unsure. Thank you.
