from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Protocol, override

from diy.internal.planner import Planner
from diy.internal.verification import verify_specification
from diy.specification import Specification


class Container(Protocol):
    """
    The protocol all containers in this package adhere to.

    Use this one when typing method parameters, since then they will be able to
    accept **any** container implementation. Since you usually don't care how a
    container is implemented internally, this can be considered a bes
    practise.
    """

    @abstractmethod
    def resolve[T](self, abstract: type[T]) -> T:
        """
        Retrieves an instance of the given type from the container.

        Depending on how the container was configured, this could return a
        shared instance (also referred to as a _singleton_), construct a fresh
        one, or even fail, since the container does not know the type or does
        not have enough information how to build it.
        """
        pass  # pragma: no cover

    @abstractmethod
    def call[R](self, function: Callable[..., R]) -> R:
        """
        Calls the given function after resolving all required parameters from
        the container.
        """
        pass  # pragma: no cover


class RuntimeContainer(Container):
    """
    A [`Container`](diy.Container) that tries to construct dependencies at
    runtime.

    Note that it accepts any spec, even invalid ones with circular
    dependencies, uncallable builder functions, and the likes. If you prefer
    something a little more safe, have a look at :class:`VerifyingContainer`.
    """

    def __init__(self, spec: Specification | None = None) -> None:
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


class VerifyingContainer(Container):
    """
    A [`Container`](diy.Container) that verifies and caches the passed specification.

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

    def __init__(self, spec: Specification) -> None:
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
