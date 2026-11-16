# ROBUST_AUDIT.md — independent reading of a sample of reworded items (2026-11-14)

Done before the robustness dataset was frozen and before any model saw a robustness item.

## What was done

- **Sample:** 24 variants of **train-split** states (6 per wording kind, 24 different families, seed
  20261114, texts under 7,000 characters). Train items, so that no evaluation item was read.
- **Reader:** a separate Claude agent. It received only the 24 texts: no code, no data, no labels, no
  description of the generator. **It is a language model, not a person.** A human audit was not done.
- **Task:** write down the formal state it understood (variables and kinds, rules in logic notation, known
  values, actions with kind, cost and reveals) and list every phrase with more than one reasonable reading.
- **Check:** its 24 states were compared with the true states by program
  (`src/msep/eval/extraction_match.py`).
- Files: `results/aggregate/robust_dev/audit/` (sample, the reader's output, the key).

## Result

- **States:** 24 of 24 equal to the true state (6 of 6 for each of lexical, syntax, reorder, prose).
- **Rules:** the reader found no rule with two non-equivalent readings.

## Wording issues the reader raised

**Introduced by the rewording — fixed before the freeze**

- "It is not the case that (X) exactly when Y": the negation could attach to X or to the whole sentence.
  For "exactly when" both readings are logically the same, but the same shape with "and" / "or" would not
  be. Fix: a negated compound statement that is an argument of another connective is now parenthesised
  ("(it is not the case that (X)) and Y"). Earlier fixes, found while writing the generator: "X does not
  hold in every case where Y" (now "in every case where Y, X …"; consequent-first "whenever" only with a
  positive consequent) and "A and B do not hold" in prose (now "neither A nor B holds" / "none of … holds").
  After the fix all 548 dev variants and all 5,076 train variants were regenerated and validated again
  (0 failures). The 24 audited texts were read before this last fix; the fix only adds parentheses.

**Inherited from the canonical benchmark text — kept, because the variants must say what the canonical
text says**

These are properties of frozen benchmark v3, present in the canonical wording too. They are reported as
limitations of the benchmark, not of the rewording.

- The header of the computational facts says the certified value "is not yet known", while the known
  values can include a computational fact (18 of 24 texts). The intended reading: the known list is
  authoritative. Most of these states also still offer the computation action for the known fact.
- The closing paragraph says a computational fact enters the decision state "only through its certified
  result", next to rules that link facts; whether a value entailed by the rules counts is not spelled out
  there (the decision rule sentence says it does: "follows with certainty from the rules and the known
  values").
- Abstract-skin items: "is it true that Q holds (Q)?" and "fact D holds" have no content beyond the
  label; one text uses "fact H" beside a task description that mentions "P(H | …)".
- Double negations written out ("not (not F3)"), actions that reveal an already known value, a joint
  action costing the same as one of its parts, the same rule stated twice in contrapositive form.

**Judged awkward, not ambiguous:** consequent-first sentences ("B holds whenever A holds") mixed with
antecedent-first ones; "the certified procedure" in the singular for an action that computes two facts;
reveal order differing from the action name in the reorder and prose variants.

## What the audit does and does not show

It shows that a careful reader recovers the intended state from each sampled text, and it found one
scope risk that was fixed. It is one reader, a language model, on 24 texts. It does not show that every
human would read every variant the same way.
