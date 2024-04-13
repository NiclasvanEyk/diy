from collections.abc import Callable
from inspect import Parameter, Signature, signature
from typing import Any


class PendingFunctionCall[**P, R]:
    """
    Preparation for calling a function with information from a
    :class:`Container`.
    """

    subject: Callable[P, R]
    """The underlying function to call"""

    parameters: dict[str, Any]
    """All parameters that should be forwarded to the underlying function"""

    signature: Signature
    """The signature of the underlying function"""

    def __init__(
        self, subject: Callable[P, R], parameters: dict[str, Any] | None = None
    ) -> None:
        super().__init__()
        self.subject = subject
        self.signature = signature(subject)
        self.parameters = parameters if parameters is not None else {}

    def bind(self, parameters: dict[str, Any]) -> None:
        """
        Binds parameters to the function call.
        """
        for name, value in parameters.items():
            target = self.signature.parameters.get(name)
            if target is None:
                continue  # TODO:

            expected_type = target.annotation
            if expected_type is None:
                # Nothing we can really do here
                continue

            if not isinstance(value, expected_type):
                received_type = type(value)
                message = (
                    f"Parameter {name} expects {expected_type}, got {received_type}"
                )
                raise TypeError(message)

        self.parameters.update(parameters)

    def can_be_called(self) -> bool:
        """
        Whether all required arguments have been bound and the function can
        safely be called without knowingly running into a error due to missing
        arguments.
        """
        return len(self.missing()) == 0

    def missing(self) -> set[str]:
        """
        The parameter names that still need to be bound in order to call the
        function.
        """
        missing: set[str] = set()
        for parameter in self.signature.parameters.values():
            if parameter.default is not Parameter.empty:
                continue

            if parameter.name not in self.parameters:
                missing.add(parameter.name)

        return missing

    def call(self) -> R:
        """
        Call the underlying function with what is bound to this object.
        Does not accept any parameters on purpose, as they should be bound to
        this object by calling `bind`.
        """

        # Start with what is bound into this instance
        args = []  # TODO: Support non-keyword arguments
        kwargs = self.parameters

        return self.subject(*args, **kwargs)  # type: ignore [reportCallIssue]
