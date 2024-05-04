from os import environ

from diy import Specification, VerifyingContainer
from wheather.client.abstract import WheatherClient
from wheather.client.random import RandomWheatherClient

spec = Specification()


@spec.partials.decorate(RandomWheatherClient, "seed")
def build_random_wheather_client_seed() -> int | None:
    if "WHEATHER_SEED" not in environ:
        return None
    return int(environ["WHEATHER_SEED"])


@spec.builders.decorate
def build_wheather_client(random: RandomWheatherClient) -> WheatherClient:
    return random


container = VerifyingContainer(spec)
