# Containers

Containers are the 

## Types Of Containers

## Functionality

The functionality of a container is quite simple on purpose.
It mainly has two important 

### Constructing Instances

### Checking Presence

### Caching Values

TLDR: Use `functools.lru_cache`

### Calling Functions

```python
event_bus = EventBus()

def upload_finished(my_service: MyService):
  # Do something with the service

event_bus.register(upload_finished)
```
