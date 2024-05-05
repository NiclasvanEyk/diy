# Minimum Viable Product / Implementation

Now we implement our first demo client, the web server and wire everything up using `diy`.
We use a minimal implementation, that does not issue actual requests to a third-party, but satisfies our protocols and pass static analysis.

## `ConstantWeatherClient`

The most boring implementation is one that always returns the same weather for every city.
It is not very practical, but is enough to be used for unit tests of our other components, that require an implementation to be useful.

```python
# weather/clients/constant.py
from typing import override
from weather.client.protocol import CurrentWeather, WeatherClient

class ConstantWeatherClient(WeatherClient):
    def __init__(self, weather: CurrentWeather) -> None:
        self._weather = weather

    @override
    def fetch_current(self, city: str) -> CurrentWeather:
        return CurrentWeather(
            city=city,
            temperature=self._weather.temperature,
            conditions=self._weather.conditions,
        )
```

We use a few best practises, such as marking the implemented protocol method with `@override`, but other than that, this implementation is not really interesting.
It always returns the same temperature and conditions that we provide it upon construction.

## Specification And Container

Now lets create our `diy` Container.

```python
# weather/container.py
from diy import Specification, VerifyingContainer
from weather.client.protocol import WeatherClient, CurrentWeather, Conditions
from weather.client.constant import ConstantWeatherClient

spec = Specification()

@spec.builders.decorate
def build_weather_client() -> WeatherClient:
    return ConstantWeatherClient(
        CurrentWeather(
            city="demo",
            temperature=12.34,
            conditions=Conditions.SUNNY,
        )
    )

container = VerifyingContainer(spec)
```

We teach our spec that when something requires a `WeatherClient` instance, we build one that always returns sunny, 12.34 degrees.

## HTTP Server

Now

```python hl_lines="5 21"
# weather/http.py
from dataclasses import dataclass
from fastapi import FastAPI
from weather.client.protocol import CurrentWeather, WeatherClient
from weather.container import container

app = FastAPI()

@dataclass
class InvalidCityResponse:
    error: str

@app.get("/current/{city}")
def current_weather_in_city(city: str) -> CurrentWeather | InvalidCityResponse:
    if any(character.isdigit() for character in city):
        # We would also set the HTTP status to 4xx
        return InvalidCityResponse(
            "The city contains digits. This must not happen!"
        )

    client = container.resolve(WeatherClient)
    weather = client.fetch_current(city)
    return weather
```

> Apologies to any cities that contain digits.
> This is just an example for business logic and I could not come up with a better one.

Regarding the usage of `diy`, the highlighted lines are interesting.
There we first import our container, and request an instance of `WeatherClient`.
The container then will supply us an instance of `ConstantWeatherClient`, as defined by our `build_weather_client` function.

Running

```shell
fastapi weather/http.py
```

starts a local server, enabling to make request by either navigating to http://localhost:8000/docs and use the web interface or by issuing `curl` commands on our terminal.

## Testing

Lets use pytest for our unit test

```python
# weather/http_test.py
from fastapi.testclient import TestClient
from weather.http import app


# This tests the happy path.
# We don't do very concrete validation, since the values are all random anyways.
def test_cities_with_numbers_are_valid():
    response = TestClient(app).get("/current/imaginary-city")
    temperature = response.json()["temperature"]
    assert isinstance(temperature, float)


# We can also test our validation logic.
# Since we are using a fake implementation right now, we don't really need to
# think about not making real requests to a third-party API.
def test_cities_with_numbers_get_rejected():
    response = TestClient(app).get("/current/imaginary-city-123")
    assert response.json() == {
        "error": "The city contains digits. This must not happen!"
    }
```

And now we validate that everything still works:

```
pytest --no-header
======================= test session starts =================================
collected 2 items                                                                                                          

weather/http_test.py ..                                                [100%]

================== 2 passed, 0 warnings in 1.90s ============================
```
