def main() -> None:
    """
    This is just a friendly wrapper around the actual commandline interface,
    which may fail unless the 'cli' extra is installed. This wrapper suggests
    installing that extra if an ImportError occurs.
    """

    try:
        from importlib import import_module
        from pathlib import Path
        from pkgutil import iter_modules

        from diy.cli.commands.root import root

        commands_dir = Path(__file__).parent / "commands"
        for c in iter_modules([str(commands_dir)], prefix="diy.cli.commands."):
            import_module(c.name)

        root()
    except ImportError as error:
        error.add_note(
            "\n".join(
                [
                    "",
                    "The error above was caught while running the diy commandline interface.",
                    "Did you install the 'cli' extra?",
                    "Maybe running the following can fix your issue:",
                    "",
                    "    pip install diy[cli]",
                    "",
                ]
            )
        )
        raise
