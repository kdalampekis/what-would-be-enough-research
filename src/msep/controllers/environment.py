"""The agent-facing environment: the only way a realistic agent can learn anything.

It exposes the prompt text, an `execute(action)` call that returns the observed
values (by display handle) and charges the action's cost, and the spend so far.
The latent world and the oracle labels are held in a closure and are not
attributes of the object, so agent code cannot read them by accident.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StepLog:
    action: str
    cost: int
    observed: dict


class AgentEnvironment:
    __slots__ = ("prompt_text", "_execute", "_cost_of", "log", "max_steps")

    def __init__(self, prompt_text: str, execute, cost_of, max_steps: int = 50):
        self.prompt_text = prompt_text
        self._execute = execute
        self._cost_of = cost_of
        self.log: list[StepLog] = []
        self.max_steps = max_steps

    def execute(self, display_action: str) -> dict[str, bool]:
        if len(self.log) >= self.max_steps:
            raise RuntimeError("step limit reached")
        observed = self._execute(display_action)
        self.log.append(StepLog(display_action, self._cost_of(display_action), dict(observed)))
        return observed

    @property
    def spent(self) -> int:
        return sum(s.cost for s in self.log)


def environment_for(record: dict) -> AgentEnvironment:
    """Build the environment for one benchmark record. Only this function touches the
    latent world; it is called by the evaluation harness, never by an agent."""
    from msep.benchmark.schemas import instance_from_record

    inst = instance_from_record(record)
    alias_a = record["rendering"]["action_alias"]
    alias_v = record["rendering"]["var_alias"]
    formal_of = {v: k for k, v in alias_a.items()}
    names = [v.name for v in inst.state.variables]

    def execute(display_action: str) -> dict[str, bool]:
        if display_action not in formal_of:
            raise KeyError(f"no such action: {display_action}")
        values = inst.execute(formal_of[display_action])
        return {alias_v[names[i]]: v for i, v in values.items()}

    def cost_of(display_action: str) -> int:
        return inst.state.action_index[formal_of[display_action]].cost

    return AgentEnvironment(record["prompt_text"], execute, cost_of)
