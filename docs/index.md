# Introduction

`diy` (/ˌdi.aɪˈwaɪ/) is a modern [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection)
container that reads Pythons native type annotations, so you don't have to
clutter your code with `Annotated` or other library specific markers.

## Quickstart

1. Install the package using your favourite package manager
   ```shell
   pip install diy
   ```
2. Construct a `diy.Container` instance
   ```python
   from diy import Container

   container = Container()
   ```
3. Teach the container how to construct a type
   ```python
   class Greeter():
       def __init__(self, name: str) -> None:
           self.name = name

       def greet(self) -> None:
           print(f"Oh, hi {self.name}!")

   @container.add
   def build_greeter() -> Greeter:
       return Greeter(name="Mark")
   ```
4. Use the `container` to construct types
   ```python
   greeter = container.resolve(Greeter)
   greeter.greet()
   # "Oh, hi Mark!"
   ```
   or to call functions
   ```python
   def greet_twice(greeter: Greeter) -> None:
       greeter.greet()
       greeter.greet()

   container.call(greet_twice)
   # "Oh, hi Mark!"
   # "Oh, hi Mark!"
   ```

This quickstart is a bit abstract and not that impressive.

If you are not familiar with dependency injection containers, you may want to
have a look at the (weather example application)[/examples/weather]. It
showcases their benefits using `diy` for building a service independant weather
application.

If you already know what such containers can do, `diy` containers can also do
all of the following

- visualize how a specific class would be resolved from the container
- verify that all classes known to the container can actually be constructed
- make a readonly version of your container that disallows new

> TODO: Link to the docs for each of the example

To learn about more features, you can move forward and read through [the guide](/guide).
It goes into more detail about how to solve certain edge cases, such as only
defining how certain parameters should be resolved, or how to opt-out of the
implicit resolving and construct the `UserService` in a different way.
