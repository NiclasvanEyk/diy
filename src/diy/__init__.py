"""
diy is a modern dependency injection container that reads Pythons native type
annotations, so you don't have to clutter your code with Annotated or other
library specific markers.

This is the root package where all components should be imported from. Don't
import directly from subpackages, as their structure might change without
notice. The exports of this root level package is considered its public API and
only it is covered by semantic versioning.

```python
# Bad ❌ This might change in the future
from diy.container import Container

# Good ✅ This would only change in major versions
from diy import Container
```
"""

from diy.container import Container, RuntimeContainer, VerifyingContainer
from diy.specification import Specification

__all__ = [
    "Container",
    "RuntimeContainer",
    "Specification",
    "VerifyingContainer",
]
