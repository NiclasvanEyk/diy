from abc import abstractmethod
from collections.abc import Callable
from typing import Protocol, runtime_checkable


@runtime_checkable
class ContainerProtocol(Protocol):
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

    @abstractmethod
    def call[R](self, function: Callable[..., R]) -> R:
        """
        Calls the given function after resolving all required parameters from
        the container.
        """


__all__ = ["ContainerProtocol"]
