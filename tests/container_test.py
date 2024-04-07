from typing import Any
from diy.exception import UninstanciableTypeError
from diy.container import RuntimeContainer, Specification
import pytest


class ConstructurWithoutSelf:
    def __init__():
        pass


def test_container_reports_uninstantiable_types():
    container = RuntimeContainer()

    with pytest.raises(UninstanciableTypeError):
        container.resolve(ConstructurWithoutSelf)


class NoConstructor:
    pass


class ConstructorWithOnlySelf:
    def __init__(self):
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
):
    container = RuntimeContainer()
    instance = container.resolve(abstract)
    assert isinstance(instance, abstract)


def test_container_can_instantiate_constructors_that_only_require_default_arguments():
    class ConstructorWithOneDefaultArgument:
        def __init__(self, name: str = "default name"):
            self.name = name

    container = RuntimeContainer()
    instance = container.resolve(ConstructorWithOneDefaultArgument)
    assert isinstance(instance, ConstructorWithOneDefaultArgument)


def test_container_actually_resolves_the_default_arguments():
    container = RuntimeContainer()

    sentinel = object()

    def my_function(my_argument=sentinel):
        return my_argument

    result = container.call(my_function)
    assert result == sentinel


class ApiClient:
    def __init__(self, token: str) -> None:
        self.token = token


def test_container_can_instantiate_kwargs_only_constructors():
    spec = Specification()
    spec.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ApiClient)
    assert isinstance(instance, ApiClient)


class ImplicitlyResolvesApiClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api


def test_container_can_implicitly_resolve_argument_that_are_contained_in_the_spec():
    spec = Specification()
    spec.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ImplicitlyResolvesApiClient)
    assert isinstance(instance, ImplicitlyResolvesApiClient)
