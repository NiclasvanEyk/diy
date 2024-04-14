from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

from diy.resolution import ResolutionChain, ResolutionChainNode

type FQN = tuple[str | None, str]


def fully_qualify(abstract: type[Any] | Callable[..., Any]) -> FQN:
    name = abstract.__qualname__

    module = abstract.__module__
    if module == "builtins":
        module = None

    return (module, name)


def join_qualified_name(fqn: FQN) -> str:
    (module, name) = fqn
    return name if module is None else f"{module}.{name}"


def qualified_name(abstract: str | type[Any] | Callable[..., Any]) -> str:
    if isinstance(abstract, str):
        return abstract

    return join_qualified_name(fully_qualify(abstract))


@dataclass
class ResoltionChainNodePrintUnit:
    node: ResolutionChainNode
    is_last: bool

    @staticmethod
    def map(nodes: list[ResolutionChainNode]) -> list[ResoltionChainNodePrintUnit]:
        if len(nodes) == 0:
            return []

        mapped = [ResoltionChainNodePrintUnit(node, False) for node in nodes]
        mapped[-1].is_last = True
        return mapped


def bold(subject: str, ansi: bool) -> str:
    if not ansi:
        return subject
    return f"\033[1m{subject}\033[0m"


def print_resolution_chain(chain: ResolutionChain, ansi: bool = True) -> str:
    root_repr = (
        f"{_print_qualified_name(chain.requestor, ansi)} [{chain.resolved_through}]"
    )

    children_repr = ""

    tree: deque[ResoltionChainNodePrintUnit] = deque(
        ResoltionChainNodePrintUnit.map(chain.children)
    )
    while len(tree) > 0:
        unit = tree.popleft()
        child = unit.node

        param_repr = _display_param(child.name, child.type, ansi)
        child_repr = "│  " * child.depth
        child_repr += f"{"└" if unit.is_last else "├"}─"
        child_repr += f" {param_repr} [{child.resolved_through}]"
        children_repr += f"\n{child_repr}"

        for unit in reversed(ResoltionChainNodePrintUnit.map(child.children)):
            tree.appendleft(unit)

    return f"{root_repr}{children_repr}"


def _print_qualified_name(
    subject: type[Any] | Callable[..., Any] | None, ansi: bool
) -> str:
    if subject is not None:
        (type_module, type_name) = fully_qualify(subject)
    else:
        (type_module, type_name) = (None, "Unknown")

    type_name = bold(type_name, ansi)
    return join_qualified_name((type_module, type_name))


def _display_param(name: str, param_type: type[Any] | None, ansi: bool) -> str:
    name_repr = bold(name, ansi)
    param_type_repr = _print_qualified_name(param_type, ansi)

    return f"{name_repr}: {param_type_repr}"
