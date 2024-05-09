from typing import override

from numpy.random import default_rng

from weather.client.protocol import (
    Condition,
    CurrentWeather,
    WeatherClient,
)


class RandomWeatherClient(WeatherClient):
    def __init__(self, seed: int | None = None) -> None:
        super().__init__()
        self.rng = default_rng(seed)

    @override
    def fetch_current(self, city: str) -> CurrentWeather:
        return CurrentWeather(
            city=city,
            temperature=self.rng.normal(loc=15, scale=25),
            conditions=self.rng.choice(list(Condition)),
        )
