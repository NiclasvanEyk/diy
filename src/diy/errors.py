from __future__ import annotations

from typing import Any

from diy.internal.display import print_resolution_plan, qualified_name
from diy.plan import (
    CallableResolutionPlan,
    InferenceBasedResolutionPlan,
    InferenceParameterResolutionPlan,
)


class DiyError(Exception):
    pass


class UninstanciableTypeError(DiyError):
    abstract: type[Any]

    def __init__(self, abstract: type[Any]) -> None:
        message = f"Can't instantiate type '{qualified_name(abstract)}', since it's __init__ method does not accept 'self' as its first argument!"
        super().__init__(message)
        self.abstract = abstract


class UnsupportedParameterTypeError(DiyError):
    pass


class FailedToInferDependencyError(DiyError):
    def __init__(
        self,
        plan: InferenceBasedResolutionPlan[Any] | CallableResolutionPlan[..., Any],
        parent: InferenceParameterResolutionPlan[Any],
    ) -> None:
        # TODO: We actually need parent.parent.type here. But that is not available (yet)
        message = (
            f"Failed to infer parameter {parent.name} for {qualified_name(parent.type)}"
        )
        super().__init__(message)
        printed_plan = print_resolution_plan(plan)
        # TODO: The plan is somewhat helpful here, but we should hint to the
        #       developer at which point of the plan this exception originates
        self.add_note(f"\n{printed_plan}")


class UnresolvableDependencyError(DiyError):
    """
    Gets thrown when a :class:`Container` tries to instantiate a type, but not
    all requirements can be automatically resolved.

    ## Example

    Imagine we want to issue HTTP requests to an external API. As a security
    measure, that API requires us to send a secret token in a header:
    ```python
    class ApiClient:
        def __init__(self, auth_token: str):
            self.auth_token = auth_token

        def request_things():
            url = "http://my-api.com/things"
            return requests.get(url, headers={token: self.auth_token}).json()
    ```

    if we don't tell our container what to use.
    """

    def __init__(self, abstract: type[Any], known: list[type[Any]] | list[str]) -> None:
        super().__init__(
            f"Failed to resolve an instance of '{qualified_name(abstract)}'"
        )
        self.abstract = abstract
        enumeration = "\n".join([f"- {qualified_name(x)}" for x in known])
        note = f"Known types are:\n{enumeration}"
        self.add_note(note)


class MissingReturnTypeAnnotationError(DiyError):
    """
    Gets thrown when trying to register a builder function for a
    :class:`Specification`, but the function is missing a return type
    annotation.

    In this case, we can not identify which type the function tries to build,
    without leveraging extensive mechanisms such as parsing its body
    on-the-fly. This would be be bad for performance and also feels a bit too
    much.
    """

    def __init__(self) -> None:
        message = "A builder function requires a return type annotation."
        super().__init__(message)
        self.add_note(
            """If you e.g. define a function
    @spec.builder
    def my_builder():
       return MyType()

you can add a return type like this:

    @spec.builder
    def my_builder() -> MyType:
       return MyType()

diy can't infer this without extensive measures, so you as a user are required
to provide proper annotations.
"""
        )


class MissingConstructorKeywordArgumentError(DiyError):
    def __init__(self, abstract: type[Any], name: str) -> None:
        message = f"Tried to register partial builder for parameter '{qualified_name(abstract)}'::'{name}' of type , but its __init__ function does not have a keyword argument named '{name}'!"
        super().__init__(message)


class MissingConstructorKeywordTypeAnnotationError(DiyError):
    def __init__(self, abstract: type[Any], name: str) -> None:
        message = f"Tried to build an instance of '{qualified_name(abstract)}', but the '{name}' parameter is missing a type annotation."
        super().__init__(message)
        self.add_note(
            "Either register an explicit builder function via diy.Specification.builders.add, or provide a type annotation for a type that is already known or can be automatically resolved."
        )


class InvalidConstructorKeywordArgumentError(DiyError):
    def __init__(
        self,
        abstract: type[Any],
        name: str,
        provided: type[Any] | str,
        required: type[Any],
    ) -> None:
        target = f"{qualified_name(abstract)}::{name}"
        message = f"Tried to register partial builder for {target}. The builder returns '{qualified_name(provided)}', but {target} accepts '{qualified_name(required)}'!"
        super().__init__(message)
