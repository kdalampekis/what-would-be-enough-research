"""Which actions discharge which obligations."""

from __future__ import annotations

from typing import Iterable

from msep.actions.base import Action
from msep.world.state import FormalState

from .model import Obligation


def discharges(state: FormalState, action: Action, ob: Obligation) -> bool:
    r = set(action.reveals)
    return state.target in r or bool(r & ob.variables)


def discharge_map(state: FormalState, obligations: Iterable[Obligation]) -> dict[str, list[str]]:
    """obligation id -> names of actions that can discharge it."""
    return {ob.id: [a.name for a in state.actions if discharges(state, a, ob)] for ob in obligations}


def action_discharges(state: FormalState, obligations: Iterable[Obligation]) -> dict[str, list[str]]:
    """action name -> ids of obligations it can discharge (the action's declared effect)."""
    obs = list(obligations)
    return {a.name: [ob.id for ob in obs if discharges(state, a, ob)] for a in state.actions}


def undischarged(state: FormalState, plan: Iterable[str], obligations: Iterable[Obligation]) -> list[Obligation]:
    acts = [state.action_index[a] for a in plan]
    return [ob for ob in obligations if not any(discharges(state, a, ob) for a in acts)]


def unresolvable(state: FormalState, obligations: Iterable[Obligation]) -> list[Obligation]:
    """Obligations no available action can discharge (they make the state NEITHER)."""
    return [ob for ob in obligations if not any(discharges(state, a, ob) for a in state.actions)]
