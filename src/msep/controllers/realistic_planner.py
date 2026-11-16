"""Epistemic Obligation Planner, realistic variant (B): a CANDIDATE mitigation, not a result.

Distinction (see README and CLAIMS.md):
- (A) `obligation_planner.py` is the oracle planner. It receives the exact formal
  state and the instance; it is part of the oracle and validation, not a mitigation.
- (B) this module sees only what an agent sees: the prompt text and an
  `AgentEnvironment` whose `execute()` returns observed values. It never receives
  the latent world or any oracle label. Whether it helps LLM agents has NOT been
  evaluated: that needs real model runs (Phase 2B/3).

Pipeline, each stage a replaceable component:

    StateExtractor        text -> formal state            (rule-based parser now; LLM extractor later)
    ObligationIdentifier  state -> unresolved obligations (exact, SAT)
    CandidateGenerator    state -> available actions
    ObligationVerifier    (action, obligation) -> discharges?
    PlanSearch            obligations x actions -> min-cost plan (weighted hitting set)
    SufficiencyChecker    state -> decided? (and the answer)
    Executor/StopRule     run one action, add its observations, re-plan; stop when decided;
                          defer when no plan exists or the step budget runs out

With the rule-based extractor, (B) plans exactly as (A) would, because this
benchmark's text fully determines the formal state. That condition is an upper
bound for a tool-using agent, not evidence about LLMs. The research question
is (B) with an LLM extractor (S2) or LLM-estimated action effects (S4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

from msep.benchmark.parsing import parse_state
from msep.obligations.discharge import discharges
from msep.obligations.extraction import extract
from msep.obligations.model import Obligation
from msep.oracle.logic import status
from msep.oracle.sufficiency import Status
from msep.world.state import FormalState, LogicalEntailment

from .environment import AgentEnvironment


# -- component interfaces --------------------------------------------------------------

class StateExtractor(Protocol):
    def extract(self, text: str) -> FormalState: ...


class ObligationIdentifier(Protocol):
    def identify(self, state: FormalState) -> list[Obligation]: ...


class PlanSearch(Protocol):
    def search(self, state: FormalState, obligations: list[Obligation]) -> tuple[str, ...] | None: ...


# -- default implementations ---------------------------------------------------------------

class ParserExtractor:
    """Rule-based extractor for this benchmark's rendering (exact on it, useless elsewhere)."""

    def extract(self, text: str) -> FormalState:
        # Opaque tasks: the planner cannot evaluate a certified computation itself; it must
        # run the computation action in the environment.
        return parse_state(text, opaque_tasks=True)


class PerturbedExtractor:
    """SYNTHETIC test tool: wraps an extractor and injects extraction errors at a fixed
    rate (drop a rule, forget a known value, miss an action). Used to exercise the
    pipeline under imperfect extraction; it is not a model of any LLM."""

    def __init__(self, base: StateExtractor, rate: float, seed: int = 0):
        self.base, self.rate, self.seed = base, rate, seed

    def extract(self, text: str) -> FormalState:
        import random
        from dataclasses import replace
        st = self.base.extract(text)
        rng = random.Random(f"{self.seed}:{hash(text) & 0xFFFFFFFF}")
        rules = tuple(r for r in st.rules if rng.random() >= self.rate) or st.rules[:1]
        ev = tuple(x for x in st.evidence if rng.random() >= self.rate)
        cp = tuple(x for x in st.computed if rng.random() >= self.rate)
        info = tuple(a for a in st.info_actions if rng.random() >= self.rate)
        comp = tuple(a for a in st.comp_actions if rng.random() >= self.rate)
        return replace(st, rules=rules, evidence=ev, computed=cp, info_actions=info, comp_actions=comp)


class ExactObligations:
    def identify(self, state: FormalState) -> list[Obligation]:
        obs, truncated = extract(state)
        if truncated:
            raise RuntimeError("obligation enumeration truncated")
        return obs


class CandidateGenerator:
    def candidates(self, state: FormalState):
        return list(state.actions)


