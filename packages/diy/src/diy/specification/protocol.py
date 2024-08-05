from abc import abstractmethod
from collections.abc import Callable
from typing import Any, Protocol, overload, runtime_checkable


@runtime_checkable
class SpecificationProtocol(Protocol):
    """
    Registers functions that construct certain types or parameters.
    """

    @overload
    @abstractmethod
    def add[T](self, builder: Callable[..., T]) -> Callable[..., T]:
        """
        Mark an existing function as a builder for an abstract type.
        """

    @overload
    @abstractmethod
    def add[T](self, builder: type[T], name: str) -> Callable[..., T]:
        """
        Mark the function as a supplier for the named constructor parameter of
        the given type.
        """

    @overload
    @abstractmethod
    def add(self, builder: type[Any]) -> None:
        """
        Simply tell the container, that this type exists.

        This helps containers to verify that this type should be "buildable" in
        the future. This means that all its parameters should have known
        constructors.
        """

    @abstractmethod
    def add[T](
        self, builder: Callable[..., Any] | type[T], name: str | None = None
    ) -> Callable[..., Any] | None:
        pass

    @overload
    @abstractmethod
    def get[T](self, abstract: type[T]) -> Callable[..., T] | None:
        """
        Retrieve a builder function for a type.
        """

    @overload
    @abstractmethod
    def get(self, abstract: type[Any], name: str) -> Callable[..., Any] | None:
        """
        Retrieve a builder function for a constructor parameter.
        """

    @abstractmethod
    def get[T](
        self, abstract: type[T], name: str | None = None
    ) -> Callable[..., T] | None:
        pass

    # TODO: This might make sense. A simple implementation would just add a
    # builder function that takes one argument (the concrete type) and somehow
    # dynamically annotates the return-type (or otherwise binds it in the
    # container). Maybe an additional lookup dict would improve performance /
    # could be used for introspection purposes?
    # @abstractmethod
    # def bind[Abstract: (Protocol | ABC), Concrete](
    #     self, abstract: type[Abstract], concrete: type[Concrete]
    # ) -> None:
    #     pass

    @abstractmethod
    def types(self) -> set[type[Any]]:
        """
        TODO:
        """


__all__ = ["SpecificationProtocol"]
