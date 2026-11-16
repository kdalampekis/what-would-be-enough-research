"""Computation actions: evaluate tasks over data the agent already has.

`execute` receives only the computation tasks (visible instance data). It has
no access to the latent world, so it cannot reveal a hidden world variable.
The tests check this structurally (the signature) and behaviourally
(outcomes are identical across every world consistent with the instance).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from typing import Mapping

from msep.world.compute_tasks import ComputeTask

from .base import Action, Resource


@dataclass(frozen=True)
class ComputationAction(Action):
    resource: ClassVar[Resource] = Resource.COMPUTATION

    def execute(self, tasks: Mapping[int, ComputeTask]) -> dict[int, bool]:
        return {v: tasks[v].evaluate() for v in self.reveals}
