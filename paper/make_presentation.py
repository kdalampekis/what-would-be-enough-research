"""Build paper/presentation.pptx: 8 slides, 16:9, neutral style, speaker notes on every slide.

Numbers come from paper/report.md and the result files it cites (results/aggregate/final_test,
results/aggregate/followup, results/aggregate/repair, including silent_errors.json). Figures from figures/.

    .venv/bin/python paper/make_presentation.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)
ACCENT = RGBColor(0x1F, 0x4E, 0x79)
RULE = RGBColor(0xCC, 0xCC, 0xCC)
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, runs, size=18, color=INK, bold=False, space=6):
    """runs: list of paragraphs; a paragraph is a str or a list of (text, bold) pieces."""
    tf = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        for piece, b in ([(para, bold)] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = piece
            r.font.size, r.font.name, r.font.bold = Pt(size), FONT, b
            r.font.color.rgb = color
    return tf


def slide(title, notes, kicker=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    if kicker:
        text(s, 0.6, 0.35, 12, 0.4, [kicker], size=13, color=ACCENT, bold=True)
    text(s, 0.6, 0.65, 12.2, 0.9, [title], size=28, bold=True)
    line = s.shapes.add_connector(1, Inches(0.6), Inches(1.5), Inches(12.73), Inches(1.5))
    line.line.color.rgb, line.line.width = RULE, Pt(1)
    s.notes_slide.notes_text_frame.text = notes
    return s


def bullets(s, x, y, w, h, items, size=18):
    text(s, x, y, w, h, [[("–  ", False)] + (it if isinstance(it, list) else [(it, False)]) for it in items], size=size, space=10)


def table(s, x, y, w, rows, col_w=None, size=14, h=0.42):
    t = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h * len(rows))).table
    for j, cw in enumerate(col_w or []):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor(0xEE, 0xF2, 0xF6) if i == 0 else RGBColor(0xFF, 0xFF, 0xFF)
            c.text = ""
            r = c.text_frame.paragraphs[0].add_run()
            r.text = str(val)
            r.font.size, r.font.name, r.font.bold = Pt(size), FONT, i == 0
            r.font.color.rgb = INK
    return t


def picture(s, name, x, y, w=None, h=None):
    s.shapes.add_picture(str(FIG / name), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


# 1. Title
s = prs.slides.add_slide(BLANK)
text(s, 0.9, 2.2, 11.5, 1.6, ["What Would Be Enough?"], size=44, bold=True)
text(s, 0.9, 3.25, 11.5, 1.0, ["Evaluating Minimal Sufficient Epistemic Plans in LLM Agents"], size=26, color=MUTED)
line = s.shapes.add_connector(1, Inches(0.9), Inches(4.3), Inches(4.5), Inches(4.3))
line.line.color.rgb, line.line.width = ACCENT, Pt(3)
text(s, 0.9, 4.55, 11.5, 1.2, ["Konstantinos Dalampekis · University of California, Los Angeles",
                               "With Apart Research · AI x Epistemics Research Sprint, November 2026"], size=16, color=MUTED)
s.notes_slide.notes_text_frame.text = (
    "Title. One question: when an agent cannot yet answer, can it tell what would be enough to settle the question, "
    "and when to stop? Work done in the AI x Epistemics sprint; the formal model, oracle and benchmark were built "
    "before the sprint, every model run during it.")

# 2. The question
s = slide("Can the agent tell what would be enough?",
          "Walk through the approval example. Approval holds exactly when the protocol is current and a checksum matches. "
          "Three actions with prices. The right answer changes with what is already known: nothing more, ask plus compute "
          "(cost 4, not the audit route at cost 6), or defer because nothing available can settle it. Doing too little "
          "decides without grounds; doing too much wastes compute and people's attention; acting when the matter is settled "
          "shows the agent does not know what its evidence supports.", kicker="The question")
text(s, 0.6, 1.75, 6.3, 1.2, [[("Approve the experiment run?  ", True), ("Yes exactly when the protocol version is current "
                                                                          "and the configuration checksum matches.", False)]], size=18)
table(s, 0.6, 3.0, 6.2, [["Action", "Resource", "Cost"], ["Ask a person about the protocol", "information", "3"],
                         ["Run the checksum", "computation", "1"], ["Request an audit (covers the protocol)", "information", "5"]],
      col_w=[3.6, 1.7, 0.9], size=15)
table(s, 7.3, 1.85, 5.45, [["What is already known", "What is enough"], ["Protocol is out of date", "Nothing: answer no"],
                           ["Nothing", "Ask + checksum (cost 4), not audit + checksum (6)"],
                           ["Nobody can be asked", "No action settles it: defer"]], col_w=[2.2, 3.25], size=15, h=0.6)
text(s, 0.6, 5.4, 12.1, 1.5, ["Sufficient: the plan settles the question whatever the results.   Minimal: the cheapest such plan.   "
                              "Stopping: act only when acting is needed, defer when nothing can help."], size=16, color=MUTED)

# 3. MSEP and the oracle
s = slide("MSEP: a task with exact answers",
          "A state has rules over a target Q, known values, and priced information and computation actions. A plan is chosen "
          "before any result is seen and is sufficient if every outcome leaves Q decided. The oracle finds every cheapest "
          "sufficient plan as a minimum-cost hitting set over obligations, by SAT and MaxSAT, and a separate brute-force path "
          "re-checked every label: 228,199 checks, zero disagreements. 300 families, 2,282 states; splits by family. "
          "Five resource classes: already sufficient, information only, computation only, both, neither.",
          kicker="Formalization")
bullets(s, 0.6, 1.8, 6.0, 4.8, [
    [("State: ", True), ("rules over a target Q, known values, priced information and computation actions", False)],
    [("Plan: ", True), ("a set of actions chosen before any result is seen", False)],
    [("Sufficient ", True), ("if every outcome leaves Q decided; ", False), ("optimal ", True), ("if also cheapest", False)],
    [("Oracle: ", True), ("cheapest plan = minimum-cost hitting set of obligations (SAT / MaxSAT); "
                          "228,199 brute-force re-checks, 0 disagreements", False)],
    [("Benchmark: ", True), ("300 families, 2,282 states; train 165 / dev 72 / held-out 63 families", False)],
], size=17)
picture(s, "architecture.png", 6.85, 2.0, w=6.0)
text(s, 6.85, 4.75, 6.0, 0.8, ["Conditions: native answer (A), structured prompt (B), EOP = model extracts the state + exact "
                               "planner, parser + planner (no model). The scoring oracle is separate and sees the true state."],
     size=12, color=MUTED)

# 4. Held-out results
s = slide("Held-out: three of four models plan near ceiling",
          "Held-out split, 63 families, Detection-Controlled, all attempted. Native optimal-plan rate: qwen3.5 0.93, qwen3.8 "
          "0.98, deepseek 0.98, gemma 0.42. EOP 1.00, 1.00, 1.00, 0.99; the parser with no model also reaches 1.00. The "
          "registered hypotheses (diagnosis easier than planning, relevance confused with sufficiency, both-resource states "
          "harder) were mostly not supported. The V marker in the figure is a verifier-only variant reported in the extended "
          "report; it follows the structured prompt. Price follow-up: qwen models give the cheapest plan on 0.95 above and "
          "0.97/0.98 below the price boundary; gemma 0.31 and 0.16 while its plans are sufficient on 0.89.",
          kicker="Evaluation")
picture(s, "conditions_test.png", 0.6, 1.75, w=12.1)
table(s, 0.6, 6.05, 12.1, [["", "qwen3.5-397b", "qwen3.8-27b", "deepseek-v4-flash", "gemma-4-26b +schema"],
                           ["Native / structured / EOP / parser", "0.93 / 0.62 / 1.00 / 1.00", "0.98 / 0.96 / 1.00 / 1.00",
                            "0.98 / 0.94 / 1.00 / 1.00", "0.42 / 0.40 / 0.99 / 1.00"]],
      col_w=[3.3, 2.2, 2.2, 2.2, 2.2], size=13, h=0.38)

# 5. Stopping
s = slide("Stopping: partly our wording, partly real",
          "On 169 held-out states that one edit had just made sufficient, qwen3.5 still acted on 0.20 and gemma on 0.72. "
          "Our text said every computational value 'is not yet known' while also listing some as known; 21 of qwen3.5's 34 "
          "unnecessary plans only re-obtained listed values (exploratory). Follow-up Study 1, registered after the held-out "
          "view, on 60 fresh families: with clarified wording qwen3.5 falls from 0.14 to 0.03, gemma from 0.73 to 0.59, both "
          "Holm p < 0.001. The registered result stands as measured; its interpretation changes. gemma's failure is real.",
          kicker="Failure analysis")
table(s, 0.6, 1.85, 7.0, [["Acts on already-sufficient states", "qwen3.5-397b", "gemma-4-26b"],
                          ["Held-out, newly sufficient (registered)", "0.20", "0.72"],
                          ["Study 1, original wording", "0.14", "0.73"],
                          ["Study 1, clarified wording", "0.03", "0.59"]], col_w=[3.8, 1.6, 1.6], size=16, h=0.55)
bullets(s, 8.0, 1.85, 4.8, 4.5, [
    [("Confound: ", True), ("the text said computed values are \"not yet known\" while listing some as known", False)],
    "21 of qwen3.5's 34 unnecessary plans re-obtained listed values",
    [("Real: ", True), ("gemma never defers when nothing helps and ignores prices", False)],
], size=17)
text(s, 0.6, 5.0, 7.0, 1.2, ["A benchmark that states what is known inconsistently measures how a model resolves the "
                             "inconsistency, not whether it knows when to stop."], size=16, color=ACCENT)

# 6. EOP, parser, rewording
s = slide("EOP works where extraction works",
          "On the benchmark's own wording EOP reaches 0.99 to 1.00, but so does a parser with no model, so the canonical "
          "score does not show that a model is needed. Rewording study: the same 137 development states in four wordings. "
          "The parser scores 0.00 on three of four. qwen models' EOP holds. On syntax wording deepseek's EOP falls to 0.81 "
          "while its native stays at 0.98; gemma's falls to 0.05. Most failures are visible, rejected by the planner; on prose "
          "24 of 137 of gemma's extractions are well-formed and wrong.", kicker="Mitigation and its boundary")
picture(s, "robustness.png", 0.6, 1.7, h=5.5)
bullets(s, 9.6, 1.85, 3.3, 5.3, [
    "Canonical wording: EOP 0.99–1.00, parser also 1.00",
    "Rewording: parser 0.00 on 3 of 4",
    "qwen EOP holds",
    "deepseek syntax: EOP 0.81 vs native 0.98",
    "gemma syntax: EOP 0.05",
], size=16)

# 7. Repair and silent errors
s = slide("Repair recovers states and lets some wrong ones through",
          "Study 3, exploratory, 174 reworded items from 12 fresh families. One repair call with the reader's message: gemma "
          "exact state 0.21 to 0.78, optimal plan 0.29 to 0.93, but accepted-but-wrong extractions rise from 0.07 to 0.16. "
          "deepseek 0.89 to 0.97 with none accepted-but-wrong. New offline analysis, exploratory and post hoc, no model calls: "
          "we planned on each accepted-but-wrong state and scored the plan on the true state. With gemma and repair, 23 of 27 "
          "still gave an optimal plan, the planner rejected one, and 3 (0.02 of items, 1 before repair) answered at once with "
          "the wrong value. Parser acceptance is not proof of semantic correctness.", kicker="Repair and silent errors")
table(s, 0.6, 1.85, 6.6, [["gemma-4-26b +schema, frozen prompt", "First", "With repair"],
                          ["Exact state", "0.21", "0.78"], ["Optimal plan", "0.29", "0.93"],
                          ["Accepted but wrong", "0.07", "0.16"]], col_w=[3.8, 1.4, 1.4], size=16, h=0.55)
text(s, 0.6, 4.4, 6.6, 0.8, ["deepseek-v4-flash: exact state 0.89 → 0.97, no accepted-but-wrong extraction."], size=15, color=MUTED)
text(s, 7.6, 1.8, 5.2, 0.5, ["27 accepted-but-wrong states, gemma with repair"], size=15, bold=True)
table(s, 7.6, 2.4, 5.1, [["Plan on the true state", "Count"], ["Still optimal", "23"], ["Rejected by the planner", "1"],
                         ["Immediate wrong answer", "3"]], col_w=[3.7, 1.4], size=16, h=0.55)
text(s, 7.6, 4.8, 5.2, 1.0, ["Exploratory, post hoc (designed 2026-11-15). Silent consequential errors: 0.02 [0.01, 0.03] "
                              "of items with repair, 1 item before."], size=13, color=MUTED)
text(s, 0.6, 5.95, 12.1, 1.0, ["Parser acceptance, an exact state and a correct decision are three different properties."],
     size=18, color=ACCENT, bold=True)

# 8. Conclusion
s = slide("Formal correctness is conditional on semantic faithfulness",
          "Conclusion: exact formal planning gives reliable epistemic plans, conditional on a faithful representation of the "
          "task. Linguistic variation, benchmark ambiguity and silent semantic errors limit end-to-end reliability. Next: "
          "formalizations that can establish when their translation is faithful enough to act on: source-grounded extraction, "
          "constrained decoding, independent semantic checks and roundtrips, several formalizations that must agree, targeted "
          "repair, calibrated abstention, human-written ambiguous tasks, and measuring the consequences of undetected errors. "
          "Limits: synthetic tasks, four open-weight models from one provider, one sample per item; follow-ups designed after "
          "the held-out view.", kicker="Conclusion and next direction")
bullets(s, 0.6, 1.8, 6.0, 4.8, [
    "Strong models plan near ceiling and follow prices",
    "Most apparent stopping error came from our own text; gemma's errors are real",
    "An exact planner removes planning errors and moves the bottleneck to translation",
    "Repair recovers states but cannot tell a well-formed wrong state from a right one",
], size=18)
text(s, 7.1, 1.8, 5.7, 0.5, ["Next: faithful language-to-formal translation"], size=18, bold=True, color=ACCENT)
bullets(s, 7.1, 2.4, 5.7, 4.3, [
    "Extraction that cites its source sentence",
    "Typed or constrained decoding",
    "Independent semantic checks and roundtrips",
    "Several formalizations; act only when they agree",
    "Calibrated abstention; targeted repair",
    "Human-written ambiguous tasks; measure the cost of undetected errors",
], size=16)

out = HERE / "presentation.pptx"
prs.save(out)
print(f"wrote {out} ({len(prs.slides)} slides)")
