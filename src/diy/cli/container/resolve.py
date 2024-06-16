from dataclasses import dataclass

from diy.cli.config.schema import DiyProjectConfig
from diy.cli.utils.import_specifiers import FailureReason, resolve_import_specifier
from diy.cli.utils.result import Err, Ok, Result
from diy.container.protocol import ContainerProtocol


class NoContainerConfigured:
    message = "Unable to resolve container from configuration!"


@dataclass
class FailedToImportSpecifier:
    cause: FailureReason


@dataclass
class ResolvedWrongType:
    actual: type


type ConfigResolutionError = (
    NoContainerConfigured | FailedToImportSpecifier | ResolvedWrongType
)


def from_config(
    config: DiyProjectConfig,
) -> Result[ContainerProtocol, ConfigResolutionError]:
    specifier = None
    if len(config.containers) == 1:
        specifier = next(iter(config.containers.values()))

    if "default" in config.containers:
        specifier = config.containers["default"]

    if specifier is None:
        return Err(NoContainerConfigured())

    result = resolve_import_specifier(specifier)

    if isinstance(result, Err):
        return Err(FailedToImportSpecifier(result.error))

    resolved = result.value[1]

    if not isinstance(resolved, ContainerProtocol):
        return Err(ResolvedWrongType(type(resolved)))

    return Ok(resolved)
