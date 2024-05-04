from collections.abc import Callable
from inspect import Parameter, Signature, signature
from types import UnionType
from typing import Annotated, Any, get_origin

from diy.errors import (
    InvalidConstructorKeywordArgumentError,
    MissingConstructorKeywordArgumentError,
    MissingReturnTypeAnnotationError,
)


def is_typelike(subject: object) -> bool:
    if isinstance(subject, type):
        return True

    if isinstance(subject, UnionType):
        return True

    return get_origin(subject) is Annotated


def assert_is_typelike(subject: object) -> None:
    if not is_typelike(subject):
        message = "return type should be a type!"
        raise TypeError(message)


def assert_annotates_return_type[R](builder: Callable[..., R]) -> type[R]:
    abstract = signature(builder, eval_str=True).return_annotation
    if abstract is Signature.empty:
        raise MissingReturnTypeAnnotationError

    assert_is_typelike(abstract)

    return abstract


def assert_parameter_annotation_matches(
    abstract: type[Any], parameter: Parameter, builder_returns: type[Any]
) -> None:
    accepts = parameter.annotation
    if accepts is Parameter.empty:
        # TODO: We could add a strict mode here and throw, if the
        return

    # For unions we check if the builder returns a proper subset of the
    # parameter types. That is, all types returned from the builder must also
    # be accepted by the parameter.
    if isinstance(accepts, UnionType):
        accepted_members = set(accepts.__args__)
        returned: set[type] = (
            set(builder_returns.__args__)
            if isinstance(builder_returns, UnionType)
            else {builder_returns}
        )
        not_accepted = returned.difference(accepted_members)

        if len(not_accepted) > 0:
            raise InvalidConstructorKeywordArgumentError(
                abstract, parameter.name, builder_returns, accepts
            )
        return

    if not isinstance(builder_returns, accepts):
        raise InvalidConstructorKeywordArgumentError(
            abstract, parameter.name, builder_returns, accepts
        )


def assert_constructor_has_parameter(abstract: type[Any], name: str) -> Parameter:
    sig = signature(abstract.__init__, eval_str=True)
    parameter = sig.parameters.get(name)
    if parameter is None:
        raise MissingConstructorKeywordArgumentError(abstract, name)
    return parameter
