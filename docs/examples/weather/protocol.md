# Protocols

First, we think about what data we need, and what our business logic may look like from a high level.

## Data Structures

If you remember the examples earlier that we need some kind of summary for the current weather state.
Something like sunny, rainy or windy.
Pythons `StrEnum`s seem like a good fit for something that has a known set of states:

```python
from enum import StrEnum

class Conditions(StrEnum):
    SUNNY = "sunny"
    RAINING = "raining"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY = "partly cloudy"
    SNOWY = "snowing"
    WINDY = "windy"
```

Then we associate the information with a location and a temperature, which is a little bit more concrete than the brief state summary.

```python
from dataclasses import dataclass

@dataclass
class CurrentWeather:
    city: str
    temperature: float
    conditions: Conditions
```

This is a very simplified example, so we do not add fields for precipitation chance, wind direction / speed or other weather related fields.
Feel free to add them when you are coding along, though some might not be available for all weather providers!

## Services

Now that we have specified the shape of our data, we need a way of requesting it.

```python
from abc import abstractmethod
from typing import Protocol

class WeatherClient(Protocol):
    @abstractmethod
    def fetch_current(self, city: str) -> CurrentWeather:
        """Somehow fetches current weather information in our format."""
```

Pythons `Protocol`s let us define an abstract set of methods, that all of our implementations will need to implement.
You may also utilize abstract base classes (`abc.ABC`), for the purpose of this tutorial it does not really matter.

Concrete client implementations then inherit from the `WeatherClient` protocol and implement the required `fetch_current` method.
In our web server or CLI we then only use the `WeatherClient` for type hints, since the `diy` container will supply the right implementation for us (more on that later).

## Notes

### Why all this boilerplate?

You may ask yourself why we dont just use something like

```python
def fetch_current_weather(city: str) -> CurrentWeather: ...
```

and call it a day.
You certainly could, but in a real-world application you might also want to request information about historical weather, forecasts and more fine-grained data such as precise maps of clouds.

```python
def fetch_current_weather(city: str) -> CurrentWeather: ...
def fetch_historical_weather(city: str) -> HistoricalWeather: ...
def fetch_forecast(city: str) -> WeatherForecast: ...
```

Then you realize, that all of these require shared logic, e.g. you need a HTTP client that sends a token for authentication.

```python
def fetch_current_weather(http: HttpClient, city: str) -> CurrentWeather: ...
def fetch_historical_weather(http: HttpClient, city: str) -> HistoricalWeather: ...
def fetch_forecast(http: HttpClient, city: str) -> WeatherForecast: ...
```

And then you want to connect to another third-party service and need each of these functions again.

```python
# clients/open_weather.py
def fetch_current_weather(http: HttpClient, city: str) -> CurrentWeather: ...
def fetch_historical_weather(http: HttpClient, city: str) -> HistoricalWeather: ...
def fetch_forecast(http: HttpClient, city: str) -> WeatherForecast: ...

# clients/weather_ai.py
def fetch_current_weather(http: HttpClient, city: str) -> CurrentWeather: ...
def fetch_historical_weather(http: HttpClient, city: str) -> HistoricalWeather: ...
def fetch_forecast(http: HttpClient, city: str) -> WeatherForecast: ...
```

And now you need to ensure that each of these implements all necessary functions.

As you can see, this is clearly possible, but I'd argue in favor of the protocol-based approach.
It is better at hiding implementation details like the HTTP client, similar to methods used by other programming languages and arguably better suited for the use of static analysis tools.

### Why Implement Multiple Clients?

Having alternatives provides more flexibility.
Imagine one weather provider having an outage, or drastically increasing the prices.

If the whole weather example is a bit too boring or seems too far-fetched, just think of LLM providers like OpenAI or Claude.
Having the freedom of switching the underlying provider once one of these releases a new shiny model, without having to rewrite parts of your application is a definitive advantage.

If you want to look at it less from a business perspective and more from a programming one, you can consider databases.
Using an abstraction layer for your database, such as [SQLAlchemy](https://www.sqlalchemy.org), enables you to use an in-memory SQLite database while testing.
This simplifies the testing setup and potentially makes them run faster.
In this case, the library authors even have done most the hard work for you, you just need to structure your code a bit different.
