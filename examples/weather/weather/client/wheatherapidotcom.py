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

    def _issue_request(self, city: str) -> Response:
        parameters = urlencode({"q": city, "key": self._key})
        return self._http.get(
            f"https://api.weatherapi.com/v1/current.json?{parameters}"
        )

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
