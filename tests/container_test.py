from __future__ import annotations

from typing import Any

import pytest

from diy import Container, RuntimeContainer, Specification
from diy.errors import UninstanciableTypeError


class ConstructurWithoutSelf:
    def __init__() -> None:
        pass


def test_container_reports_uninstantiable_types() -> None:
    container = RuntimeContainer()

    with pytest.raises(UninstanciableTypeError):
        container.resolve(ConstructurWithoutSelf)


class NoConstructor:
    pass


class ConstructorWithOnlySelf:
    def __init__(self) -> None:
        self.something = "foo"


@pytest.mark.parametrize(
    "abstract",
    [
        NoConstructor,
        ConstructorWithOnlySelf,
    ],
)
def test_container_can_instantiate_constructors_that_require_no_arguments(
    abstract: type[Any],
) -> None:
    container = RuntimeContainer()
    instance = container.resolve(abstract)
    assert isinstance(instance, abstract)


def test_container_can_instantiate_constructors_that_only_require_default_arguments() -> (
    None
):
    class ConstructorWithOneDefaultArgument:
        def __init__(self, name: str = "default name") -> None:
            self.name = name

    container = RuntimeContainer()
    instance = container.resolve(ConstructorWithOneDefaultArgument)
    assert isinstance(instance, ConstructorWithOneDefaultArgument)


def test_container_actually_resolves_the_default_arguments() -> None:
    container = RuntimeContainer()

    sentinel = object()

    def my_function(my_argument=sentinel):
        return my_argument

    result = container.call(my_function)
    assert result == sentinel


class ApiClient:
    def __init__(self, token: str) -> None:
        self.token = token


def test_container_can_instantiate_kwargs_only_constructors() -> None:
    spec = Specification()
    spec.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ApiClient)
    assert isinstance(instance, ApiClient)


class ImplicitlyResolvesApiClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api


def test_container_can_implicitly_resolve_argument_that_are_contained_in_the_spec() -> (
    None
):
    spec = Specification()
    spec.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ImplicitlyResolvesApiClient)
    assert isinstance(instance, ImplicitlyResolvesApiClient)


def test_it_can_inject_itself_via_protocols() -> None:
    spec = Specification()
    container = RuntimeContainer(spec)

    # TODO: Not sure if adding to the spec _after_ handing it into a container
    #       should have an effect on the container. Could be prevented by deep-
    #       copying the spec in the container constructor, but for this
    #       specific use-case, it is convenient. Though I guess it feelds more
    #       proper to support injecting builder arguments from the container
    #       instead.
    spec.add(Container, lambda: container)

    instance = container.resolve(Container)
    assert instance == container
