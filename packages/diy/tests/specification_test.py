import pytest

from diy import Container
from diy.errors import (
    MissingConstructorKeywordArgumentError,
    MissingReturnTypeAnnotationError,
)


class Greeter:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


def test_raises_exception_when_decorating_builder_functions_without_type_annotaions() -> (
    None
):
    container = Container()

    with pytest.raises(MissingReturnTypeAnnotationError):

        @container.add
        def greeter():  # noqa: ANN202
            return Greeter("Example")


def test_raises_exception_when_registering_partial_for_nonexisting_parameter() -> None:
    container = Container()

    with pytest.raises(MissingConstructorKeywordArgumentError):

        @container.add(Greeter, "none_existent")
        def build_greeter() -> str:
            return ""
