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
        return InvalidCityResponse("The city contains digits. This must not happen!")

    client = container.resolve(WeatherClient)
    weather = client.fetch_current(city)
    return weather
