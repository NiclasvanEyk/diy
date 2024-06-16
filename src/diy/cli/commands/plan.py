from typing import Any

from click import echo, option

from diy.cli.commands.root import root
from diy.cli.config.resolve import message_and_exit_code, resolve_config
from diy.cli.container.resolve import from_config
from diy.cli.parameters import CONTAINER_IMPORT_SPECIFIER, IMPORT_SPECIFIER
from diy.cli.utils.result import Err
from diy.container.protocol import ContainerProtocol
from diy.internal.display import print_resolution_plan
from diy.internal.planner import Planner


@root.command
@option("--container", type=CONTAINER_IMPORT_SPECIFIER)
@option("--subject", type=IMPORT_SPECIFIER)
def plan(container: ContainerProtocol | None = None, subject: Any = None) -> None:
    """
    Test how the given SUBJECT would be resolved.

    If SUBJECT refers to a type, it refers to how a new instance would be
    constructed. If it refers to a function, it describes how it would be
    called.

    You may reference a container, or configure one in your config.
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

    def display_plan(subject: Any) -> None:
        if isinstance(subject, type):
            plan = planner.plan(subject)
        elif callable(subject):
            plan = planner.plan_call(subject)
        else:
            plan = planner.plan(type(subject))

        echo(print_resolution_plan(plan))

    # show a single plan
    if subject is not None:
        display_plan(subject)
        return

    for t in planner.spec.types():
        display_plan(t)
        echo("")
