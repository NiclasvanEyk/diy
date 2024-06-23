from collections.abc import Callable
from typing import override

from diy.container.protocol import ContainerProtocol
from diy._internal.planner import Planner
from diy.specification.default import Specification
from diy.specification.protocol import SpecificationProtocol


class RuntimeContainer(ContainerProtocol):
    """
    A container that tries to construct dependencies at
    runtime.

    Note that it accepts any spec, even invalid ones with circular
    dependencies, uncallable builder functions, and the likes. If you prefer
    something a little more safe, have a look at :class:`VerifyingContainer`.
    """

    def __init__(self, spec: SpecificationProtocol | None = None) -> None:
        super().__init__()
        self._spec = spec or Specification()
        self._planner = Planner(self._spec)

    @override
    def resolve[T](self, abstract: type[T]) -> T:
        plan = self._planner.plan(abstract)
        return plan.execute()

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        plan = self._planner.plan_call(function)
        return plan.execute()


__all__ = ["RuntimeContainer"]
