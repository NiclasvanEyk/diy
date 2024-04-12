from typing import Any


def qualified_name(abstract: str | type[Any]) -> str:
    if isinstance(abstract, str):
        return abstract
    return abstract.__qualname__
