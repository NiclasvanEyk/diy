import pytest

from diy.errors import (
    MissingConstructorKeywordArgumentError,
    MissingReturnTypeAnnotationError,
)
from diy.specification import Specification


class Greeter:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


def test_raises_exception_when_decorating_builder_functions_without_type_annotaions() -> (
    None
):
    spec = Specification()

    with pytest.raises(MissingReturnTypeAnnotationError):

        @spec.decorate
        def greeter():  # noqa: ANN202
            return Greeter("Example")


def test_raises_exception_when_registering_partial_for_nonexisting_parameter() -> None:
    spec = Specification()

    with pytest.raises(MissingConstructorKeywordArgumentError):

        @spec.decorate(Greeter, "none_existent")
        def build_greeter() -> str:
            return ""
