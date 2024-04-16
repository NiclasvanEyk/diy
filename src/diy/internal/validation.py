from typing import Annotated, get_origin


def is_typelike(subject) -> bool:
    if not isinstance(subject, type):
        if not get_origin(subject) is Annotated:
            return False

    return True


def assert_is_typelike(subject) -> None:
    if not is_typelike(subject):
        assert False, "return type should be a type!"
