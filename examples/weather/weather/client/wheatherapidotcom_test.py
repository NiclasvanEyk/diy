import json
from urllib.parse import parse_qsl

from httpx import Client, MockTransport, Request, Response

from weather.client.protocol import Condition
from weather.client.wheatherapidotcom import WeatherApiWeatherClient


def request_handler(request: Request) -> Response:
    query_params = {
        key.decode("utf8"): val.decode("utf8")
        for key, val in parse_qsl(request.url.query)
    }
    assert query_params["q"] == "New York"
    assert query_params["key"] == "s3cret"

    return Response(
        status_code=200,
        content=json.dumps(
            {
                "location": {
                    "name": "New York",
                },
                "current": {
                    "temp_c": 12.34,
                    "condition": {
                        "code": 1000,
                    },
                },
            }
        ),
    )


def test_with_mock_http_client() -> None:
    api_client = WeatherApiWeatherClient(
        http=Client(transport=MockTransport(request_handler)),
        key="s3cret",
    )

    weather = api_client.fetch_current("New York")
    assert weather.city == "New York"
    assert weather.temperature == 12.34
    assert weather.conditions == Condition.SUNNY
