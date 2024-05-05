# First Real Implementation

The aptly named [Weatherapi website](https://www.weatherapi.com) has all features we need and a simple to use HTTP API.
It requires an API key to use.

## Implementing The Client

```python
# weather/client/wheatherapidotcom.py
from urllib.parse import urlencode
from httpx import Client, Response
from weather.client.protocol import Conditions, CurrentWeather, WeatherClient


class WeatherApiWeatherClient(WeatherClient):
    def __init__(self, http: Client, key: str) -> None:
        super().__init__()
        self._http = http
        self._key = key

    def fetch_current(self, city: str) -> CurrentWeather:
        response = self._issue_request(city)
        weather = self._map_response(response)
        return weather
```

Our client takes two constructor arguments:

- A `httpx.Client`, something that can issue HTTP requests
- An API key that we use to authenticate our application when making requests to weatherapi.com

For now, we ignore how we get these two, just imagine we magically get the right values from somewhere.
This is exactly what dependency injection / inversion of control is about.

The implementation of `fetch_current` looks quite simple, we somewhow issue a HTTP request to the API and then transform the response into our `CurrentWeather` object.

> The remaining code is specific to the weatherapi.com API, so if you are not interested, feel free to skip ahead to the next section.

When issuing our request, we need to set the `q` query parameter to our "search" query.
We simply use the `city` that was passed to us and hope for the best.
Additionally, we need to tell the API who we are, by setting the `key` query parameter to the API key identifying our application.
Since we assume to get passed the right one, we simply set it to the one passed to this instance upon construction.

```python
    def _issue_request(self, city: str) -> Response:
        parameters = urlencode({"q": city, "key": self._key})
        return self._http.get(
            f"https://api.weatherapi.com/v1/current.json?{parameters}"
        )
```

The next methods deal with mapping the response form the wheatherapi.com schema, to the one used by our application.
These won't match one-to-one, so we need to use some transformation steps.

```python
    def _map_response(self, response: Response) -> CurrentWeather:
        body = response.json()
        return CurrentWeather(
            city=body["location"]["name"],
            temperature=body["current"]["temp_c"],
            conditions=self._map_conditions(body["current"]["condition"]["code"]),
        )

    def _map_conditions(self, code: int) -> Conditions:
        # Full list at https://www.weatherapi.com/docs/weather_conditions.json
        # This implementation is abbreviated on purpose.
        if code == 1000:
            return Conditions.SUNNY
        if code == 1006:
            return Conditions.CLOUDY
        if code > 1183 and code <= 1282:
            return Conditions.RAINING
        return Conditions.WINDY

```

And thats it.
We can now continue with implementing "passing the right values" when constructing an instance of our `WeatherApiWeatherClient`.

## Adjusting Our Container

To recap:

> Our client takes two constructor arguments:
>
> - A `httpx.Client`, something that can issue HTTP requests
> - An API key that we use to authenticate our application when making requests to weatherapi.com

As far as our `diy` container is concerned, the first constructor parameter one is not a problem.
All of its constructor arguments [are optional](https://www.python-httpx.org/api/#client), so it can just run `httpx.Client()` to get a fresh instance.
The API key however can not be automatically built.
Here is where we explicitly need to tell our container, how the key should be retrieved.

### Hardcoded Keys And Builder Function

One option would be to just hardcode the value and call it a day

```python
# weather/container.py
from weather.client.wheatherapidotcom import WeatherApiWeatherClient
from httpx import Client

# ...

@spec.builders.decorate
def build_weather_api_client() -> WeatherApiWeatherClient:
    http = Client()
    api_key = "s3cr3t"

    return WeatherApiWeatherClient(http, api_key)

# ...
```

We add the necessary import statements, and add a new builder function to our specification.
This one just builds an instance of `httpx.Client` and hardcodes the api key.

### Partials And Environment Variables

The approach from the previous section works, but could also be done differently.
Our builder function was necessary to tell our container how to get the api key.
The construction of `httpx.Client` is not complicated, and could have been done by our container.

```python
# weather/container.py
from weather.client.wheatherapidotcom import WeatherApiWeatherClient
from os import environ

# ...

@spec.partials.decorate(WeatherApiWeatherClient, "key")
def build_weather_api_client_key() -> str:
    return "s3cr3t"

# ...
```

## Adding Tests
