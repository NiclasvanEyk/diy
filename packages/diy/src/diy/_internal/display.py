from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from sys import stdout
from types import UnionType
from typing import Any

from diy._internal.plan import (
    BuilderBasedResolutionPlan,
    BuilderParameterResolutionPlan,
    CallableResolutionPlan,
    DefaultParameterResolutionPlan,
    NoArgsConstructorParameterResolutionPlan,
    ParameterPlanList,
    ParameterResolutionPlan,
    ResolutionPlan,
)

type FQN = tuple[str | None, str]


def fully_qualify(abstract: type[Any] | Callable[..., Any]) -> FQN:
    name = abstract.__qualname__

    module = abstract.__module__
    if module == "builtins":
        module = None

    return (module, name)


def join_qualified_name(fqn: FQN, ansi: bool) -> str:
    (module, name) = fqn
    if module is None:
        return name

    prefix = gray(f"{module}:", ansi)
    return f"{prefix}{name}"


def qualified_name(
    abstract: str | type[Any] | Callable[..., Any], ansi: bool = False
) -> str:
    if isinstance(abstract, UnionType):
        return f" {gray('|', ansi)} ".join(
            [qualified_name(t) for t in abstract.__args__]  # type: ignore[generalTypeIssues]
        )

    if isinstance(abstract, str):
        return abstract

    return join_qualified_name(fully_qualify(abstract), False)


@dataclass
class PlanDisplayContainer[**P, T]:
    node: ParameterResolutionPlan[P, T]
    is_last: bool

    @staticmethod
    def map(nodes: ParameterPlanList) -> list[PlanDisplayContainer[..., Any]]:
        if len(nodes) == 0:
            return []
        mapped = [PlanDisplayContainer(node, False) for node in nodes]
        mapped[-1].is_last = True
        return mapped


def bold(subject: str, ansi: bool) -> str:
    if not ansi:
        return subject
    return f"\033[1m{subject}\033[0m"


def gray(subject: str, ansi: bool) -> str:
    if not ansi:
        return subject
    return f"\x1b[38;5;7m{subject}\033[0m"


@dataclass
class PlanDecoration:
    clazz: str
    abstract: str
    function: str
    parameter: str
    constructor: str


def print_resolution_plan(
    plan: ResolutionPlan[..., Any], ansi: bool | None = None
) -> str:
    if ansi is None:
        ansi = stdout.isatty()
    if ansi is None:
        ansi = False

    root_repr = ""

    # Print the name
    if isinstance(plan, CallableResolutionPlan):
        root_repr = f"{plan.subject}"
    else:
        root_repr = _print_qualified_name(plan.type, ansi)

    # print how it is created
    if isinstance(plan, BuilderBasedResolutionPlan):
        name = _print_qualified_name(plan.builder, ansi)
        root_repr += f" <- {name}"

    # If we resolve the whole plan through a single builder, we are done here
    if isinstance(plan, BuilderBasedResolutionPlan):
        return root_repr

    # If not, we need to recursively display the parameters and their
    # resolution.
    children_repr = ""

    tree = deque(PlanDisplayContainer.map(plan.parameters))
    while len(tree) > 0:
        unit = tree.popleft()
        child = unit.node

        param_repr = _display_param(child.name, child.type, ansi)
        padding = f"{gray('│', ansi)}  " if len(tree) > 0 else "   "
        child_repr = "" + padding * child.depth
        child_repr += gray(f"{"└" if unit.is_last else "├"}─", ansi)
        child_repr += f"{param_repr}"
        if isinstance(child, BuilderParameterResolutionPlan):
            name = _print_qualified_name(child.builder, ansi)
            child_repr += f" {gray('<-', ansi)} {name}"
        if isinstance(child, NoArgsConstructorParameterResolutionPlan):
            child_repr += f" {gray('<-', ansi)} {child.type.__name__}()"
        children_repr += f"\n{child_repr}"

        if isinstance(child, DefaultParameterResolutionPlan):
            continue
        if isinstance(child, BuilderParameterResolutionPlan):
            continue
        if isinstance(child, NoArgsConstructorParameterResolutionPlan):
            continue

        for unit in reversed(PlanDisplayContainer.map(child.parameters)):
            tree.appendleft(unit)

    return f"{root_repr}{children_repr}"


def _print_qualified_name(
    subject: type[Any] | Callable[..., Any] | None, ansi: bool
) -> str:
    if isinstance(subject, UnionType):
        return " | ".join([_print_qualified_name(t, ansi) for t in subject.__args__])  # type: ignore[generalTypeIssues]

    if subject is not None:
        (type_module, type_name) = fully_qualify(subject)
    else:
        (type_module, type_name) = (None, "Unknown")

    type_name = bold(type_name, ansi)
    return join_qualified_name((type_module, type_name), ansi)


def _display_param(name: str, param_type: type[Any] | None, ansi: bool) -> str:
    name_repr = bold(name, ansi)
    param_type_repr = _print_qualified_name(param_type, ansi)

    return f"{name_repr}: {param_type_repr}"
