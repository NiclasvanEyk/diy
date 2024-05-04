from diy.container import RuntimeContainer, Specification


class HttpClient:
    def __init__(self, base: str) -> None:
        self.base = base


class ApiClient:
    def __init__(self, http: HttpClient) -> None:
        self.http = http


spec = Specification()


@spec.partials.decorate(HttpClient, "base")
def build_http_client_base() -> str:
    return "https://example.com/api"


container = RuntimeContainer(spec)
