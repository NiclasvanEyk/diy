from dataclasses import dataclass
from importlib import import_module
from types import ModuleType

from diy.cli.utils.result import Err, Ok, Result


class UnsupportedRelativeImport:
    pass


class MissingColon:
    pass


@dataclass
class MultipleColons:
    amount: int


@dataclass
class ImportFailed:
    module: str
    error: ImportError


@dataclass
class SymbolNotFound:
    module: str
    symbol: str
    known: list[str]


type FailureReason = (
    UnsupportedRelativeImport
    | MissingColon
    | MultipleColons
    | ImportFailed
    | SymbolNotFound
)


def message(reason: FailureReason) -> str:
    match reason:
        case UnsupportedRelativeImport():
            return "relative imports are not supported"
        case MissingColon():
            return "an import specifier needs to contain at least one ':'. Use the form my.module:value to refer to a value from a specific module"
        case MultipleColons(amount):
            return f"an import specifier must contain exactly one ':', but yours contained {amount}"
        case ImportFailed(module_name, error):
            return f"Failed to import '{module_name}': {error!r}"
        case SymbolNotFound(module_name, symbol_name, symbols):
            known = "\n".join([f"- {symbol}" for symbol in symbols])
            return f"Could not find '{symbol_name}' in module '{module_name}'.\nFound:\n{known}"


def resolve_import_specifier(
    specifier: str,
) -> Result[tuple[ModuleType, object], FailureReason]:
    """
    Either resolves the specifier, or returns a string desribing why the
    resolution failed.
    """

    if specifier.startswith("."):
        return Err(UnsupportedRelativeImport())
        # return "relative imports are not supported"

    parts = specifier.split(":")
    if len(parts) < 2:
        return Err(MissingColon())
        # return "an import specifier needs to contain at least one ':'. Use the form my.module:value to refer to a value from a specific module"
    if len(parts) > 2:
        return Err(MultipleColons(len(parts)))
        # return f"an import specifier must contain exactly one ':', but yours contained {len(parts)}"

    module_name, symbol_name = parts

    try:
        module = import_module(module_name)
    except ImportError as error:
        return Err(ImportFailed(module_name, error))
        # return f"Failed to import '{module_name}'"

    symbols = (
        module.__all__
        if hasattr(module, "__all__")
        else [x for x in dir(module) if not x.startswith("__")]
    )
    if symbol_name not in symbols:
        return Err(SymbolNotFound(module_name, symbol_name, symbols))
        # known = "\n".join([f"- {symbol}" for symbol in symbols])
        # return f"Could not find '{symbol_name}' in module '{module_name}'.\nFound:\n{known}"

    return Ok((module, getattr(module, symbol_name)))
