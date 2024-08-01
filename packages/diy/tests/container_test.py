from __future__ import annotations

from typing import Annotated, Any

import pytest

from diy import Container, Specification
from diy._internal.display import print_resolution_plan
from diy.errors import (
    FailedToInferDependencyError,
    MissingConstructorKeywordTypeAnnotationError,
    UninstanciableTypeError,
)


class ConstructurWithoutSelf:
    def __init__() -> None:  # type: ignore[reportSelfClsParameterName]
        pass


class ConstructorWithWeirdArgs:
    def __init__(foo) -> None:  # noqa: N805 # type: ignore[reportSelfClsParameterName]
        super().__init__()


def test_container_reports_uninstantiable_types() -> None:
    container = Container()

    with pytest.raises(UninstanciableTypeError):
        container.resolve(ConstructurWithoutSelf)

    with pytest.raises(UninstanciableTypeError):
        container.resolve(ConstructorWithWeirdArgs)


class NoConstructor:
    pass


class ConstructorWithOnlySelf:
    def __init__(self) -> None:
        super().__init__()
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
    container = Container()
    instance = container.resolve(abstract)
    assert isinstance(instance, abstract)


def test_container_can_instantiate_constructors_that_only_require_default_arguments() -> (
    None
):
    class ConstructorWithOneDefaultArgument:
        def __init__(self, name: str = "default name") -> None:
            super().__init__()
            self.name = name

    container = Container()
    instance = container.resolve(ConstructorWithOneDefaultArgument)
    assert isinstance(instance, ConstructorWithOneDefaultArgument)


def test_container_actually_resolves_the_default_arguments() -> None:
    container = Container()

    sentinel = object()

    def my_function(my_argument: object = sentinel) -> object:
        return my_argument

    result = container.call(my_function)
    assert result == sentinel


class ApiClient:
    def __init__(self, token: str) -> None:
        super().__init__()
        self.base = token


def test_container_can_instantiate_kwargs_only_constructors() -> None:
    spec = Specification()

    @spec.add
    def build_api_client() -> ApiClient:
        return ApiClient("test")

    container = Container(spec)
    instance = container.resolve(ApiClient)
    assert isinstance(instance, ApiClient)


class ImplicitlyResolvesApiClient:
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api


def test_container_can_implicitly_resolve_argument_that_are_contained_in_the_spec() -> (
    None
):
    container = Container()

    @container.add
    def build_api_client() -> ApiClient:
        return ApiClient("test")

    instance = container.resolve(ImplicitlyResolvesApiClient)
    assert isinstance(instance, ImplicitlyResolvesApiClient)


class Greeter:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


def test_it_throws_when_type_cannot_be_resolved() -> None:
    container = Container()
    with pytest.raises(FailedToInferDependencyError):
        container.resolve(Greeter)


def test_it_can_inject_itself_via_protocols() -> None:
    spec = Specification()
    container = Container(spec)

    # TODO: Not sure if adding to the spec _after_ handing it into a container
    #       should have an effect on the container. Could be prevented by deep-
    #       copying the spec in the container constructor, but for this
    #       specific use-case, it is convenient. Though I guess it feelds more
    #       proper to support injecting builder arguments from the container
    #       instead.
    @spec.add
    def inject_self() -> Container:
        return container

    instance = container.resolve(Container)
    assert instance == container


class UnannotatedGreeter:
    def __init__(self, name) -> None:  # noqa: ANN001
        super().__init__()
        self.name = name


def test_raises_exception_when_registering_partial_for_unannotated_parameter() -> None:
    spec = Specification()
    container = Container(spec)

    with pytest.raises(MissingConstructorKeywordTypeAnnotationError):
        container.resolve(UnannotatedGreeter)


def test_it_can_resolve_when_all_args_have_registered_partials() -> None:
    spec = Specification()

    @spec.add(Greeter, "name")
    def build_greeter_name() -> str:
        return "foo"

    container = Container(spec)
    greeter = container.resolve(Greeter)
    assert isinstance(greeter, Greeter)


def test_it_prefers_partial_builders_to_default_args() -> None:
    class DefaultGreeter:
        def __init__(self, name: str = "default") -> None:
            self.name = name

    spec = Specification()

    @spec.add(DefaultGreeter, "name")
    def build_default_greeter() -> str:
        return "override"

    container = Container(spec)
    greeter = container.resolve(DefaultGreeter)

    assert isinstance(greeter, DefaultGreeter)
    assert greeter.name == "override"


class CloudBucket:
    def __init__(self, path: str) -> None:
        self.path = path


ProfilePicturesBucket = Annotated[CloudBucket, "profile-pictures"]
OpenGraphImagesBucket = Annotated[CloudBucket, "og-images"]


def test_it_can_build_types_based_on_annotations() -> None:
    class UserService:
        def __init__(self, bucket: ProfilePicturesBucket) -> None:
            super().__init__()
            self.bucket = bucket

    class OgImageGenerator:
        def __init__(self, bucket: OpenGraphImagesBucket) -> None:
            super().__init__()
            self.bucket = bucket

    spec = Specification()

    @spec.add
    def build_pfp_bucket() -> ProfilePicturesBucket:
        return CloudBucket("s3:profile_pictures")

    @spec.add
    def build_og_bucket() -> OpenGraphImagesBucket:
        return CloudBucket("do:og-images")

    container = Container(spec)

    user_service = container.resolve(UserService)
    assert user_service.bucket.path == "s3:profile_pictures"

    generator = container.resolve(OgImageGenerator)
    assert generator.bucket.path == "do:og-images"


class ConfigStore:
    def get(self, key: str) -> str:
        return "test"


def test_it_supplies_builders_with_args_from_the_container() -> None:
    spec = Specification()

    @spec.add
    def build_api_client(config: ConfigStore) -> ApiClient:
        return ApiClient(config.get("token"))

    container = Container(spec)
    instance = container.resolve(ApiClient)

    assert instance.base == "test"


class ConsumesApiClient:
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api


def test_it_supplies_nested_builders_with_args_from_the_container() -> None:
    container = Container()

    @container.add
    def build_api_client(config: ConfigStore) -> ApiClient:
        return ApiClient(config.get("api_base"))

    instance = container.resolve(ConsumesApiClient)

    assert instance.api.base == "test"
