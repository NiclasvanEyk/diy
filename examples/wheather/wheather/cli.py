# This is the command line interface to our wheather application.


from click import argument, command, echo, style
from wheather.client.abstract import WheatherClient
from wheather.container import container


def display_wheather(client: WheatherClient, city: str) -> None:
    wheather = client.fetch_current(city)

    temperature_color = "blue"
    if wheather.temperature > 15:
        temperature_color = "yellow"
    if wheather.temperature > 30:
        temperature_color = "red"

    conditions = style(wheather.conditions, italic=True)
    city = style(wheather.city, italic=True)
    temperature = style(
        f"{wheather.temperature:.2f}°C", italic=True, fg=temperature_color
    )

    echo(f"It is {conditions} in {city} with a temperature of {temperature}")


@command
@argument("city")
def wheather(city: str) -> None:
    client = container.resolve(WheatherClient)
    display_wheather(client, city)


if __name__ == "__main__":
    wheather()
