from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, FastAPI

from weather.client.protocol import CurrentWeather, WeatherClient
from weather.container import container

app = FastAPI()


@dataclass
class InvalidCityResponse:
    error: str


def FromContainer[T](dependency: type[T]) -> Any:  # noqa: N802
    def dependency_resolver() -> T:
        return container.resolve(dependency)

    return Depends(dependency_resolver)


@app.get("/current/{city}")
def current_weather_in_city(
    city: str,
    client: Annotated[WeatherClient, FromContainer(WeatherClient)],
) -> CurrentWeather | InvalidCityResponse:
    if any(character.isdigit() for character in city):
        # We would also set the HTTP status to 4xx
        return InvalidCityResponse("The city contains digits. This must not happen!")

    return client.fetch_current(city)
