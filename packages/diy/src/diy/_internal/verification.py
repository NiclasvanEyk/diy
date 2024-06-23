from typing import Any

from diy._internal.plan import ResolutionPlan
from diy._internal.planner import Planner
from diy.specification.protocol import SpecificationProtocol

type VerifiedSpecification = dict[type[Any], ResolutionPlan[..., Any]]


def verify_specification(spec: SpecificationProtocol) -> VerifiedSpecification:
    """
    Looks at all types in the specification and verifies they can actually be
    resolved at runtime.
    """

    planner = Planner(spec)

    plans: VerifiedSpecification = {}
    for type in spec.types():
        plans[type] = planner.plan(type)

    return plans
