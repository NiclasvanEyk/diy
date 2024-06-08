from __future__ import annotations

from collections.abc import Callable
from typing import override

from diy.container.protocol import ContainerProtocol
from diy.internal.planner import Planner
from diy.internal.verification import verify_specification
from diy.specification.protocol import SpecificationProtocol


class VerifyingContainer(ContainerProtocol):
    """
    A container that verifies and caches the passed specification.

    While a :class:`RuntimeContainer` needs to construct an inference plan from
    the ground up every an instance is requested, :class:`VeryifyingContainer`s
    store each plan. This requires a bit more memory, but should be faster.

    It also is more safe, since when e.g. there is a circular dependency. You
    would already notice it when constructing the container, instead of
    failing unexpectetly somewhere in the future. However, this means you fail,
    even when the invalid dependency could potentially never be requested from
    the container.

    This also enables you to verify containers during tests, thereby catching
    misconfigured specifications early in the development process.
    """

    def __init__(self, spec: SpecificationProtocol) -> None:
        super().__init__()
        self._spec = verify_specification(spec)
        self._planner = Planner(spec)
        self._verified_spec = verify_specification(spec)

    @override
    def resolve[T](self, abstract: type[T]) -> T:
        plan = self._spec.get(abstract)
        if plan is None:
            plan = self._planner.plan(abstract)
            self._verified_spec[abstract] = plan
        return plan.execute()

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        plan = self._planner.plan_call(function)
        return plan.execute()


__all__ = ["VerifyingContainer"]
