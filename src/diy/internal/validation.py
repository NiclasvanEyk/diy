from collections.abc import Callable
from inspect import Parameter, Signature, signature
from types import UnionType
from typing import Annotated, Any, get_origin

from diy.errors import (
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


def assert_constructor_has_parameter(abstract: type[Any], name: str) -> Parameter:
    sig = signature(abstract.__init__, eval_str=True)
    parameter = sig.parameters.get(name)
    if parameter is None:
        raise MissingConstructorKeywordArgumentError(abstract, name)
    return parameter
