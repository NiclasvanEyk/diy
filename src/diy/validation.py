from typing import Any


def validate(additional: list[type[Any]] = list) -> None:
    """
    Useful in tests to check if all types registered into the container.

    Accepts an additional list of types that should be built without any
    problems.
    """
