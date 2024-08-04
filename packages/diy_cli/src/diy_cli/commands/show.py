import json
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from click import argument, echo, option
from diy._internal.display import fully_qualify, print_resolution_plan, qualified_name
from diy._internal.plan import ResolutionPlan
from diy._internal.planner import Planner
from diy.container.protocol import ContainerProtocol

from diy_cli.commands.root import root
from diy_cli.config.resolve import message_and_exit_code, resolve_config
from diy_cli.container.resolve import from_config
from diy_cli.parameters import CONTAINER_IMPORT_SPECIFIER, IMPORT_SPECIFIER
from diy_cli.serialization.format import DisplayFormat
from diy_cli.serialization.v1 import (
    NamespacedType,
    PlanKind,
    PrintedContainer,
    PrintedPlan,
)
from diy_cli.utils.result import Err


@root.command
@option(
    "--container",
    type=CONTAINER_IMPORT_SPECIFIER,
    help="The container that the subject should be resolved from",
)
@option(
    "--format",
    type=DisplayFormat,
    help="Determines the output format.",
)
@argument(
    "subject",
    type=IMPORT_SPECIFIER,
    required=False,
)
def show(
    container: ContainerProtocol | None = None,
    subject: None | type | Callable[..., Any] | str = None,
    format: DisplayFormat = DisplayFormat.TEXT,
) -> None:
    """
    Show how the given SUBJECT would be resolved. If omitted, all types and
    functions known by the container are listed.

    Subject is an import specifier, e.g. "app.services:MyService". If SUBJECT
    refers to a type, it refers to how a new instance would be constructed. If
    it refers to a function, it describes how it would be called.

    If you do not specify a container explicitly, the default one from the
    project configuration will be used.
    """

    if container is None:
        result = resolve_config()
        if isinstance(result, Err):
            [message, exit_code] = message_and_exit_code(result.error)
            echo(f"Failed to resolve configuration: {message}", err=True)
            exit(exit_code)
        config = result.value

        result = from_config(config)
        if isinstance(result, Err):
            echo(f"Failed to resolve container: ${result.error!r}", err=True)
            exit(1)
        container = result.value

    planner = container._planner  # noqa: SLF001
    if not isinstance(planner, Planner):
        echo(
            f"_planner attribute of {container!r} does not contain an instance of diy.Planner!"
        )

    if format == DisplayFormat.TEXT:
        if subject is not None:
            _display_text_plan(subject)
            return

        for subject in planner.spec.types():
            _display_text_plan(subject)
            echo("")
    else:
        if subject is not None:
            # TODO: Implement this
            message = "Not implemented yet!"
            raise Exception(message)

        _display_all_plans_in_json(planner)


def _get_plan[T](planner: Planner, subject: T) -> ResolutionPlan[..., T]:
    if isinstance(subject, type):
        return planner.plan(subject)

    if callable(subject):
        return planner.plan_call(subject)

    return planner.plan(type(subject))


def _display_text_plan(subject: Any) -> None:
    echo(print_resolution_plan(_get_plan(subject)))


def _display_all_plans_in_json(planner: Planner) -> None:
    plans: dict[str, PrintedPlan] = {}
    for subject in planner.spec.types():
        namespace, name = fully_qualify(subject)
        plans[qualified_name(subject)] = PrintedPlan(
            kind=PlanKind.INFERENCE,
            subject=NamespacedType(
                namespace=namespace,
                name=name,
            ),
        )
    ordered_plans: OrderedDict[str, PrintedPlan] = OrderedDict(sorted(plans.items()))
    container = PrintedContainer(plans=ordered_plans)
    echo(json.dumps(asdict(container), indent=4))
