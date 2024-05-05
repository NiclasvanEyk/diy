# This is the command line interface to our weather application.


from click import argument, command, echo, style

from weather.client.protocol import WeatherClient
from weather.container import container


def display_weather(client: WeatherClient, city: str) -> None:
    weather = client.fetch_current(city)

    temperature_color = "blue"
    if weather.temperature > 15:
        temperature_color = "yellow"
    if weather.temperature > 30:
        temperature_color = "red"

    conditions = style(weather.conditions, italic=True)
    city = style(weather.city, italic=True)
    temperature = style(
        f"{weather.temperature:.2f}°C", italic=True, fg=temperature_color
    )

    echo(f"It is {conditions} in {city} with a temperature of {temperature}")


@command
@argument("city")
def weather(city: str) -> None:
    client = container.resolve(WeatherClient)
    display_weather(client, city)


if __name__ == "__main__":
    weather()
