from collections.abc import Callable
from typing import Any, overload, override

from diy._internal.planner import Planner
from diy.container.protocol import ContainerProtocol
from diy.specification.default import Specification
from diy.specification.protocol import SpecificationProtocol


class Container(ContainerProtocol, SpecificationProtocol):
    """
    The default and most flexible implementation of a Container.

    It is a specification and container at the same time, so you can teach it
    how to construct types, as well as resolve ones.

    While this seems simple, since you only need to construct one "thing", it
    may be hard to trace down when a builder was registered, and by whom. This
    can theoretically happen at any time.
    """

    def __init__(self, spec: SpecificationProtocol | None = None) -> None:
        super().__init__()
        self._spec = spec or Specification()
        self._planner = Planner(self._spec)

    # =========================================================================
    # SpecificationProtocol
    # =========================================================================

    @overload
    def add[T](self, builder: Callable[..., T]) -> Callable[..., T]:
        """
        Mark an existing function as a builder for an abstract type.
        """

    @overload
    def add[T](self, builder: type[T], name: str) -> Callable[..., T]:
        """
        Mark the function as a supplier for the named constructor parameter of
        the given type.
        """

    @overload
    def add(self, builder: type[Any]) -> None:
        """
        Simply tell the container, that this type exists.

        This helps containers to verify that this type should be "buildable" in
        the future. This means that all its parameters should have known
        constructors.
        """

    @override
    def add[T](
        self, builder: Callable[..., Any] | type[T], name: str | None = None
    ) -> Callable[..., Any] | None:
        return self._spec.add(builder, name)

    @override
    def get[T](
        self, abstract: type[T], name: str | None = None
    ) -> Callable[..., T] | None:
        return self._spec.get(abstract, name)

    @override
    def types(self) -> set[type[Any]]:
        return self._spec.types()

    # =========================================================================
    # ContainerProtocol
    # =========================================================================

    @override
    def resolve[T](self, abstract: type[T]) -> T:
        plan = self._planner.plan(abstract)
        return plan.execute()

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        plan = self._planner.plan_call(function)
        return plan.execute()


__all__ = ["Container"]
