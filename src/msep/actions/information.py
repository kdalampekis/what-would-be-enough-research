"""Information actions: observe external-world variables.

`execute` needs the latent world. It returns only the values of the variables
the action reveals and performs no inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from typing import TYPE_CHECKING

from .base import Action, Resource

if TYPE_CHECKING:
    from msep.world.state import LatentWorld


@dataclass(frozen=True)
class InformationAction(Action):
    resource: ClassVar[Resource] = Resource.INFORMATION

    def execute(self, world: "LatentWorld") -> dict[int, bool]:
        return {v: world.value(v) for v in self.reveals}
