from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

type ResolutionChainEntry = ResolutionChainNode | ResolutionChain


class ResolvedThrough(StrEnum):
    BUILDER = "builder"
    PARTIAL = "partial"
    INFERENCE = "inference"
    DEFAULT = "default"


@dataclass
class ResolutionChainNode[T]:
    name: str
    """The name of the parameter."""

    depth: int

    type: type[T] | None = field(default=None)
    """The type of the parameter."""

    resolved_through: ResolvedThrough | None = field(default=None)

    children: list[ResolutionChainNode[Any]] = field(default_factory=list)
    """
    All entries that need to be resolved to construct the type of this
    parameter.
    """


@dataclass
class ResolutionChain:
    """
    Keeps track of which types depend on what other types to be instantiaded
    while resolving them out of the container.

    This helps with error messages, e.g. the following diagram

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
    is represented by the entries in the `children` list.
    """

    requestor: Callable[..., Any] | type[Any]

    depth: int = -1
    """
    What is trying to be resolved. Either a type or a function that we resolve
    the arguments for.
    """

    resolved_through: ResolvedThrough | None = field(default=None)

    children: list[ResolutionChainNode[Any]] = field(default_factory=list)
    """
    All entries that need to be resolved to construct the type of this
    parameter.
    """
