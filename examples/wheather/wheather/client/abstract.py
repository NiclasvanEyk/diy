from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Conditions(StrEnum):
    """
    Maps our known states of the wheather.

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
class CurrentWheather:
    """
    The information that we use to display the current state of the wheather.
    """

    city: str
    temperature: float
    conditions: Conditions


class WheatherClient(Protocol):
    @abstractmethod
    def fetch_current(self, city: str) -> CurrentWheather:
        """
        Somehow fetches current wheather information in our format.
        """
