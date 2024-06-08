from os import environ

from diy import Specification, VerifyingContainer
from weather.client.protocol import WeatherClient
from weather.client.random import RandomWeatherClient

spec = Specification()


# This function tells us how our application builds a client returning random
# weather information. This might be useful for unit testing environments,
# where we only want to test e.g. the HTTP endpoint or a CLI function.
@spec.partials.decorate(RandomWeatherClient, "seed")
def build_random_weather_client_seed() -> int | None:
    if "WEATHER_SEED" not in environ:
        return None
    return int(environ["WEATHER_SEED"])


# This sets the "default" implementation of a weather client for the whole
# container. Since the arguments of builder function are also provided by the
# container, it will construct the RandomWeatherClient and use the seed
# argument as defined in our build_random_whather_client_seed function from
# above.
@spec.decorate
def build_weather_client(random: RandomWeatherClient) -> WeatherClient:
    return random


container = VerifyingContainer(spec)
