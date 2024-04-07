from typing import Callable, Protocol


class Container(Protocol):
    """
    Knows how to create objects.
    """

    def resolve[T](self, abstract: type[T]) -> T:
        """
        Instantiates an object of the given abstract type.

        This is **the** central method of our container.
        """

    def call[R](self, function: Callable[..., R]) -> R:
        """
        Runs the callable (most likely a function) by resolving its parameters
        from this container.
        """
