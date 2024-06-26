from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

type ParameterPlanList = list[ParameterResolutionPlan[..., Any]]


@dataclass
class ParameterResolutionPlanBase[T]:
    name: str
    """The name of the parameter."""

    depth: int
    """How deep is the resolution chain, where -1 is the requestor."""

    type: type[T]
    """The type of the parameter."""

    parent: ResolutionPlan[..., Any] | ParameterResolutionPlan[..., Any]
    """The parent plan that requested this one."""


@dataclass
class DefaultParameterResolutionPlan[T](ParameterResolutionPlanBase[T]):
    """
    A parameter that is resolved simply by using the default value.
    """


@dataclass
class NoArgsConstructorParameterResolutionPlan[T](ParameterResolutionPlanBase[T]):
    """
    A parameter that is resolved by simply constructing the constructor
    without any arguments.
    """

    def execute(self) -> T:
        return self.type()


@dataclass
class BuilderParameterResolutionPlan[**P, T](ParameterResolutionPlanBase[T]):
    """
    A parameter that is resolved by calling its builder.
    """

    builder: Callable[P, T]
    """The function that knows how to build the type."""

    args_plan: CallableResolutionPlan[P, T]
    """A plan for calling the function that knows how to build the type."""

    def execute(self) -> T:
        """Actually build the type"""
        return self.args_plan.execute()


@dataclass
class InferenceParameterResolutionPlan[T](ParameterResolutionPlanBase[T]):
    """
    A parameter that is resolved by recursively trying our best to resolve all
    parameter of its constructor.
    """

    parameters: ParameterPlanList = field(default_factory=list)
    """
    All entries that need to be resolved to construct the type of this
    parameter.
    """

    def execute(self) -> T:
        args = []
        kwargs = {}
        for plan in self.parameters:
            match plan:
                case DefaultParameterResolutionPlan():
                    pass

                case NoArgsConstructorParameterResolutionPlan():
                    kwargs[plan.name] = plan.execute()

                case BuilderParameterResolutionPlan():
                    kwargs[plan.name] = plan.execute()

                case InferenceParameterResolutionPlan():
                    kwargs[plan.name] = plan.execute()

        return self.type(*args, **kwargs)


type ParameterResolutionPlan[**P, T] = (
    BuilderParameterResolutionPlan[P, T]
    | InferenceParameterResolutionPlan[T]
    | DefaultParameterResolutionPlan[T]
    | NoArgsConstructorParameterResolutionPlan[T]
)


# =============================================================================


@dataclass
class InferenceBasedResolutionPlan[T]:
    """
    Keeps track of which types depend on what other types to be instantiaded
    while resolving them out of the container.

    This helps with error messages, e.g. the following diagram

    TODO: Adjust this to be a real one printed by us, maybe through a doctest
    ```
    UserService
    ├─ api: ApiClient
    │  └─ http: HttpClient ──▶ HttpClient
    ├─ mailer: Mailer
    │  ├─ transport: Transport ──▶ SMTPTransport
    │  │  └─ foo: Unknown
    │  └─ bar: Unknown
    └─ logger: Logger ──▶ RotatingFileLogger
    ```
    makes it easy to exactly understand what is needed by the UserService and
    what it received.

    The root entry in the diagram corresponds to this class, everything below
    is represented by the entries in the `parameters` dict.
    """

    type: type[T]
    """
    What is trying to be resolved. Either a type or a function that we resolve
    the arguments for.
    """

    parameters: ParameterPlanList = field(default_factory=list)
    """
    All entries that need to be resolved to construct the type of this
    parameter.
    """

    def execute(self) -> T:
        """
        Try to run the plan and return the expected result. This is either what
        the function returns, or an instance of the requested type.
        """
        args, kwargs = resolve_parameter_plans(self.parameters)
        return self.type(*args, **kwargs)


@dataclass
class BuilderBasedResolutionPlan[**P, T]:
    type: type[T]
    """
    What is trying to be resolved. Either a type or a function that we resolve
    the arguments for.
    """

    # TODO: If the builder gets its arguments resolved, we need to continue
    #       resolving them. But for now this might be to complex.
    builder: Callable[P, T]

    args_plan: CallableResolutionPlan[P, T]

    def execute(self) -> T:
        return self.args_plan.execute()


@dataclass
class CallableResolutionPlan[**P, T]:
    subject: Callable[P, T]
    """
    What is trying to be resolved. Either a type or a function that we resolve
    the arguments for.
    """

    parameters: ParameterPlanList = field(default_factory=list)

    def execute(self) -> T:
        args, kwargs = resolve_parameter_plans(self.parameters)
        return self.subject(*args, **kwargs)  # type: ignore


type ResolutionPlan[**P, T] = (
    CallableResolutionPlan[P, T]
    | BuilderBasedResolutionPlan[P, T]
    | InferenceBasedResolutionPlan[T]
)


def resolve_parameter_plans[T](
    parameters: ParameterPlanList,
) -> tuple[list[Any], dict[str, Any]]:
    args = []
    kwargs = {}
    for plan in parameters:
        match plan:
            case DefaultParameterResolutionPlan():
                pass
            case NoArgsConstructorParameterResolutionPlan():
                kwargs[plan.name] = plan.execute()
            case BuilderParameterResolutionPlan():
                kwargs[plan.name] = plan.execute()
            case InferenceParameterResolutionPlan():
                kwargs[plan.name] = plan.execute()

    return args, kwargs
