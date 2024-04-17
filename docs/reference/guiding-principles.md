# Guiding Principles

This page acts as a reference for concepts and principles that are mentioned throughout the documentation.

## Infer As Much As Possible

If a function or constructor only requires types that the container already knows how to build, we simply supply them.
You can still register a custom implementation if you want, but you are not required to.

```python
import os

from diy import Specification, RuntimeContainer

from app.database import DatabaseConnection, connect_to_database


class UserService:
  def __init__(
    self,
    db_connection: DatabaseConnection,
    initial_password: str = "s3cr3t",
  ):
    ...

spec = Specification()

@spec.builders.decorate
def build_database_connection() -> DatabaseConnection:
  return connect_to_database(os.environ["DATABASE_URL"])

container = RuntimeContainer(spec)

# We know enough to fill all parameters of the UserService constructor.
# So even though the container was not explicitly taught how to construct a
# UserService, we can build one by constructing a DatabaseConnection, pass it
# to the UserService constructor and return the instance.
user_service = container.resolve(UserService)
```

## Avoid Library Specific Annotations

Some of the other python dependency injection libraries rely on annotations
that need to be present on your code in order for them to work. This can be
handy, but couples your code to that specific library.

```python
from other_di_library import inject, Depends

# The following function is entangled with the DI process
@inject
def get_users(user_service: UserService): ...

# another form of this
def get_users(user_service: UserService = Depends(UserService): ...
def get_users(user_service: Annotated[UserService, Depends(UserService)]): ...
```

This works, but you have to adjust your existing code to fit the libraries
expectations.

Using `diy`, we do not need such annotations, and instead call functions on a
container.

```python
from diy import RuntimeContainer

# Imagine this is constructed and filled with the necessary specs
container: RuntimeContainer

# This function can be called like every other one. It is not important or
# relevant that there exists a container somewhere, that could provide it with
# parameters.
def get_users(user_service: UserService): ...

# If we want our container to provide parameters, we do so externally and
# explicitly
result = container.call(get_users)
```

This way the library (`diy`) is made to work for your code, and not the other
way around.

## Fail Fast And Catch Errors Early

Trying to resolve an instance from the container can fail.
After building a container, you should be able to run some analysis, _before_
you deploy and run it on production.

!!! warning "All of this has not been implemented yet!"

### Sketch

TODO: Move this to the guide and reference it

#### CLI

Using your terminal you can import

```shell
diy verify \                             # pass any identifier understood by importlib.
  --container "app.containers:default" \ # You may already know this from e.g. uvicorn.
  --include "app"                        # All types from this and all submodules will be
                                         # analyzed and verified, that all types are
                                         # buildable.
```

#### Test Frameworks

Maybe also a pytest plugin or plain python functions for `unittest`?

## Provide Helpful Feedback

Everything can fail.
However, especially when
[trying to infer as much as possible](#infer-as-much-as-possible), you need
helpful error messages.

### Bad Example

Imagine the following

```
DependencyInjectionError: Failed to resolve "DatabaseConnection".
```

accompanied with a looong stacktrace consisting of mostly framework code.

Not that helpful.
Some questions are:

- What type required did we need a `DatabaseConnection` in the first place?
- What did go wrong? Were there wrong credentials or did I use the wrong port? Is the database even running?
- 

### Good Example

```
DependencyInjectionError: Failed to resolve parameter db_connection when
                          building an instance of UserService.

app.api.users.get_users_endpoint()
├─ mailer: aws.ses.Mailer
├─ logger: logging.Logger
└─ user_service: app.services.UserService
   └─ db: app.db.DatabaseConnection  <-- Here

caused by: InvalidCredentialsError: Wrong user or password
```

Now we know everything we need!
Something tried to call a function `get_users_endpoint`, which required three
parameters. The first two were successfully built, but something went wrong
when trying to build an instance of the `UserService`. This needs a
`DatabaseConnection` and something was wrong with the supplied credentials.
