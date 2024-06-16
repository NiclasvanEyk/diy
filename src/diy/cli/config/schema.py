from dataclasses import dataclass


@dataclass
class DiyProjectConfig:
    containers: dict[str, str]
    """
    A mapping of a name to an import specifier.
    """