class ObligationVerifier:
    def verifies(self, state: FormalState, action, ob: Obligation) -> bool:
        return discharges(state, action, ob)


class HittingSetSearch:
    def __init__(self, verifier: ObligationVerifier | None = None, candidates: CandidateGenerator | None = None):
        self.verifier = verifier or ObligationVerifier()
        self.candidates = candidates or CandidateGenerator()

    def search(self, state: FormalState, obligations: list[Obligation]) -> tuple[str, ...] | None:
        if not obligations:
            return ()
        acts = self.candidates.candidates(state)
        w = WCNF()
        for o in obligations:
            clause = [j + 1 for j, a in enumerate(acts) if self.verifier.verifies(state, a, o)]
            if not clause:
                return None
            w.append(clause)
        for j, a in enumerate(acts):
            w.append([-(j + 1)], weight=a.cost)
        with RC2(w) as rc2:
            model = rc2.compute()
        chosen = set(model or [])
        return tuple(sorted(a.name for j, a in enumerate(acts) if (j + 1) in chosen))


class SufficiencyChecker:
    def decided(self, state: FormalState) -> bool | None:
        """True/False if the knowledge entails q / not-q; None if undetermined."""
        s = status(state)
        return True if s is Status.ENTAILED else False if s is Status.CONTRADICTED else None


# -- the controller ------------------------------------------------------------------------------

@dataclass
class PlannerTrace:
    outcome: str = ""                 # answered | deferred | step_limit
    decision: bool | None = None
    steps: list[dict] = field(default_factory=list)
    initial_plan: tuple[str, ...] | None = None
    total_cost: int = 0
    final_known: list[str] = field(default_factory=list)  # handles known at the end (audit of information flow)


@dataclass
class EpistemicObligationPlanner:
    extractor: StateExtractor = field(default_factory=ParserExtractor)
    obligations: ObligationIdentifier = field(default_factory=ExactObligations)
    search: PlanSearch = field(default_factory=HittingSetSearch)
    checker: SufficiencyChecker = field(default_factory=SufficiencyChecker)
    max_steps: int = 20

    def plan(self, text: str) -> dict:
        """Static plan only (no execution): what the planner would do, for plan-level scoring."""
        state = self.extractor.extract(text)
        if not isinstance(state.decision_rule, LogicalEntailment):
            return {"supported": False, "plan": None, "state_sufficient": None}
        decided = self.checker.decided(state)
        if decided is not None:
            return {"supported": True, "state_sufficient": True, "plan": (), "decision": decided}
        obs = self.obligations.identify(state)
        return {"supported": True, "state_sufficient": False, "plan": self.search.search(state, obs),
                "obligations": [o.describe(state) for o in obs]}

    def run(self, env: AgentEnvironment) -> PlannerTrace:
        trace = PlannerTrace()
        state = self.extractor.extract(env.prompt_text)
        if not isinstance(state.decision_rule, LogicalEntailment):
            trace.outcome = "unsupported_rule"
            return trace
        for step in range(self.max_steps + 1):
            decided = self.checker.decided(state)
            if decided is not None:
                trace.outcome, trace.decision = "answered", decided
                break
            obs = self.obligations.identify(state)
            plan = self.search.search(state, obs)
            if step == 0:
                trace.initial_plan = plan
            if plan is None:
                trace.outcome = "deferred"
                break
            if step == self.max_steps:
                trace.outcome = "step_limit"
                break
            # next action: discharges the most obligations; ties by cost, then name
            nxt = min(plan, key=lambda n: (-sum(discharges(state, state.action_index[n], o) for o in obs),
                                           state.action_index[n].cost, n))
            observed = env.execute(nxt)
            idx = {v.name: i for i, v in enumerate(state.variables)}
            learned = {idx[h]: v for h, v in observed.items()}
            trace.steps.append({"action": nxt, "observed": observed})
            state = state.with_knowledge(learned)
        trace.total_cost = env.spent
        trace.final_known = sorted(state.variables[i].name for i in state.known)
        return trace
