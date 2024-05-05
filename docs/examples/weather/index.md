# Weather

A exemplary system for dealing with weather data.
It fetches data from various sources and shows how to e.g. work with providing API tokens to your data fetching classes.

This example will guide through the building process and highlight the usage of `diy` and the reasonings behind it.
The final source can be seen at https://github.com/NiclasvanEyk/diy/tree/main/examples/weather.

## What You Will Learn

- Integrating with `click` CLIs and `fastapi` HTTP server
- Binding concrete implementations to abstract protocols
- Replacing real implementations with test doubles while unit testing

## Goal

The main goal is to supply current weather information, based on a given city.
E.g. our CLI can be used like this:

```shell
weather "New York"
```
```
It is sunny in New York with a temperature of 24.82°C
```

The HTTP interface shares all services and roughly looks like this:

```shell
curl 'http://localhost:8000/current/New%20York'
```
```json
{
  "city": "New York",
  "temperature": 24.82,
  "conditions": "sunny"
}
```

While the result is simple, it speaks to **real** third-party APIs to get the data.
This way you see how to solve real problems, while hopefully still illustrating the benefits of using `diy`.