"""Inverse of rendering: rebuild a formal state from the prompt text alone.

Two uses:
1. Validation of the rendering (ASSUMPTIONS A11): for every benchmark instance,
   parse(render(state)) must equal the state up to renaming. Then the text the
   agent sees carries all the information the oracle uses.
2. The deterministic state extractor for the realistic planner. It reads only
   the text. It works because this benchmark's rendering is regular; it is a
   tool, not evidence that an LLM can extract the state (see controllers/).

The parsed state uses display handles (Q, F1, K2, ...) as variable names and
display action names.
"""

from __future__ import annotations

import re
from fractions import Fraction

from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.certified_tasks import CnfSatisfiable, ModPow, PosteriorAbove, Primality
from msep.world.constraints import And, Iff, Implies, Not, Or, Var
from msep.world.state import FormalState, LogicalEntailment, PosteriorThreshold, Rule, Variable, VarKind


class ParseError(ValueError):
    pass


# -- formulas ---------------------------------------------------------------------------

_TOKEN = re.compile(r"\(|\)|[A-Za-z_][A-Za-z_0-9]*")


class _FormulaParser:
    def __init__(self, text: str, index: dict[str, int]):
        self.toks = _TOKEN.findall(text)
        self.i = 0
        self.index = index

    def peek(self, k: int = 0):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else None

    def take(self, expected: str | None = None) -> str:
        t = self.peek()
        if t is None or (expected is not None and t != expected):
            raise ParseError(f"expected {expected!r}, got {t!r}")
        self.i += 1
        return t

    def parse(self):
        f = self.expr()
        if self.peek() is not None:
            raise ParseError(f"trailing tokens: {self.toks[self.i:]}")
        return f

    def expr(self):
        if self.peek() == "if":
            self.take("if")
            left = self.or_expr()
            self.take("then")
            right = self.or_expr()
            return Implies(left, right)
        left = self.or_expr()
        if self.toks[self.i:self.i + 4] == ["if", "and", "only", "if"]:
            self.i += 4
            return Iff(left, self.or_expr())
        return left

    def or_expr(self):
        parts = [self.and_expr()]
        while self.peek() == "or":
            self.take("or")
            parts.append(self.and_expr())
        return parts[0] if len(parts) == 1 else Or(tuple(parts))

    def and_expr(self):
        parts = [self.unary()]
        # In "X if and only if Y" the token after X is "if", so this loop never eats that "and".
        while self.peek() == "and":
            self.take("and")
            parts.append(self.unary())
        return parts[0] if len(parts) == 1 else And(tuple(parts))

    def unary(self):
        t = self.peek()
        if t == "not":
            self.take("not")
            return Not(self.unary())
        if t == "(":
            self.take("(")
            f = self.expr()
            self.take(")")
            return f
        name = self.take()
        if name not in self.index:
            raise ParseError(f"unknown variable {name!r}")
        return Var(self.index[name])


# -- tasks -----------------------------------------------------------------------------------

def parse_task(desc: str):
    m = re.fullmatch(r"pow\((\d+), (\d+), (\d+)\) equals (\d+)", desc)
    if m:
        return ModPow(*map(int, m.groups()))
    m = re.fullmatch(r"(\d+) is a prime number", desc)
    if m:
        return Primality(int(m.group(1)))
    m = re.fullmatch(r"the following constraint set over x1\.\.x(\d+) is satisfiable "
                     r"\(all (\d+) clauses true at once\): (.*)", desc)
    if m:
        clauses = []
        for c in re.findall(r"\(([^)]*)\)", m.group(3)):
            lits = []
            for part in c.split(" or "):
                part = part.strip()
                neg = part.startswith("not ")
                v = int(part[(5 if neg else 1):] if neg else part[1:])
                lits.append(-v if neg else v)
            clauses.append(tuple(lits))
        if len(clauses) != int(m.group(2)):
            raise ParseError("clause count mismatch")
        return CnfSatisfiable(int(m.group(1)), tuple(clauses))
    m = re.fullmatch(r"P\(H \| all \w+ observations seen\) exceeds ([0-9.]+), where P\(H\) = ([0-9/]+), "
                     r"the observations are independent given H and given not H, and (.*)", desc)
    if m:
        liks = tuple((Fraction(a), Fraction(b)) for a, b in
                     re.findall(r"P\(seen \| H\) = ([0-9/]+), P\(seen \| not H\) = ([0-9/]+)", m.group(3)))
        return PosteriorAbove(Fraction(m.group(2)), liks, Fraction(m.group(1)))
    raise ParseError(f"unrecognised computation task: {desc[:60]}")


