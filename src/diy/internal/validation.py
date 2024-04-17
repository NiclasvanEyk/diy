from typing import Annotated, get_origin


def is_typelike(subject: object) -> bool:
    if isinstance(subject, type):
        return True

    return get_origin(subject) is Annotated


def assert_is_typelike(subject: object) -> None:
    if not is_typelike(subject):
        message = "return type should be a type!"
        raise TypeError(message)
