from __future__ import annotations

from inspect import FullArgSpec, getfullargspec, signature, Parameter
from typing import Callable, override, Any

from diy import Container
from diy.exception import UninstanciableTypeError, UnresolvableDependencyError


def requires_arguments(spec: FullArgSpec) -> bool:
    if len(spec.args) == 0:
        return False

    if len(spec.args) == 1 and spec.args == ["self"]:
        return False

    return True


def can_be_instanciated(spec: FullArgSpec) -> bool:
    if len(spec.args) <= 0:
        return False

    return spec.args[0] == "self"


class Specification:
    """
    Registers functions that construct certain types.
    """

    builders: dict[type[Any], Callable[..., Any]] = {}

    def add[T](self, abstract: type[T], builder: Callable[[], T]) -> None:
        self.builders[abstract] = builder

    def get[T](self, abstract: type[T]) -> Callable[[], T] | None:
        if abstract in self.builders:
            return self.builders[abstract]
        return None


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
        constructor = abstract.__init__
        spec = getfullargspec(constructor)

        if not can_be_instanciated(spec):
            raise UninstanciableTypeError(abstract)

        builder = self.spec.get(abstract)
        if builder is not None:
            return builder()

        # Maybe we can simplify this to just resolve empty args and kwargs
        if not requires_arguments(spec):
            return abstract()

        [args, kwargs] = self.resolve_args(constructor)
        return abstract(*args, **kwargs)

    def resolve_args(
        self, subject: Callable[..., Any]
    ) -> tuple[list[Any], dict[str, Any]]:
        spec = signature(subject)
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        for name, parameter in spec.parameters.items():
            # TODO: This can definitely be done better
            if name == "self":
                continue

            if parameter.kind not in [
                Parameter.KEYWORD_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            ]:
                # TODO: Maybe introduce a more specific Exception
                raise UnresolvableDependencyError()

            if parameter.default is not Parameter.empty:
                continue  # We will just use the default from python

            abstract = parameter.annotation
            if abstract is Parameter.empty:
                # TODO: Maybe introduce a more specific Exception
                raise UnresolvableDependencyError()

            builder = self.spec.get(abstract)
            if builder is None:
                # TODO: Maybe introduce a more specific Exception
                raise UnresolvableDependencyError()

            kwargs[name] = builder()

        return (args, kwargs)

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        [args, kwargs] = self.resolve_args(function)
        return function(*args, **kwargs)
