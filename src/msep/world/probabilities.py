"""Priors over world variables (used only by the posterior-threshold decision rule).

World variables get independent Bernoulli priors, conditioned on the
constraints. Computed variables are never given a prior: they are fixed facts,
handled in the worst case by the oracle.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Mapping

PRIOR_CHOICES = (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(3, 4))


def uniform_prior(world_vars) -> tuple[tuple[int, Fraction], ...]:
    return tuple((i, Fraction(1, 2)) for i in world_vars)


def random_prior(rng: random.Random, world_vars) -> tuple[tuple[int, Fraction], ...]:
    return tuple((i, rng.choice(PRIOR_CHOICES)) for i in world_vars)


def assignment_weight(assignment: Mapping[int, bool], prior: Mapping[int, Fraction]) -> Fraction:
    """Unnormalised prior weight of the world-variable part of an assignment."""
    w = Fraction(1)
    for i, p in prior.items():
        w *= p if assignment[i] else 1 - p
    return w
