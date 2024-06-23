import json
from dataclasses import asdict

from click import echo

from diy_cli.commands.root import root
from diy_cli.config.resolve import (
    message_and_exit_code,
    resolve_config,
)
from diy_cli.utils.result import Err


@root.command
def config() -> None:
    """
    Prints the current configuration in JSON to the console.

    Exit codes:
    1       General error.
    2       pyproject.toml not found.
    3       pyproject.toml is missing a tools.diy section.
    4       pyproject.toml has a tools.diy section, but it violates the
            configuration schema.
    """

    configuration = resolve_config()
    if isinstance(configuration, Err):
        [message, exit_code] = message_and_exit_code(configuration.error)
        echo(message, err=True)
        exit(exit_code)

    echo(json.dumps(asdict(configuration.value), indent=4))
