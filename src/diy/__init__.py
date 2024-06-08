"""
diy is a modern dependency injection container that reads Pythons native type
annotations, so you don't have to clutter your code with Annotated or other
library specific markers.

At the root level, this package exports only the two default implementations of
the specification and the container protocools. More specialized components
must be imported from their respective modules.
"""

from diy.container.default import Container
from diy.specification.default import Specification

__all__ = ["Container", "Specification"]
