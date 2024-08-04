from dataclasses import dataclass, field
from enum import StrEnum


class PlanKind(StrEnum):
    BUILDER = "builder"
    """The subject is a type, which is resolved by calling a function."""

    CALLABLE = "callable"
    """The subject is a function, that we want to resolve arguments for."""

    # TODO: What about callables that get their args from builder functions?
    #       As in "if callable xyz wants param 123, give this value"

    INFERENCE = "inference"
    """
    The subject is a type, that we infer by inspecting its constructor
    parameters and try to resolve them from the container.
    """


class ParameterPlanKind(StrEnum):
    BUILDER = "builder"
    INFERENCE = "inference"
    DEFAULT = "default"
    NO_ARGS_CONSTRUCTOR = "no-args-constructor"


@dataclass
class NamespacedType:
    namespace: str | None
    name: str


@dataclass
class PrintedPlan:
    kind: PlanKind
    subject: NamespacedType


@dataclass
class PrintedContainer:
    """
    The plans of a container for JSON serialization.

    The specific format might change, but you can rely on a top level 'version'
    key containing the version to check for compatibility.
    """

    version: int = 1
    plans: dict[str, PrintedPlan] = field(default_factory=dict)
