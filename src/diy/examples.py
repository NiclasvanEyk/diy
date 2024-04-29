from diy.container import Container, RuntimeContainer, Specification


class HttpClient:
    def __init__(self, base: str) -> None:
        self.base = base


class ApiClient:
    def __init__(self, http: HttpClient) -> None:
        self.http = http


def api_client() -> Container:
    spec = Specification()

    @spec.partials.decorate(HttpClient, "base")
    def build_http_client_base() -> str:
        return "https://example.com/api"

    return RuntimeContainer(spec)
