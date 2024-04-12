from __future__ import annotations

from typing import Annotated, Any

import pytest

from diy import Container, RuntimeContainer, Specification
from diy.errors import (
    MissingConstructorKeywordTypeAnnotationError,
    UninstanciableTypeError,
    UnresolvableDependencyError,
)


class ConstructurWithoutSelf:
    def __init__() -> None:  # type: ignore[reportSelfClsParameterName]
        pass


class ConstructorWithWeirdArgs:
    def __init__(foo) -> None:  # noqa: N805
        pass


def test_container_reports_uninstantiable_types() -> None:
    container = RuntimeContainer()

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
    container = RuntimeContainer()
    instance = container.resolve(abstract)
    assert isinstance(instance, abstract)


def test_container_can_instantiate_constructors_that_only_require_default_arguments() -> (
    None
):
    class ConstructorWithOneDefaultArgument:
        def __init__(self, name: str = "default name") -> None:
            super().__init__()
            self.name = name

    container = RuntimeContainer()
    instance = container.resolve(ConstructorWithOneDefaultArgument)
    assert isinstance(instance, ConstructorWithOneDefaultArgument)


def test_container_actually_resolves_the_default_arguments() -> None:
    container = RuntimeContainer()

    sentinel = object()

    def my_function(my_argument: object = sentinel) -> object:
        return my_argument

    result = container.call(my_function)
    assert result == sentinel


class ApiClient:
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token


def test_container_can_instantiate_kwargs_only_constructors() -> None:
    spec = Specification()
    spec.builders.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ApiClient)
    assert isinstance(instance, ApiClient)


class ImplicitlyResolvesApiClient:
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api


def test_container_can_implicitly_resolve_argument_that_are_contained_in_the_spec() -> (
    None
):
    spec = Specification()
    spec.builders.add(ApiClient, lambda: ApiClient("test"))

    container = RuntimeContainer(spec)
    instance = container.resolve(ImplicitlyResolvesApiClient)
    assert isinstance(instance, ImplicitlyResolvesApiClient)


class Greeter:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


def test_it_throws_when_type_cannot_be_resolved() -> None:
    spec = Specification()
    container = RuntimeContainer(spec)

    with pytest.raises(UnresolvableDependencyError):
        container.resolve(Greeter)


def test_it_can_inject_itself_via_protocols() -> None:
    spec = Specification()
    container = RuntimeContainer(spec)

    # TODO: Not sure if adding to the spec _after_ handing it into a container
    #       should have an effect on the container. Could be prevented by deep-
    #       copying the spec in the container constructor, but for this
    #       specific use-case, it is convenient. Though I guess it feelds more
    #       proper to support injecting builder arguments from the container
    #       instead.
    spec.builders.add(Container, lambda: container)

    instance = container.resolve(Container)
    assert instance == container


class UnannotatedGreeter:
    def __init__(self, name) -> None:  # noqa: ANN001
        super().__init__()
        self.name = name


def test_raises_exception_when_registering_partial_for_unannotated_parameter() -> None:
    spec = Specification()
    container = RuntimeContainer(spec)

    with pytest.raises(MissingConstructorKeywordTypeAnnotationError):
        container.resolve(UnannotatedGreeter)


def test_it_can_resolve_when_all_args_have_registered_partials() -> None:
    spec = Specification()
    spec.partials.add(Greeter, "name", str, lambda: "foo")

    container = RuntimeContainer(spec)
    greeter = container.resolve(Greeter)
    assert isinstance(greeter, Greeter)


def test_it_prefers_partial_builders_to_default_args() -> None:
    class DefaultGreeter:
        def __init__(self, name: str = "default") -> None:
            self.name = name

    spec = Specification()
    spec.partials.add(DefaultGreeter, "name", str, lambda: "override")
    container = RuntimeContainer(spec)

    greeter = container.resolve(DefaultGreeter)

    assert isinstance(greeter, DefaultGreeter)
    assert greeter.name == "override"


def test_it_can_build_types_based_on_annotations() -> None:
    class CloudBucket:
        def __init__(self, path: string) -> None:
            self.path = path

    ProfilePicturesBucket = Annotated[CloudBucket, "profile-pictures"]
    OpenGraphImagesBucket = Annotated[CloudBucket, "og-images"]

    class UserService:
        def __init__(self, bucket: ProfilePicturesBucket) -> None:
            self.bucket = bucket

    class OgImageGenerator:
        def __init__(self, bucket: OpenGraphImagesBucket) -> None:
            self.bucket = bucket

    spec = Specification()
    spec.builders.add(ProfilePicturesBucket, lambda: CloudBucket("s3:profile_pictures"))
    spec.builders.add(OgImageGenerator, lambda: CloudBucket("do:og-images"))

    container = RuntimeContainer(spec)

    user_service = container.resolve(UserService)
    assert user_service.bucket.path == "s3:profile_pictures"

    generator = container.resolve(OgImageGenerator)
    assert generator.bucket.path == "do:og-images"
