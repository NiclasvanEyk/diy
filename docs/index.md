# Introduction

`diy` (/ˌdi.aɪˈwaɪ/) is a [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection)
container that reads Pythons native type annotations, so you don't have to 
clutter your code with `Annotated` or other library specific markers.

## Getting Started

First, install the package using your favourite package manager

```shell
pip install diy
```

Then start specifying how to construct objects of a certain type:

```python
import diy
import os

# Our specification tells the container how to construct types
spec = diy.Specification()

# Lets start with the example of an API client, that authenticates by including
# a secret token in a header. However, it has no hard opinions for how to 
# retrieve that token. It just takes it as a constructor parameter.
class ApiClient:
  def __init__(self, token: str):
    self.token = token

# We now teach our spec how to build an instance of this class, by reading the
# token from an environment variable.
@spec.builders.decorate
def build_api_client() -> ApiClient:
  return ApiClient(token=os.environ["API_TOKEN"])
```

Once you are done specifying, you can construct a container based on the specification:

```python
# Pass the previously constructed spec to your container
container = diy.RuntimeContainer(spec)

# If we need an instance of our client, we can simply request it from the 
# container
api_client = container.resolve(ApiClient)

# Additionally, if we have classes that only depend on classes that we already
# know how to construct, we don't need to specify them explicitly.
class UserService:
  def __init__(self, api: ApiClient):
    self.api = api

# Since the UserService class only needs an instance of ApiClient, which we 
# know how to construct, we in turn assume how a UserService should be 
# constructed.
user_service = container.resolve(UserService)
```

This was just a simple example.
To learn about more features, you can move forward and read through [the guide](/guide).
It into more detail about how to solve certain edge cases, such as only defining how certain parameters should be resolved, or how to opt-out of the implicit resolving and construct the `UserService` in a different way.

Alternatively you could look at [some more in-depth examples](/examples).
They show how `diy` works in a real-world scenario, and how using its `Container`s make e.g. testing easier.

