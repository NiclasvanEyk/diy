from __future__ import annotations

from inspect import Signature, signature
from typing import Any, Callable

from diy.errors import MissingReturnTypeAnnotationError


class Specification:
    """
    Registers functions that construct certain types.
    Intended to be used by a :class:`diy.Container`.

    >>> from diy import Specification
    ...
    >>> class Greeter:
    ...   def __init__(self, name: str):
    ...     self.name = name
    ...
    ...   def greet(self):
    ...     print(f"Hello {self.name}!")
    ...
    >>> spec = Specification()
    >>> spec.add(Greeter, lambda: Greeter("Ella"))
    ...
    >>> builder = spec.get(Greeter)
    >>> instance = builder()
    >>> instance.greet()
    Hello Ella!
    """

    builders: dict[type[Any], Callable[..., Any]]

    def __init__(self) -> None:
        self.builders = {}

    def add[T](self, abstract: type[T], builder: Callable[[], T]) -> None:
        """
        Imperatively register a builder function for the abstract type.

        >>> from diy import Specification
        ...
        >>> class Greeter:
        ...   def __init__(self, name: str):
        ...     self.name = name
        ...
        ...   def greet(self):
        ...     print(f"Hello {self.name}!")
        ...
        >>> spec = Specification()
        >>> spec.add(Greeter, lambda: Greeter("Ella"))
        ...
        >>> builder = spec.get(Greeter)
        >>> instance = builder()
        >>> instance.greet()
        Hello Ella!
        """
        self.builders[abstract] = builder

    def magic[T](self, builder: Callable[[], T]) -> None:
        """TODO: Find a better name for all of these."""

    def get[T](self, abstract: type[T]) -> Callable[[], T] | None:
        """
        Retrieve the builder function for the abstract type.

        >>> from diy import Specification
        ...
        >>> class Greeter:
        ...   def __init__(self, name: str):
        ...     self.name = name
        ...
        ...   def greet(self):
        ...     print(f"Hello {self.name}!")
        ...
        >>> spec = Specification()
        >>> spec.add(Greeter, lambda: Greeter("Ella"))
        ...
        >>> builder = spec.get(Greeter)
        >>> instance = builder()
        >>> instance.greet()
        Hello Ella!
        """
        if abstract in self.builders:
            return self.builders[abstract]
        return None

    def builder[T](self, builder: Callable[..., T]):
        """
        Mark an existing function as a builder for an abstract type by
        decorating it.

        >>> from diy import Specification
        ...
        >>> class Greeter:
        ...   def __init__(self, name: str):
        ...     self.name = name
        ...
        ...   def greet(self):
        ...     print(f"Hello {self.name}!")
        ...
        >>> spec = Specification()
        ...
        >>> @spec.builder
        ... def build_greeter() -> Greeter:
        ...   return Greeter("Ella")
        ...
        >>> builder = spec.get(Greeter)
        >>> instance = builder()
        >>> instance.greet()
        Hello Ella!
        """

        abstract = signature(builder).return_annotation
        if abstract is Signature.empty:
            raise MissingReturnTypeAnnotationError()

        self.builders[abstract] = builder
        return builder
