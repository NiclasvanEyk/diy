# diy

A dependency injection container that heavily utilizes Pythons type annotations.

-------------------------------

# Examples

### Weather Application

We construct an application that tells us the current temperature.
Exciting, right?

To realize this, we use an imaginary third-party API that we call over HTTP.
The author of said API has given us a secret token that we need to send in a header.
This way, the author prevents unwanted usage of their API and can block tokens that make too many requests.

We create a class for 

```python
import dataclasses

# This is roughly what our imaginary API would return
@dataclasses.dataclass
class WeatherApiResponse:
  city: str
  description: str
  celsius: float
  farenheit: float


class WeatherApiClient:
  def __init__(self, secret_token: str):
    self.secret_token = secret_token

  def request_wheather(city: str) -> WeatherApiResponse
    # The actual implementation is of no importance, so we'll ignore it.
    # Just imagine we use your favourite python library to make a GET request
    # and also include the value of `self.secret_token` to authenticate 
    # ourselves.

  # In this example we won't define more methods on this class. But it can be
  # really practical to e.g. make one method per endpoint the API provides.
  # Maybe our weather API also can tell us information about the forecast or
  # historical statistics. Then we can simply add more methods to this class,
  # that deal with the details of those endpoints.
```



```python
import diy

# A specification is just a way of telling our container how to construct 
# certain types of objects.
spec = diy.Specification()

# Lets take this one as an example
class WeatherApiClient:
  def __init__(self, secret_token: str):
    self.secret_token = secret_token

  ...

# You might call a third-party API, which requires you to send a secret token 
# in a header as a security mechanism. There is no way for us to automatically 
# know the value of your secret token, so there is some code required from you 
# to tell the container how to get it.
# Lets read it from an environment as start.
import os
spec.add(WeatherApiClient, lambda: ApiClient(os.environ["API_CLIENT_TOKEN"])

# If we are done constructing our specification, we can use it to build a 
# container. This is just an object that we can use to actually build instances
# of the types we specified.
container = diy.container.RuntimeContainer(spec)

# Just tell it what type you want
api_client = container.resolve(WeatherApiClient)

# This might not be that impressive, so lets imagine you also create a service
# class, so you could easily swap our your API provider or return fake 
# responses while testing.
class WheatherService():
  def __init__(self, api: WeatherApiClient):
    self.api = api

  ...

# Since the WheatherService only relies on types already known to our 
# container, no more setup is required. The container looks at the constructor 
# of the WheatherService class and constructs an ApiClient for it as we have 
# instructed it to do.
service = container.resolve(WheatherService)
```
