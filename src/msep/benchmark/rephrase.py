"""Linguistic robustness variants (PREREG_ROBUST.md): the same formal state, worded differently.

Four kinds, each derived from one benchmark record. Handles (Q, F1, K2, ...), action names, costs, the
formal state and therefore every oracle label are unchanged; only the wording of the state description
changes. The task instructions and the output format that follow the description are not touched.

  lexical   same layout, order and rule notation; different terminology for everything else
  syntax    same terminology and order; facts, rules, known values and actions written as sentences
            with a different structure (rules in words: "K4 is true whenever K2 is false")
  reorder   canonical wording; sections and the items inside them in a different order
  prose     running paragraphs without list markup: the lexical terminology, the sentence forms and
            a different order together (the least template-like rendering)

Every unit of a variant (one line or sentence) is parsed back by `parse_blocks`, an inverse written for
these templates only, and the recovered state must equal the canonical one (experiments/generate_robust.py).
Nothing here is read by any oracle.
"""

from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass

from msep.actions.base import Resource
from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.certified_tasks import OpaqueTask
from msep.world.constraints import And, Iff, Implies, Not, Or, Var, render
from msep.world.state import FormalState, LogicalEntailment, Rule, Variable, VarKind

from .parsing import ParseError, _FormulaParser
from .rendering import Rendering

GENERATOR_VERSION = "rb-v1"
KINDS = ("lexical", "syntax", "reorder", "prose")

CANON = {
    "decision": "Decision: is it true that {label} (Q)?",
    "facts_h": "Facts about the world (each is true or false):",
    "comp_h": "Computational facts (each is fully determined by inputs shown here; its certified value is not "
              "yet known):",
    "rules_h": "Rules (all of these are true):",
    "actions_h": "Available actions:",
    "tv": ("is true", "is false", "are true", "are false"),
    "tail": "Decision rule: a decision about Q is justified only if it follows with certainty from the rules "
            "and the known values.\n"
            "Information actions (ASK_...) are the only way to obtain new evidence about the world. Computation "
            "actions run a certified procedure (code execution, a primality test, a SAT solver, or an exact "
            "posterior calculation) on inputs you already have; a computational fact becomes part of the decision "
            "state only through its certified result, not through an uncertified estimate. You are choosing a plan "
            "before running anything: actions are chosen together, before any result is seen.",
}
ALT = {
    "decision": "Question to settle: does the following hold: {label}? Call this statement Q.",
    "facts_h": "Conditions in the world (each one either holds or does not hold):",
    "comp_h": "Derived results (each one is completely fixed by the inputs given here; its verified outcome has "
              "not been obtained yet):",
    "rules_h": "Constraints (every one of them holds):",
    "actions_h": "Steps you can take:",
    "tv": ("holds", "does not hold", "hold", "do not hold"),
    "tail": "Standard for deciding: an answer about Q is warranted only when it follows with certainty from the "
            "constraints and the values established so far.\n"
            "Evidence queries (the ASK_... steps) are the sole means of obtaining new evidence about the world. "
            "Calculations execute a verified procedure (running code, a primality check, a SAT solver, or an exact "
            "posterior computation) on inputs already in your possession; a derived result enters the decision "
            "state only via its verified outcome, never via an unverified guess. You are selecting a plan before "
            "executing anything: the steps are selected together, before any outcome is seen.",
}
PROSE = {
    "decision": "You need to settle one question: is it the case that {label}? We refer to this statement as Q.",
    "facts_h": "Several conditions in the world matter here, and each of them either holds or does not hold.",
    "comp_h": "There are also derived results; each is completely fixed by the inputs given here, but its "
              "verified outcome has not been obtained yet.",
    "rules_h": "The situation obeys the following constraints, all of which hold.",
    "actions_h": "You can take the following steps, each at a price.",
}


@dataclass(frozen=True)
class Block:
    kind: str            # decision | facts | comp | rules | known | actions | tail
    header: str | None
    units: tuple[str, ...]
    style: str           # which templates the units use: canon | alt | sent | prose


