from typing import Any


class DiyException(Exception):
    pass


class UninstanciableTypeError(DiyException):
    abstract: type[Any]

    def __init__(self, abstract: type[Any]) -> None:
        message = f"Can't instantiate type '{abstract.__qualname__}', since it's __init__ method does not accept 'self' as its first argument!"
        super().__init__(message)
        self.abstract = abstract


class UnresolvableDependencyError(DiyException):
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

    pass
