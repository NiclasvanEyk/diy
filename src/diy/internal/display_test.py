from diy.internal.display import print_resolution_chain
from diy.resolution import ResolutionChain, ResolutionChainNode, ResolvedThrough


class Logger: ...


class Encrypter: ...


class HttpClient: ...


class ApiClient:
    def __init__(self, http: HttpClient): ...


class SmtpTransport:
    def __init__(self, crypt: Encrypter): ...


class Mailer:
    def __init__(self, transport: SmtpTransport, from_addr: str): ...


class UserService:
    def __init__(self, api: ApiClient, mailer: Mailer, logger: Logger): ...


def test_it_can_display_long_resolution_chains() -> None:
    chain = ResolutionChain(
        requestor=UserService,
        resolved_through=ResolvedThrough.INFERENCE,
        children=[
            ResolutionChainNode(
                name="api",
                depth=0,
                type=ApiClient,
                resolved_through=ResolvedThrough.INFERENCE,
                children=[
                    ResolutionChainNode(
                        name="http",
                        depth=1,
                        type=HttpClient,
                        resolved_through=ResolvedThrough.INFERENCE,
                    ),
                ],
            ),
            ResolutionChainNode(
                name="mailer",
                depth=0,
                type=Mailer,
                children=[
                    ResolutionChainNode(
                        name="transport",
                        depth=1,
                        type=SmtpTransport,
                        resolved_through=ResolvedThrough.INFERENCE,
                        children=[
                            ResolutionChainNode(
                                name="crypt",
                                depth=2,
                                type=Encrypter,
                                resolved_through=ResolvedThrough.INFERENCE,
                            ),
                        ],
                    ),
                    ResolutionChainNode(
                        name="from_addr",
                        depth=1,
                        type=str,
                        resolved_through=ResolvedThrough.PARTIAL,
                    ),
                ],
            ),
            ResolutionChainNode(
                name="logger",
                depth=0,
                type=Logger,
                resolved_through=ResolvedThrough.INFERENCE,
            ),
        ],
    )

    print(f"\n{print_resolution_chain(chain)}")
