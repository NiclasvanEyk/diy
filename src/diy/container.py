from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Protocol, override

from diy.internal.planner import Planner
from diy.specification import Specification


class Container(Protocol):
    # TODO: Write documentation

    @abstractmethod
    def resolve[T](self, abstract: type[T]) -> T:
        pass  # pragma: no cover

    @abstractmethod
    def call[R](self, function: Callable[..., R]) -> R:
        pass  # pragma: no cover


class RuntimeContainer(Container):
    """
    A :class:`Container` that reflects dependencies at runtime.

    It mostly defers to a `class`:Planner instance to resolve the dependency
    chain and then simply executes said plan.
    """

    def __init__(self, spec: Specification | None = None) -> None:
        super().__init__()
        self._planner = Planner(spec or Specification())

    @override
    def resolve[T](self, abstract: type[T]) -> T:
        plan = self._planner.plan(abstract)
        return plan.execute()

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        plan = self._planner.plan_call(function)
        return plan.execute()
