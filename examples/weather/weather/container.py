from os import environ

from diy import Container

from weather.client.constant import ConstantWeatherClient
from weather.client.protocol import Condition, CurrentWeather, WeatherClient
from weather.client.random import RandomWeatherClient
from weather.client.wheatherapidotcom import WeatherApiWeatherClient

container = Container()


@container.add
def build_constant_weather_client() -> ConstantWeatherClient:
    return ConstantWeatherClient(
        weather=CurrentWeather(
            city="New York",
            temperature=12.34,
            conditions=Condition.SUNNY,
        )
    )


@container.add(WeatherApiWeatherClient, "key")
def build_weather_api_weather_client_key() -> str:
    if "WEATHERAPIDOTCOM_KEY" not in environ:
        message = "WEATHERAPIDOTCOM_KEY needs to be defined in the environment!"
        raise Exception(message)
    return str(environ["WEATHERAPIDOTCOM_KEY"])


# This function tells us how our application builds a client returning random
# weather information. This might be useful for unit testing environments,
# where we only want to test e.g. the HTTP endpoint or a CLI function.
@container.add(RandomWeatherClient, "seed")
def build_random_weather_client_seed() -> int | None:
    if "WEATHER_SEED" not in environ:
        return None
    return int(environ["WEATHER_SEED"])


# This sets the "default" implementation of a weather client for the whole
# container. Since the arguments of builder function are also provided by the
# container, it will construct the RandomWeatherClient and use the seed
# argument as defined in our build_random_whather_client_seed function from
# above.
@container.add
def build_weather_client(random: RandomWeatherClient) -> WeatherClient:
    return random
