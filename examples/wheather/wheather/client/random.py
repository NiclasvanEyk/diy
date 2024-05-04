from typing import override

from numpy.random import default_rng
from wheather.client.abstract import Conditions, CurrentWheather, WheatherClient


class RandomWheatherClient(WheatherClient):
    def __init__(self, seed: int | None = None) -> None:
        super().__init__()
        self.rng = default_rng(seed)

    @override
    def fetch_current(self, city: str) -> CurrentWheather:
        return CurrentWheather(
            city=city,
            temperature=self.rng.normal(loc=15, scale=25),
            conditions=self.rng.choice(list(Conditions)),
        )
