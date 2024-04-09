import pytest

from diy.errors import MissingReturnTypeAnnotationError
from diy.specification import Specification


class Greeter:
    def __init__(self, name: str) -> None:
        self.name = name


def test_can_register_via_add_and_receive_via_get() -> None:
    spec = Specification()
    spec.add(Greeter, lambda: Greeter("Example"))

    builder = spec.get(Greeter)
    assert builder is not None

    instance = builder()
    assert instance.name == "Example"


def test_can_register_via_decorator_and_receive_via_get() -> None:
    spec = Specification()

    @spec.builder
    def greeter() -> Greeter:
        return Greeter("Example")

    builder = spec.get(Greeter)
    assert builder is not None

    instance = builder()
    assert instance.name == "Example"


def test_raises_exception_when_decorating_builder_functions_without_type_annotaions() -> (
    None
):
    spec = Specification()

    with pytest.raises(MissingReturnTypeAnnotationError):

        @spec.builder
        def greeter():
            return Greeter("Example")
