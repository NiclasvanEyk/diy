from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Conditions(StrEnum):
    """
    Maps our known states of the weather.

    This might be necessary for displaying a certain kind of icon that visually
    supports the displayed data.
    """

    SUNNY = "sunny"
    RAINING = "raining"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY = "partly cloudy"
    SNOWY = "snowing"
    WINDY = "windy"


@dataclass
class CurrentWeather:
    """
    The information that we use to display the current state of the weather.
    """

    city: str
    temperature: float
    conditions: Conditions


class WeatherClient(Protocol):
    @abstractmethod
    def fetch_current(self, city: str) -> CurrentWeather:
        """
        Somehow fetches current weather information in our format.
        """
