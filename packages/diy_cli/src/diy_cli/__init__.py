from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

from diy_cli.commands.root import root


def main() -> None:
    """
    This is just a friendly wrapper around the actual commandline interface,
    which may fail unless the 'cli' extra is installed. This wrapper suggests
    installing that extra if an ImportError occurs.
    """

    commands_dir = Path(__file__).parent / "commands"
    for c in iter_modules([str(commands_dir)], prefix="diy_cli.commands."):
        import_module(c.name)

    root()
