# Specifications

Specifications are one half of `diy`.
They determine how objects should be constructed.
While `diy` tries to [infer as much as possible](/reference/guiding-principles/#infer-as-much-as-possible), there are some edge cases where a sensible default cannot be inferred.

Lets start with an example showing _why_ we even need them:

```python
from enum import StrEnum

class HashingAlgorithm:
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

The simplest way to define a specification is using lambda functions.

```python
spec = diy.Specification()

spec.add(PasswordHasher, lambda: PasswordHasher(HashingAlgorithm.CRC32))
```

If a one-liner is not sufficient you can also pass a function by reference

```python
def build_hasher():
  return PasswordHasher(HashingAlgorithm.CRC32)
spec.add(PasswordHasher, build_hasher)
```

However this can look a bit awkward.
In this case, you may prefer utilizing decorators:

```python
@spec.builder
def build_hasher() -> PasswordHasher:
  return PasswordHasher(HashingAlgorithm.CRC32)
```

!!! warning "Always annotate the return type when using decorators!"
    Usually these kinds of annotations are optional in Python.
    However when using the decorator approach for registering builder functions, they are mandatory!
    Otherwise we'd have to run extensive analysis on the function body to check what type the function constructs.
    If you forget to add them a `diy.erros.MissingReturnTypeAnnotationError` is thrown.

## Partial Specifications

Sometimes the need arises to specify one or only a few parameters of a constructor.

Consider the following example of an class that notifies users about certain events via email:

```python
class EmailNotifier:
  def __init__(
    self,
    transport: EmailTransport,  # how the emails should be delivered
    global_bcc: str | None,     # an address to forward mails to
  ):
    ...
```

It accepts a `transport` instance, that adheres to the `EmailTransport` protocol.
Implementations of that protocol may send the email via SMTP, a third party API, or even record the mail to memory for testing purposes.
Our `EmailNotifier` does not care.
However, it does accept a global email that all emails should be forwarded to.
This 

## Conditional Specifications

TODO: When `UserService` needs `EmailNotifier` -> use global_bcc = "customer-support@niclasve.me"
      When `ImportService` needs `EmailNotifier` -> use global_bcc = "data-engineering@niclasve.me"
