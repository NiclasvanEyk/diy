from diy.internal.display import print_resolution_plan

# FIXME: Use the new plans
from diy.internal.planner import Planner
from diy.specification import Specification


class Logger:
    ...


class Encrypter:
    ...


class HttpClient:
    ...


class ApiClient:
    def __init__(self, http: HttpClient) -> None:
        ...


class SmtpTransport:
    def __init__(self, crypt: Encrypter) -> None:
        ...


class Mailer:
    def __init__(self, transport: SmtpTransport, from_addr: str) -> None:
        ...


class UserService:
    def __init__(self, api: ApiClient, mailer: Mailer, logger: Logger) -> None:
        ...


def test_it_can_display_long_resolution_plans() -> None:
    spec = Specification()

    @spec.partials.decorate(Mailer, "from_addr")
    def build_mailer_from_addr() -> str:
        return "foo"

    plan = Planner(spec).plan(UserService)

    snapshot = """tests.internal.display_test.UserService
├─ api: tests.internal.display_test.ApiClient
│  └─ http: tests.internal.display_test.HttpClient
├─ mailer: tests.internal.display_test.Mailer
│  ├─ transport: tests.internal.display_test.SmtpTransport
│  │  └─ crypt: tests.internal.display_test.Encrypter
│  └─ from_addr: str <- tests.internal.display_test.test_it_can_display_long_resolution_plans.<locals>.build_mailer_from_addr
└─ logger: tests.internal.display_test.Logger"""

    actual = print_resolution_plan(plan, ansi=False)

    assert snapshot == actual
