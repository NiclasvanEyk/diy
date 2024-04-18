from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from diy.internal.validation import (
    assert_annotates_return_type,
    assert_constructor_has_parameter,
    assert_parameter_annotation_matches,
)


class Builders:
    """
    Add and retrieve builder functions for types."""

    _by_type: dict[type[Any], Callable[..., Any]]

    def __init__(self) -> None:
        super().__init__()
        self._by_type = {}

    def decorate[T](self, builder: Callable[..., T]) -> Callable[..., T]:
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
        >>> @spec.builders.decorate
        ... def build_greeter() -> Greeter:
        ...   return Greeter("Ella")
        ...
        >>> builder = spec.builders.get(Greeter)
        >>> instance = builder()
        >>> instance.greet()
        Hello Ella!
        """
        abstract = assert_annotates_return_type(builder)
        self._by_type[abstract] = builder
        return builder

    def get[T](self, abstract: type[T]) -> Callable[..., T] | None:
        """
        Retrieve a builder function for the given abstract type.

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
        >>> @spec.builders.decorate
        ... def build_greeter() -> Greeter:
        ...   return Greeter("Ella")
        ...
        >>> builder = spec.builders.get(Greeter)
        >>> instance = builder()
        >>> instance.greet()
        Hello Ella!
        """
        return self._by_type.get(abstract)


class Partials:
    """
    Add and retrieve builder functions for constructor paramters of types.
    """

    # TODO: The doctests don't represent realistic use cases.
    #       Maybe they should utilize a container?

    _by_type: defaultdict[type[Any], dict[str, Callable[..., Any]]]

    def __init__(self) -> None:
        super().__init__()
        self._by_type = defaultdict(dict)

    def decorate[P](self, abstract: type[Any], name: str) -> Callable[..., Any]:
        """
        Add the given partial function for the given parameter of the given
        abstract type by decorating it.

        >>> from diy import Specification
        ...
        >>> class Simple: pass
        ...
        >>> class Greeter:
        ...   def __init__(self, name: str, simple: Simple):
        ...     self.name = name
        ...     self.simple = simple
        ...
        ...   def greet(self):
        ...     print(f"Hello {self.name}!")
        ...
        >>> spec = Specification()
        ...
        >>> @spec.partials.decorate(Greeter, "name")
        ... def build_greeter_name() -> str:
        ...   return "Ella"
        ...
        >>> builder = spec.partials.get(Greeter, "name")
        >>> instance = builder()
        >>> print(builder())
        Ella
        """

        def decorator(builder: Callable[..., P]) -> Callable[..., Callable[..., P]]:
            builder_returns = assert_annotates_return_type(builder)
            parameter = assert_constructor_has_parameter(abstract, name)
            assert_parameter_annotation_matches(abstract, parameter, builder_returns)
            self._by_type[abstract][name] = builder

            def inner() -> Callable[..., P]:
                return builder  # pragma: no cover

            return inner

        return decorator

    def get(self, abstract: type[Any], name: str) -> Callable[..., Any] | None:
        """
        Retrieve a bound partial builder function.
        """
        return self._by_type[abstract].get(name)


class Specification:
    """
    Registers functions that construct certain types.
    Intended to be used by a :class:`diy.Container`.
    """

    builders: Builders
    """Add and retrieve builder functions for types."""

    partials: Partials
    """Add and retrieve builder functions for constructor paramters of types."""

    def __init__(self) -> None:
        super().__init__()
        self.builders = Builders()
        self.partials = Partials()

    def types(self) -> set[type[Any]]:
        types = set(self.builders._by_type.keys())
        types.update(self.partials._by_type.keys())
        return types
