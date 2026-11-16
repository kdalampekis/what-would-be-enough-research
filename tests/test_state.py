import inspect

import pytest

from msep.actions.base import Action
from msep.actions.computation import ComputationAction
from msep.actions.information import InformationAction
from msep.world.compute_tasks import Divisible
from msep.world.state import FormalState, Instance, LatentWorld

from helpers import A, C, Q, and_state


def test_information_cannot_reveal_computed():
    st = and_state()
    with pytest.raises(ValueError, match="information action"):
        FormalState(variables=st.variables, rules=st.rules, target=Q,
                    info_actions=(InformationAction("ASK_C", (C,), 1),), compute_tasks=st.compute_tasks)


def test_computation_cannot_reveal_world():
    st = and_state()
    with pytest.raises(ValueError, match="computation action"):
        FormalState(variables=st.variables, rules=st.rules, target=Q,
                    comp_actions=(ComputationAction("COMPUTE_A", (A,), 1),), compute_tasks=st.compute_tasks)


def test_action_type_is_not_a_parameter():
    with pytest.raises(TypeError):
        InformationAction("X", (A,), 1, resource="computation")
    with pytest.raises(TypeError):
        Action("X", (A,), 1)


def test_computation_execute_has_no_world_access():
    params = list(inspect.signature(ComputationAction.execute).parameters)
    assert params == ["self", "tasks"]


def test_wrong_computed_value_rejected():
    st = and_state()
    with pytest.raises(ValueError, match="computed value"):
        FormalState(variables=st.variables, rules=st.rules, target=Q, computed=((C, False),),
                    compute_tasks=((C, Divisible(391, 17)),))


def test_latent_world_must_satisfy_rules():
    st = and_state()
    with pytest.raises(ValueError, match="violates"):
        Instance(st, LatentWorld(((Q, False), (A, True), (3, False))))  # C is true, so q must be true
