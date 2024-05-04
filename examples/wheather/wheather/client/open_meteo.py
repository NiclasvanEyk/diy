from wheather.client.abstract import WheatherClient


class OpenMeteoWheatherClient(WheatherClient):
    def __init__(self) -> None:
        super().__init__()

    def fetch_current(self, city: str) -> CurrentWheather:
        return await super().fetch_current(city)
