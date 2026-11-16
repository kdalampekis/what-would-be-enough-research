"""Minimal transformations that turn a base scenario into matched siblings.

Siblings share the theory (variables, rules, computation tasks) and the latent
world. They differ only in what is already known and which actions are on
offer. Every transformation returns a short human-readable description that is
stored with the instance.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from msep.actions.base import Action
from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.state import FormalState, Instance, VarKind


def set_known(instance: Instance, var_indices: Iterable[int]) -> FormalState:
    """Fix these variables at their true values (world: observed, computed: computed)."""
    full = instance.full_assignment()
    return instance.state.with_knowledge({i: full[i] for i in var_indices})


def set_menu(state: FormalState, actions: Iterable[Action]) -> FormalState:
    info = tuple(a for a in actions if isinstance(a, InformationAction))
    comp = tuple(a for a in actions if isinstance(a, ComputationAction))
    return replace(state, info_actions=info, comp_actions=comp)


def describe_knowledge(state: FormalState) -> str:
    known = [state.variables[i].name for i in sorted(state.known)]
    unknown = [v.name for i, v in enumerate(state.variables) if i not in state.known and i != state.target]
    return f"known: {', '.join(known) or 'nothing'}; unknown: {', '.join(unknown) or 'nothing'}"


def kinds_of(state: FormalState, names: Iterable[str]) -> dict[str, str]:
    return {n: state.variables[i].kind.value for n in names
            for i, v in enumerate(state.variables) if v.name == n}


__all__ = ["set_known", "set_menu", "describe_knowledge", "kinds_of", "VarKind"]
