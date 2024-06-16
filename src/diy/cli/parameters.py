from typing import Any, override

from click import Context, ParamType

from diy.cli.utils.import_specifiers import message, resolve_import_specifier
from diy.cli.utils.result import Err
from diy.container.protocol import ContainerProtocol


class ImportSpecifierParamType(ParamType):
    name = "import specifier"

    @override
    def convert(self, value: Any, param: Any, ctx: Context | None) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid string", param, ctx)

        result = resolve_import_specifier(value)
        if isinstance(result, Err):
            self.fail(message(result.error), param, ctx)

        return result.value


IMPORT_SPECIFIER = ImportSpecifierParamType()


class ContainerImportSpecifierParamType(ParamType):
    name = "container import specifier"

    @override
    def convert(self, value: Any, param: Any, ctx: Context | None) -> Any:
        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid string", param, ctx)

        result = resolve_import_specifier(value)
        if isinstance(result, Err):
            # TODO: Write proper
            self.fail("TODO", param, ctx)

        subject = result.value[1]

        if callable(subject):
            subject = subject()
            if not isinstance(subject, ContainerProtocol):
                self.fail(
                    f"Function {subject!r} imported by '{value}' did not return an instance of the diy ContainerProtocol",
                    param,
                    ctx,
                )

        if not isinstance(subject, ContainerProtocol):
            self.fail(
                f"Instance {subject!r} imported by '{value}' did not refer to an instance of the diy ContainerProtocol",
                param,
                ctx,
            )

        return subject


CONTAINER_IMPORT_SPECIFIER = ContainerImportSpecifierParamType()
