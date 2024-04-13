import pytest

from diy.invocation import PendingFunctionCall


def add(a: int, b: int) -> int:  # noqa: FURB118
    return a + b


def test_it_can_detect_if_all_args_are_bound() -> None:
    pending = PendingFunctionCall(add)
    assert pending.can_be_called() == False
    assert pending.missing() == {"a", "b"}

    pending.bind({"a": 2})
    assert pending.can_be_called() == False
    assert pending.missing() == {"b"}

    pending.bind({"b": 2})
    assert pending.can_be_called()


class Greeter:
    def greet(self, name: str) -> None:
        pass


def test_it_detects_that_self_does_not_need_to_be_bound_for_instances() -> None:
    instance = Greeter()
    pending = PendingFunctionCall(instance.greet)
    pending.bind({"name": "Ella"})

    assert pending.can_be_called()


def test_it_detects_that_self_needs_to_be_bound_when_passing_class_method() -> None:
    pending = PendingFunctionCall(Greeter.greet)
    pending.bind({"name": "Ella"})

    assert pending.can_be_called() == False


def test_it_detects_it_can_be_invoked_when_parameter_with_defaults_is_missing() -> None:
    def add_with_default_two(a: int, b: int = 2) -> int:
        return a + b

    pending = PendingFunctionCall(add_with_default_two)
    pending.bind({"a": 2})

    assert pending.can_be_called()


def test_it_calls_subject_with_bound_parameters() -> None:
    pending = PendingFunctionCall(add, {"a": 2, "b": 2})
    result = pending.call()

    assert result == 4


def test_it_detects_when_wrong_parameter_type_is_bound() -> None:
    pending = PendingFunctionCall(add)

    with pytest.raises(TypeError):
        pending.bind({"a": "definitely not an integer"})
