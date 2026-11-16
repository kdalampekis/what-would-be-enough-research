"""Action schema shared by information and computation actions.

An action reveals the values of a fixed set of variables at a positive cost.
Which kind of variable it may reveal is fixed by its type and checked when a
FormalState is built: information actions reveal only world variables,
computation actions reveal only computed variables.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class Resource(str, Enum):
    INFORMATION = "information"
    COMPUTATION = "computation"


@dataclass(frozen=True)
class Action:
    name: str
    reveals: tuple[int, ...]
    cost: int = 1

    resource: ClassVar[Resource]  # fixed by subclass, not settable per instance

    def __post_init__(self) -> None:
        if type(self) is Action:
            raise TypeError("use InformationAction or ComputationAction")
        if not self.name or not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"bad action name {self.name!r}")
        if not self.reveals:
            raise ValueError(f"action {self.name} reveals nothing")
        if len(set(self.reveals)) != len(self.reveals):
            raise ValueError(f"action {self.name} lists a variable twice")
        if type(self.cost) is not int or self.cost < 1:
            raise ValueError(f"action {self.name}: cost must be a positive integer")

    def to_json(self) -> dict:
        return {"name": self.name, "type": self.resource.value,
                "reveals": list(self.reveals), "cost": self.cost}
