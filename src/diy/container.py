from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from inspect import FullArgSpec, Parameter, getfullargspec, signature
from typing import Any, Protocol, override

from diy.errors import (
    MissingConstructorKeywordTypeAnnotationError,
    UninstanciableTypeError,
    UnresolvableDependencyError,
    UnsupportedParameterTypeError,
)
from diy.specification import Specification


class Container(Protocol):
    # TODO: Write documentation

    @abstractmethod
    def resolve[T](self, abstract: type[T]) -> T:
        pass

    @abstractmethod
    def call[R](self, function: Callable[..., R]) -> R:
        pass


class RuntimeContainer(Container):
    """
    A :class:`Container` that reflects dependencies at runtime.
    """

    spec: Specification

    def __init__(self, spec: Specification | None = None) -> None:
        super().__init__()
        self.spec = spec or Specification()

    @override
    def resolve[T](self, abstract: type[T]) -> T:
        # Maybe we already know how to build this
        builder = self.spec.builders.get(abstract)
        if builder is not None:
            return builder()

        # if not first check if it even can be built
        assert_is_instantiable(abstract)

        # if yes, try to resolve it based on the knowledge we have
        [args, kwargs] = self.resolve_args(abstract.__init__)
        return abstract(*args, **kwargs)

    def resolve_args(
        self, subject: Callable[..., Any]
    ) -> tuple[list[Any], dict[str, Any]]:
        spec = signature(subject)
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        for name, parameter in spec.parameters.items():
            # TODO: This can definitely be done better
            if name == "self" or name[0:1] == "*" or name[0:2] == "**":
                continue

            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                # TODO: Maybe introduce a way of supplying these?
                #       We skip them for now, since the empty constructor
                #       has these at the end.
                continue

            if parameter.kind not in [
                Parameter.KEYWORD_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            ]:
                # HINT: Take a look at Signature.apply_defaults for supporting
                #       positional argument defaults
                # TODO: Support other cases
                raise UnsupportedParameterTypeError

            if parameter.default is not Parameter.empty:
                continue  # We will just use the default from python

            abstract = parameter.annotation
            if abstract is Parameter.empty:
                raise MissingConstructorKeywordTypeAnnotationError(abstract, name)

            builder = self.spec.builders.get(abstract)
            if builder is None:
                raise UnresolvableDependencyError(
                    abstract, self.spec.builders.known_types()
                )

            kwargs[name] = builder()

        return (args, kwargs)

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        [args, kwargs] = self.resolve_args(function)
        return function(*args, **kwargs)


def requires_arguments(spec: FullArgSpec) -> bool:
    if len(spec.args) == 0:
        return False

    return not (len(spec.args) == 1 and spec.args == ["self"])


def assert_is_instantiable(abstract: type[Any]) -> None:
    # TODO: Maybe we can also use `signature` here
    spec = getfullargspec(abstract.__init__)
    if len(spec.args) <= 0:
        raise UninstanciableTypeError(abstract)

    if spec.args[0] != "self":
        raise UninstanciableTypeError(abstract)
