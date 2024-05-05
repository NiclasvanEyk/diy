from typing import override

from weather.client.protocol import CurrentWeather, WeatherClient


class ConstantWeatherClient(WeatherClient):
    def __init__(self, weather: CurrentWeather) -> None:
        super().__init__()
        self._weather = weather

    @override
    def fetch_current(self, city: str) -> CurrentWeather:
        return CurrentWeather(
            city=city,
            temperature=self._weather.temperature,
            conditions=self._weather.conditions,
        )
