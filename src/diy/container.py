from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from inspect import Parameter, getfullargspec, signature
from typing import Any, Protocol, override

from diy.errors import (
    MissingConstructorKeywordTypeAnnotationError,
    UninstanciableTypeError,
    UnresolvableDependencyError,
    UnsupportedParameterTypeError,
)
from diy.resolution import (
    ResolutionChain,
    ResolutionChainEntry,
    ResolutionChainNode,
    ResolvedThrough,
)
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
    """

    spec: Specification

    def __init__(self, spec: Specification | None = None) -> None:
        super().__init__()
        self.spec = spec or Specification()

    @override
    def resolve[T](
        self,
        abstract: type[T],
        chain_parent: ResolutionChainEntry | None = None,
    ) -> T:
        root_chain = False
        if chain_parent is None:
            root_chain = True
            chain_parent = ResolutionChain(requestor=abstract)

        # Maybe we already know how to build this
        builder = self.spec.builders.get(abstract)
        if builder is not None:
            chain_parent.resolved_through = ResolvedThrough.BUILDER
            return builder()

        # if not first check if it even can be built
        assert_is_instantiable(abstract)

        # if yes, try to resolve it based on the knowledge we have
        [args, kwargs] = self.resolve_args(abstract.__init__, chain_parent)
        if root_chain:
            print(chain_parent)
        return abstract(*args, **kwargs)

    def resolve_args(
        self,
        subject: Callable[..., Any],
        chain_parent: ResolutionChainEntry | None = None,
    ) -> tuple[list[Any], dict[str, Any]]:
        spec = signature(subject)
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        if chain_parent is None:
            chain_parent = ResolutionChain(requestor=subject)

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

            chain_entry = ResolutionChainNode(name, chain_parent.depth + 1)
            chain_parent.children.append(chain_entry)

            if isinstance(chain_parent, ResolutionChainNode):
                parent_type = chain_parent.type
                if isinstance(parent_type, type):
                    partial_builder = self.spec.partials.get(parent_type, name)
                    if partial_builder is not None:
                        chain_entry.resolved_through = ResolvedThrough.PARTIAL
                        kwargs[name] = partial_builder()
                        continue

            if parameter.default is not Parameter.empty:
                chain_entry.resolved_through = ResolvedThrough.DEFAULT
                continue  # We will just use the default from python

            abstract = parameter.annotation
            if abstract is Parameter.empty:
                raise MissingConstructorKeywordTypeAnnotationError(abstract, name)

            if not isinstance(abstract, type):
                print(f"!!!ANNOTATION ({abstract}) WAS NOT AN INSTANCE OF TYPE!!!")
            else:
                chain_entry.type = abstract

            # TODO: This can't happen right now, but it might be better dx if
            #       we throw a different error when ALL args of a constructor
            #       cannot be resolved. Maybe we could also include the
            #       "resolver chain" in the error message, so users know WHY a
            #       type was resolved. That would also make this code path
            #       irrelevant.
            # TODO: Somewhere we need to use the resolution chains to realize
            #       the above. Maybe we need to use self.resolve here and
            #       recurse instead of using the builders?
            # TODO: Detect loops, maybe using the chain?

            chain_entry.resolved_through = ResolvedThrough.INFERENCE
            resolved = self.resolve(abstract, chain_parent)
            kwargs[name] = resolved

            # builder = self.spec.builders.get(abstract)
            # if builder is None:
            #     raise UnresolvableDependencyError(
            #         abstract, self.spec.builders.known_types()
            #     )
            # kwargs[name] = builder()
            # chain_entry.resolved_through = ResolvedThrough.BUILDER

        return (args, kwargs)

    @override
    def call[R](self, function: Callable[..., R]) -> R:
        [args, kwargs] = self.resolve_args(function)
        return function(*args, **kwargs)


def assert_is_instantiable(abstract: type[Any]) -> None:
    # TODO: Maybe we can also use `signature` here
    spec = getfullargspec(abstract.__init__)
    if len(spec.args) <= 0:
        raise UninstanciableTypeError(abstract)

    if spec.args[0] != "self":
        raise UninstanciableTypeError(abstract)
