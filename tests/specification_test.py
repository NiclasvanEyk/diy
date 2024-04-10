import pytest

from diy.errors import MissingReturnTypeAnnotationError
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

        @spec.builders.decorate
        def greeter():  # noqa: ANN202
            return Greeter("Example")