# -- whole state --------------------------------------------------------------------------------

def parse_state(text: str, opaque_tasks: bool = False) -> FormalState:
    """opaque_tasks=True keeps computation tasks as descriptions that cannot be evaluated
    (agent-side use: certified results only through the environment)."""
    lines = text.splitlines()
    world: list[str] = []
    comp: dict[str, str] = {}
    rules_txt: list[str] = []
    known: dict[str, bool] = {}
    actions = []
    prior: dict[str, Fraction] = {}
    tau = None
    section = None
    for line in lines:
        if line.startswith("Facts about the world"):
            section = "world"
            continue
        if line.startswith("Computational facts"):
            section = "comp"
            continue
        if line.startswith("Rules ("):
            section = "rules"
            continue
        if line.startswith("Prior probabilities"):
            section = "prior"
            continue
        if line.startswith("Known so far:"):
            body = line.split(":", 1)[1].strip()
            if body != "nothing":
                for h, v in re.findall(r"([FK]\d+) is (true|false)", body):
                    known[h] = v == "true"
            section = None
            continue
        if line.startswith("Available actions:"):
            section = "actions"
            continue
        if line.startswith("Decision rule:"):
            m = re.search(r"probability is at least ([0-9/]+)", line)
            tau = Fraction(m.group(1)) if m else None
            section = None
            continue
        if not line.strip():
            continue
        if section == "world":
            m = re.match(r"\s+(F\d+): ", line)
            if m:
                world.append(m.group(1))
        elif section == "comp":
            m = re.match(r"\s+(K\d+): (.*)$", line)
            if m:
                comp[m.group(1)] = m.group(2)
        elif section == "rules":
            m = re.match(r"\s+\d+\. (.*)$", line)
            if m:
                rules_txt.append(m.group(1))
        elif section == "prior":
            m = re.match(r"\s+P\(([FK]\d+) is true\) = ([0-9/]+)", line)
            if m:
                prior[m.group(1)] = Fraction(m.group(2))
        elif section == "actions":
            m = re.match(r"\s+(\S+) \((information|computation), cost (\d+)\): .* the value of (.*)$", line)
            if m:
                actions.append((m.group(1), m.group(2), int(m.group(3)), [x.strip() for x in m.group(4).split(",")]))
    names = ["Q", *world, *sorted(comp, key=lambda h: int(h[1:]))]
    index = {n: i for i, n in enumerate(names)}
    variables = tuple(Variable(n, VarKind.COMPUTED if n.startswith("K") else VarKind.WORLD) for n in names)
    rules = tuple(Rule(f"R{k + 1}", _FormulaParser(t, index).parse()) for k, t in enumerate(rules_txt))
    info, compa = [], []
    for name, kind, cost, reveals in actions:
        idx = tuple(index[h] for h in reveals)
        (info if kind == "information" else compa).append(
            (InformationAction if kind == "information" else ComputationAction)(name, idx, cost))
    if opaque_tasks:
        from msep.world.certified_tasks import OpaqueTask
        tasks = tuple((index[h], OpaqueTask(d)) for h, d in comp.items())
    else:
        tasks = tuple((index[h], parse_task(d)) for h, d in comp.items())
    evidence = tuple(sorted((index[h], v) for h, v in known.items() if h.startswith("F")))
    computed = tuple(sorted((index[h], v) for h, v in known.items() if h.startswith("K")))
    if tau is not None:
        pri = {index[h]: p for h, p in prior.items()}
        pri[0] = Fraction(1, 2)
        rule, prior_t = PosteriorThreshold(tau), tuple(sorted(pri.items()))
    else:
        rule, prior_t = LogicalEntailment(), ()
    return FormalState(variables=variables, rules=rules, target=0, evidence=evidence, computed=computed,
                       info_actions=tuple(info), comp_actions=tuple(compa), compute_tasks=tasks,
                       decision_rule=rule, prior=prior_t)
