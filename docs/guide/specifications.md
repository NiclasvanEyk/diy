# Specifications

Specifications are one half of `diy`.
They determine how objects should be constructed.
While `diy` tries to [infer as much as possible](/reference/guiding-principles/#infer-as-much-as-possible), there are some edge cases where a sensible default cannot be inferred.

Lets start with an example showing _why_ we even need them:

```python
from enum import StrEnum

class HashingAlgorithm(StrEnum):
  SHA256 = "sha256"
  CRC32 = "crc32"
  MD5 = "md5"

class PasswordHasher:
  def __init__(self, algorithm: HashingAlgorithm):
    self.algorithm = algorithm

  # ...
```

In this case, it can not be automatically inferred what `HashingAlgorithm` to use, when constructing a `PasswordHasher`.
If you would try to resolve an instance of `PasswordHasher` without any specifications, you would receive

```python
import diy

container = diy.RuntimeContainer()
hasher = container.get(PasswordHasher)
# 🧨💥 raises a diy.errors.UnresolvableDependencyError
```

To solve this, we _explicitly_ need to tell the container how it should construct one.
And this is where specs come into play.

## Defining Specifications



```python
@spec.decorate
def build_hasher() -> PasswordHasher:
  return PasswordHasher(HashingAlgorithm.CRC32)
```

!!! warning "Always annotate the return type when using decorators!"
    Usually these kinds of annotations are optional in Python.
    However when using the decorator approach for registering builder functions, they are mandatory!
    Otherwise we'd have to run extensive analysis on the function body to check what type the function constructs.
    If you forget to add them a `diy.erros.MissingReturnTypeAnnotationError` is thrown.

### Builder Function Dependencies

!!! warning "This is not implemented yet!"
    TODO

## Partial Specifications

Sometimes the need arises to specify one or only a few parameters of a constructor.

Consider a `UserService` that does lots of things related to users

```python
class UserService:
  def __init__(
    self,
    mailer: EmailSender,
    api: UsersApiClient,
    debug: bool,
  ):
    # forward the arguments to properties
```

Lets assume the first two parameters can be resolved from the container.
The third one is a simple boolean, which the container can not choose a sensible default for.
Lets pretend we only want to set this to true, if the environment variable `DEBUG` is defined.

We could register a builder: retrieve the values for `mailer` and `api` by specifying them as [builder function dependencies](#builder-function-dependencies), set `debug` based on the presence of the environment variable and build our instance based on that

```python
import os
import diy

spec = diy.Specification()

def build_user_service(
    mailer: EmailSender,
    api: UsersApiClient,
) -> UserService:
  return UserService(mailer, api, "DEBUG" in os.environ)
```

This works, but leads to more code, the more arguments our `UserService` has.
We also

## Leveraging Annotated Types

!!! warning "This is not implemented yet!"
    TODO

Someone could create a "token type" / a specific type for one kind of special dependency.
Imagine you have a class representing a cloud storage bucket

```python title="app/cloud/interfaces.py"
from typing import Protocol

class CloudStorageBucket(Protocol):
  def path_exists(path: str) -> bool:
    # ...

  def read(path: str) -> str:
    # ...

  # ...
```

You might have several instances of this class that you want to inject into services.
Imagine you got a bucket for user profile pictures, and one for.

```python title="app/cloud/buckets.py"
from typing import Annotated
from app.cloud.interfaces import CloudStorageBucket

# Just put something as the second argument here, the specific contents
# of the string do not matter.
ProfilePicturesBucket = Annotated[CloudStorageBucket, "users"]
OpenGraphImagesBucket = Annotated[CloudStorageBucket, "og-images"]
```

then we annotate our classes accordingly

```python
class UserService:
  def __init__(self, profile_pictures_bucket: ProfilePicturesBucket):
    # ...

class ImageGenerator:
  def __init__(self, bucket: OpenGraphImagesBucket):
    # ...
```

Note that to an IDE or type checker, those parameters still look and behave like regular `CloudStorageBucket`s.
But specifying annotated types for specific instances has the advantage that you can easily find all the places where your code interacts with this specific bucket.
We also can utilize this for our dependency injection container:

```python
import diy
from app.cloud.buckets import ProfilePicturesBucket, OpenGraphImagesBucket
from app.cloud.aws import S3CloudStorageBucket  # This is a specialized CloudStorageBucket child class utilizing the AWS sdk
from app.cloud.digitalocean import DoSpacesBucket # Another one from a different cloud provider

spec = diy.Specification()

@spec.decorate
def build_profile_pictures_bucket() -> ProfilePicturesBucket:
  return S3CloudStorageBucket("arn:aws:s3:::profile-pictures")

@spec.decorate
def build_og_images_bucket() -> OpenGraphImagesBucket:
  return DoSpacesBucket("/images/og")
```

Now our container knows to assign the correct buckets to the correct services.

## Conditional Specifications

!!! warning "This is not implemented yet!"
    TODO: Implement this, but the Annotated Specifications might be better?
          This is more of an escape hatch for types out of your control.

TODO: When `UserService` needs `EmailNotifier` -> use global_bcc = "customer-support@niclasve.me"
      When `ImportService` needs `EmailNotifier` -> use global_bcc = "data-engineering@niclasve.me"

## Eager And Lazy Specifications

DB Session -> short lived
Current Request -> short lived
PasswordHasher -> long lived, static
