from __future__ import annotations

from typing import Any


class DiyError(Exception):
    pass


class UninstanciableTypeError(DiyError):
    abstract: type[Any]

    def __init__(self, abstract: type[Any]) -> None:
        message = f"Can't instantiate type '{abstract.__qualname__}', since it's __init__ method does not accept 'self' as its first argument!"
        super().__init__(message)
        self.abstract = abstract


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


class MissingReturnTypeAnnotationError(DiyError):
    """
    Gets thrown when trying to register a builder function for a
    :class:`Specificaiton`, but the function is missing a return type
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
