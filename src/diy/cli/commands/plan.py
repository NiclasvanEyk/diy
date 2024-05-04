from typing import Any

from click import argument, echo, option

from diy.cli.commands.root import root
from diy.cli.parameters import CONTAINER_IMPORT_SPECIFIER, IMPORT_SPECIFIER
from diy.container import Container
from diy.internal.display import print_resolution_plan
from diy.internal.planner import Planner


@root.command
@argument("container", type=CONTAINER_IMPORT_SPECIFIER)
@option("--subject", type=IMPORT_SPECIFIER)
def plan(container: Container, subject: Any = None) -> None:
    """
    Test how the given CONTAINER would construct the given SUBJECT.

    If SUBJECT refers to a type, it refers to how a new instance would be
    constructed. If it refers to a function, it describes how it would be
    called.
    """

    planner = container._planner
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
