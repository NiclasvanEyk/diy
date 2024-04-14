from diy.container import RuntimeContainer


class Innermost:
    pass


class Inner:
    def __init__(self, innermost: Innermost) -> None:
        pass


class Outer:
    def __init__(self, inner: Inner) -> None:
        pass


def test_it_can_resolve_nested_types() -> None:
    instance = RuntimeContainer().resolve(Outer)
    assert isinstance(instance, Outer)
