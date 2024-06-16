from dataclasses import dataclass
from pathlib import Path
from tomllib import loads as load_toml

from diy.cli.config.schema import DiyProjectConfig
from diy.cli.utils.result import Err, Ok, Result


@dataclass
class MissingPyprojectFile:
    searched_paths: list[str]


class MissingDiyToolSection:
    pass


@dataclass
class ViolatesSchema:
    config: dict
    error: Exception


type FailedToResolveProjectConfig = (
    MissingPyprojectFile | MissingDiyToolSection | ViolatesSchema
)


def message_and_exit_code(error: FailedToResolveProjectConfig) -> tuple[str, int]:
    match error:
        case MissingPyprojectFile():
            return ("diy is not configured! Could not find a pyproject.toml file.", 2)
        case MissingDiyToolSection():
            return (
                "diy is not configured! Add a [tools.diy] section to your pyproject.toml",
                3,
            )
        case ViolatesSchema(values, error):
            return (
                f"Invalid diy configuration!\n\nconfig: \n{values}\n\nerror: {error!r}",
                4,
            )


def resolve_config() -> Result[DiyProjectConfig, FailedToResolveProjectConfig]:
    paths = ["pyproject.toml"]
    existing: Path | None = None

    for path in paths:
        if Path(path).exists():
            existing = Path(path)
            break

    if existing is None:
        return Err(MissingPyprojectFile(paths))

    toml = load_toml(existing.read_text())

    diy_config_dict = toml.get("tool", dict()).get("diy")
    if diy_config_dict is None:
        return Err(MissingDiyToolSection())

    try:
        return Ok(DiyProjectConfig(**diy_config_dict))
    except TypeError as error:
        return Err(ViolatesSchema(diy_config_dict, error))
