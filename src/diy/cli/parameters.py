from importlib import import_module
from types import ModuleType
from typing import Any

from click import ParamType

from diy import Container


def resolve_import_specifier(specifier: str) -> str | tuple[ModuleType, Any]:
    if specifier.startswith("."):
        return "relative imports are not supported"

    parts = specifier.split(":")
    if len(parts) < 2:
        return "an import specifier needs to contain at least one ':'. Use the form my.module:value to refer to a value from a specific module"
    if len(parts) > 2:
        return f"an import specifier must contain exactly one ':', but yours contained {len(parts)}"

    module_name, symbol_name = parts

    try:
        module = import_module(module_name)
    except ImportError:
        # TODO: Maybe include the stacktrace here?
        return f"Failed to import '{module_name}'"

    symbols = (
        module.__all__
        if hasattr(module, "__all__")
        else [x for x in dir(module) if not x.startswith("__")]
    )
    if symbol_name not in symbols:
        known = "\n".join([f"- {symbol}" for symbol in symbols])
        return f"Could not find '{symbol_name}' in module '{module_name}'.\nFound:\n{known}"

    return module, getattr(module, symbol_name)


class ImportSpecifierParamType(ParamType):
    def convert(self, value: Any, param, ctx) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid string", param, ctx)

        result = resolve_import_specifier(value)
        if isinstance(result, str):
            self.fail(result, param, ctx)

        module, value = result
        return value


IMPORT_SPECIFIER = ImportSpecifierParamType()


class ContainerImportSpecifierParamType(ParamType):
    def convert(self, value: Any, param, ctx) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid string", param, ctx)

        result = resolve_import_specifier(value)
        if isinstance(result, str):
            self.fail(result, param, ctx)

        module, subject = result

        if callable(subject):
            subject = subject()
            if not isinstance(subject, Container):
                self.fail(
                    f"Function {subject!r} imported by '{value}' did not return an instance of diy.Container",
                    param,
                    ctx,
                )

        if not isinstance(subject, Container):
            self.fail(
                f"Instance {subject!r} imported by '{value}' did not refer to an instance of diy.Container",
                param,
                ctx,
            )

        return subject


CONTAINER_IMPORT_SPECIFIER = ContainerImportSpecifierParamType()