def variant_seed(instance_id: str, kind: str) -> int:
    return int(hashlib.sha256(f"{GENERATOR_VERSION}:{instance_id}:{kind}".encode()).hexdigest()[:12], 16)


def _join(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


# -- rules in words -----------------------------------------------------------------------------------------

def _simple(f) -> bool:
    """A literal. Everything else, including a negated compound, is parenthesised when it is an argument:
    "it is not the case that (X) and Y" could otherwise be read with the negation over the conjunction."""
    return isinstance(f, Var) or (isinstance(f, Not) and isinstance(f.arg, Var))


def say(f, names, rng: random.Random, tv) -> str:
    """A formula as a sentence. Every compound argument is parenthesised, so the reading is unique."""
    if isinstance(f, Var):
        return f"{names[f.index]} {tv[0]}"
    if isinstance(f, Not):
        if isinstance(f.arg, Var):
            return f"{names[f.arg.index]} {tv[1]}"
        return f"it is not the case that ({say(f.arg, names, rng, tv)})"
    w = lambda g: say(g, names, rng, tv) if _simple(g) else f"({say(g, names, rng, tv)})"  # noqa: E731
    if isinstance(f, (And, Or)):
        parts = [w(a) for a in f.args]
        if rng.random() < 0.5:
            parts.reverse()
        return (" and " if isinstance(f, And) else " or ").join(parts)
    if isinstance(f, Implies):
        a, b = w(f.left), w(f.right)
        form = rng.randrange(3)
        if form == 0 and isinstance(f.right, Not):
            form = 1  # consequent-first only for a positive consequent: "X does not hold whenever ..." can be misread
        return (f"{b} whenever {a}", f"whenever {a}, {b}", f"in every case where {a}, {b}")[form]
    if isinstance(f, Iff):
        a, b = w(f.left), w(f.right)
        if rng.random() < 0.5:
            a, b = b, a
        return f"{a} {('exactly when', 'precisely when')[rng.randrange(2)]} {b}"
    raise TypeError(f"not a formula: {f!r}")


def _cap(s: str) -> str:
    return s[0].upper() + s[1:]


class _SentenceParser:
    """Inverse of `say` (validation only)."""

    def __init__(self, text: str, index: dict[str, int]):
        self.toks = [t if t in index else t.lower() for t in re.findall(r"\(|\)|,|[A-Za-z_][A-Za-z_0-9]*", text)]
        self.i, self.index = 0, index

    def peek(self, n=1):
        return self.toks[self.i:self.i + n]

    def take(self, *expected):
        if self.peek(len(expected)) != list(expected):
            raise ParseError(f"expected {expected}, got {self.peek(len(expected))}")
        self.i += len(expected)

    def parse(self):
        f = self.sentence()
        if self.i != len(self.toks):
            raise ParseError(f"trailing tokens: {self.toks[self.i:]}")
        return f

    def sentence(self):
        for lead in (["whenever"], ["in", "every", "case", "where"]):
            if self.peek(len(lead)) == lead:
                self.i += len(lead)
                a = self.primary()
                self.take(",")
                return Implies(a, self.primary())
        left = self.primary()
        if self.peek() == ["whenever"]:
            self.take("whenever")
            return Implies(self.primary(), left)
        if self.peek(2) in (["exactly", "when"], ["precisely", "when"]):
            self.i += 2
            return Iff(left, self.primary())
        for word, cls in (("and", And), ("or", Or)):
            if self.peek() == [word]:
                parts = [left]
                while self.peek() == [word]:
                    self.take(word)
                    parts.append(self.primary())
                return cls(tuple(parts))
        return left

    def primary(self):
        if self.peek() == ["("]:
            self.take("(")
            f = self.sentence()
            self.take(")")
            return f
        if self.peek(6) == ["it", "is", "not", "the", "case", "that"]:
            self.i += 6
            self.take("(")
            f = self.sentence()
            self.take(")")
            return Not(f)
        (h,) = self.peek() or [None]
        if h not in self.index:
            raise ParseError(f"expected a handle, got {h!r}")
        self.i += 1
        for words, pos in ((["is", "true"], True), (["is", "false"], False), (["does", "not", "hold"], False),
                           (["holds"], True)):
            if self.peek(len(words)) == words:
                self.i += len(words)
                return Var(self.index[h]) if pos else Not(Var(self.index[h]))
        raise ParseError(f"no truth value after {h}")


# -- rendering ----------------------------------------------------------------------------------------------

def _known_unit(known: list[tuple[str, bool]], style: str) -> str:
    if style in ("canon", "alt"):
        v = (CANON if style == "canon" else ALT)["tv"]
        body = "; ".join(f"{h} {v[0] if val else v[1]}" for h, val in known)
        return ("Known so far: " + (body or "nothing")) if style == "canon" else \
            ("Established so far: " + (body or "nothing yet"))
    v = (CANON if style == "sent" else ALT)["tv"]
    groups = []
    for val in dict.fromkeys(val for _, val in known):  # order of first appearance
        hs = [h for h, x in known if x == val]
        if style == "prose" and not val and len(hs) > 1:  # "A and B do not hold" could be read as "not both"
            groups.append(f"neither {hs[0]} nor {hs[1]} holds" if len(hs) == 2 else f"none of {_join(hs)} holds")
        else:
            groups.append(f"{_join(hs)} {v[(0 if val else 1) + (2 if len(hs) > 1 else 0)]}")
    if style == "sent":
        return "Known so far: " + ("; ".join(groups) + "." if groups else "no value is known yet.")
    return ("At this point it has been established that " + " and that ".join(groups) + ".") if groups else \
        "At this point nothing has been established yet."


def _action_unit(name: str, info: bool, cost: int, reveals: list[str], style: str, rng: random.Random) -> str:
    if style == "canon":
        return (f"{name} ({'information' if info else 'computation'}, cost {cost}): "
                f"{'find out' if info else 'run the certified procedure and record'} the value of {', '.join(reveals)}")
    if style == "alt":
        return (f"{name} ({'evidence query' if info else 'calculation'}, price {cost}): "
                + (f"learn the actual status of {', '.join(reveals)}" if info else
                   f"execute the verified procedure and note the outcome for {', '.join(reveals)}"))
    what = _join(reveals)
    if style == "sent":
        val = "the value of" if len(reveals) == 1 else "the values of"
        does = f"finds out {val} {what}" if info else f"runs the certified procedure and records {val} {what}"
        kind = "information" if info else "computation"
        return (f"For a cost of {cost}, the {kind} action {name} {does}.",
                f"{name} is {'an' if info else 'a'} {kind} action with cost {cost} that {does}.")[rng.randrange(2)]
    kind = "evidence query" if info else "calculation"
    does = f"reveals the actual status of {what}" if info else \
        f"executes the verified procedure and reports the outcome for {what}"
    return (f"Paying {cost} lets you use the {kind} {name}, which {does}.",
            f"The {kind} {name} has a price of {cost}; it {does}.")[rng.randrange(2)]


def build_blocks(state: FormalState, r: Rendering, kind: str, seed: int) -> list[Block]:
    """The variant as ordered blocks. `r.action_alias` must already hold the display action names."""
    if kind not in KINDS:
        raise ValueError(kind)
    if not isinstance(state.decision_rule, LogicalEntailment):
        raise ValueError("only logical-entailment states are supported")
    rng = random.Random(seed)
    handle = {i: r.var_alias[x.name] for i, x in enumerate(state.variables)}
    style = {"lexical": "alt", "syntax": "sent", "reorder": "canon", "prose": "prose"}[kind]
    voc = {"alt": ALT, "sent": CANON, "canon": CANON, "prose": PROSE}[style]
    tv = (ALT if style == "prose" else CANON)["tv"]
    shuffle = kind in ("reorder", "prose")

    def order(xs: list) -> list:
        if shuffle and len(xs) > 1:
            first = list(xs)
            for _ in range(8):  # a different order whenever one exists
                rng.shuffle(xs)
                if xs != first:
                    break
        return xs

    def define(i: int) -> str:
        h, label = handle[i], r.var_label[handle[i]]
        return {"canon": f"{h}: {label}", "alt": f"{h}: {label}", "sent": f"{h} stands for the statement that {label}.",
                "prose": f"{h} says that {label}."}[style]

    world = order(sorted((i for i in state.world_vars() if i != state.target), key=lambda i: handle[i]))
    comp = order(sorted(state.computed_vars(), key=lambda i: handle[i]))
    rules = sorted(state.rules, key=lambda x: render(x.formula, handle))
    if r.order_seed is not None:
        random.Random(r.order_seed).shuffle(rules)
    rules = order(rules)
    rule_units = []
    for k, rule in enumerate(rules, 1):
        if style in ("canon", "alt"):
            rule_units.append(f"{k}. {render(rule.formula, handle)}")
        else:
            s = _cap(say(rule.formula, handle, rng, tv)) + "."
            rule_units.append(f"{k}. {s}" if style == "sent" else s)
    known = order(sorted(((handle[i], val) for i, val in state.known.items())))
    acts = order(sorted(state.actions, key=lambda a: r.action_alias[a.name]))
    act_units = []
    for a in acts:
        rev = sorted(handle[x] for x in a.reveals)
        if shuffle and len(rev) > 1:
            rng.shuffle(rev)
        act_units.append(_action_unit(r.action_alias[a.name], a.resource is Resource.INFORMATION, a.cost, rev, style, rng))
    blocks = {
        "facts": Block("facts", voc["facts_h"], tuple(define(i) for i in world), style),
        "comp": Block("comp", voc["comp_h"], tuple(define(i) for i in comp), style),
        "rules": Block("rules", voc["rules_h"], tuple(rule_units), style),
        "known": Block("known", None, (_known_unit(known, style),), style),
        "actions": Block("actions", voc["actions_h"], tuple(act_units), style),
    }
    seq = ["facts", "comp", "rules", "known", "actions"]
    if kind == "reorder":
        seq = (["actions", "known", "rules", "facts", "comp"], ["known", "actions", "facts", "comp", "rules"],
               ["rules", "actions", "comp", "facts", "known"], ["actions", "rules", "known", "comp", "facts"])[rng.randrange(4)]
    elif kind == "prose":
        seq = (["facts", "comp", "rules", "known", "actions"], ["facts", "comp", "known", "actions", "rules"],
               ["actions", "facts", "comp", "rules", "known"])[rng.randrange(3)]
    if not comp:
        seq = [s for s in seq if s != "comp"]
    label = r.var_label["Q"]
    head = (ALT if style == "alt" else PROSE if style == "prose" else CANON)["decision"].format(label=label)
    tail = (ALT if style in ("alt", "prose") else CANON)["tail"]
    return [Block("decision", None, (head,), style), *[blocks[s] for s in seq], Block("tail", None, (tail,), style)]


def assemble(blocks: list[Block]) -> str:
    """Blocks to text. List styles: one unit per indented line; prose: one paragraph per block. The two
    definition blocks (facts, computational facts) stay together, as in the canonical text."""
    paras: list[list[str]] = []
    prev = None
    for b in blocks:
        prose = b.style == "prose"
        if b.kind in ("decision", "known", "tail"):
            lines = [b.units[0]]
        elif prose:
            lines = [" ".join([b.header, *b.units])]
        else:
            lines = [b.header, *[f"  {u}" for u in b.units]]
        if prev in ("facts", "comp") and b.kind in ("facts", "comp"):
            if prose:
                paras[-1][-1] += " " + lines[0]
            else:
                paras[-1] += lines
        else:
            paras.append(lines)
        prev = b.kind
    return "\n\n".join("\n".join(p) for p in paras)


def render_variant(state: FormalState, r: Rendering, kind: str, instance_id: str) -> tuple[str, list[Block]]:
    blocks = build_blocks(state, r, kind, variant_seed(instance_id, kind))
    return assemble(blocks), blocks


# -- inverse (validation only) ------------------------------------------------------------------------------

_ACTION_RX = (
    (r"^(?P<n>\S+) \((?P<k>information|computation), cost (?P<c>\d+)\): .* the value of (?P<r>.*)$", None),
    (r"^(?P<n>\S+) \((?P<k>evidence query|calculation), price (?P<c>\d+)\): .* (?:status of|outcome for) (?P<r>.*)$", None),
    (r"^For a cost of (?P<c>\d+), the (?P<k>information|computation) action (?P<n>\S+) .* the values? of (?P<r>.*)\.$", None),
    (r"^(?P<n>\S+) is an? (?P<k>information|computation) action with cost (?P<c>\d+) that .* the values? of (?P<r>.*)\.$", None),
    (r"^Paying (?P<c>\d+) lets you use the (?P<k>evidence query|calculation) (?P<n>\S+), which .* (?:status of|outcome for) (?P<r>.*)\.$", None),
    (r"^The (?P<k>evidence query|calculation) (?P<n>\S+) has a price of (?P<c>\d+); it .* (?:status of|outcome for) (?P<r>.*)\.$", None),
)


def parse_blocks(blocks: list[Block]) -> FormalState:
    """Rebuild the formal state from the units of a variant, using only their text."""
    world, comp, rules_txt, known, actions = [], [], [], {}, []
    for b in blocks:
        for u in b.units:
            if b.kind in ("facts", "comp"):
                m = re.match(r"^([FK]\d+)(?:: | stands for the statement that | says that )", u)
                if not m:
                    raise ParseError(f"definition: {u[:60]}")
                (world if b.kind == "facts" else comp).append(m.group(1))
            elif b.kind == "rules":
                rules_txt.append((re.sub(r"^\d+\. ", "", u), b.style))
            elif b.kind == "known":
                body = re.sub(r"^(Known so far: |Established so far: |At this point it has been established that )", "", u)
                if body.rstrip(".") in ("nothing", "nothing yet", "no value is known yet",
                                        "At this point nothing has been established yet"):
                    continue
                for g in re.split(r"; | and that ", body.rstrip(".")):
                    m = re.match(r"^(neither |none of )(.*) holds$", g)
                    if m:
                        hs, val = m.group(2), False
                    else:
                        m = re.match(r"^(.*?) (is true|are true|holds|hold|is false|are false|does not hold|do not hold)$", g)
                        if not m:
                            raise ParseError(f"known: {g}")
                        hs, val = m.group(1), m.group(2) in ("is true", "are true", "holds", "hold")
                    for h in re.findall(r"[FK]\d+", hs):
                        known[h] = val
                    if re.sub(r"[FK]\d+|,| and | nor |\s", "", hs):
                        raise ParseError(f"known: {g}")
            elif b.kind == "actions":
                for rx, _ in _ACTION_RX:
                    m = re.match(rx, u)
                    if m:
                        break
                else:
                    raise ParseError(f"action: {u}")
                kind = "information" if m.group("k") in ("information", "evidence query") else "computation"
                actions.append((m.group("n"), kind, int(m.group("c")), re.findall(r"[FK]\d+", m.group("r"))))
    names = ["Q", *world, *comp]
    index = {n: i for i, n in enumerate(names)}
    variables = tuple(Variable(n, VarKind.COMPUTED if n in comp else VarKind.WORLD) for n in names)
    rules = []
    for k, (t, style) in enumerate(rules_txt):
        f = _FormulaParser(t, index).parse() if style in ("canon", "alt") else _SentenceParser(t.rstrip("."), index).parse()
        rules.append(Rule(f"R{k + 1}", f))
    info = tuple(InformationAction(n, tuple(index[h] for h in rv), c) for n, k, c, rv in actions if k == "information")
    compa = tuple(ComputationAction(n, tuple(index[h] for h in rv), c) for n, k, c, rv in actions if k == "computation")
    return FormalState(variables=variables, rules=tuple(rules), target=0,
                       evidence=tuple(sorted((index[h], v) for h, v in known.items() if h in world)),
                       computed=tuple(sorted((index[h], v) for h, v in known.items() if h in comp)),
                       info_actions=info, comp_actions=compa,
                       compute_tasks=tuple((index[h], OpaqueTask(h)) for h in comp), decision_rule=LogicalEntailment())
