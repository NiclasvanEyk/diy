# Design Decisions

This document contains notes about certain design decisions, that did not work out.

## Simpler Lambdas

For simple cases one could support a terser syntax then the one utilizing decorators:

```python
import diy

class Greeter:
  pass

spec = diy.Specification()

# Decorator approach
@spec.builders.decorate
def build_greeter() -> Greeter:
  return Greeter()

# Terser:
spec.builders.add(Greeter, lambda: Greeter())
```

### Problem

Type checkers don't work well when the two arguments have different types.
The following works without issue:

```python
class Other:
  pass

# For context: this is the signature of builders.add:
# def add[T](abstract: T, builder: Callable[..., T]):

spec.builders.add(Other, lambda: Greeter)
```

The generic type `T` is inferred to be `Other | Greeter`, but we would like to make this a type error, since the lambda does not return an instance of `Other`.

I also don't know of a simple way of inferring the return type of a lambda that easily.
Otherwise an even terser syntax would be possible:

```python
spec.builders.add(lambda: Greeter)
```

Maybe with some tricks one could somehow infer this?

