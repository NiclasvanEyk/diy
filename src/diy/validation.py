from typing import Any


def validate(additional: list[type[Any]] | None) -> None:
    """
    Useful in tests to check if all types registered into the container.

    Accepts an additional list of types that should be built without any
    problems.
    """
    if additional is None:
        additional = []

    raise NotImplementedError
