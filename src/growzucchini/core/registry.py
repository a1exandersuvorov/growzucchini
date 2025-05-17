from enum import Enum

DEVICE_REGISTRY = {}
CONTROLLER_REGISTRY = {}


def device_registry(name):
    def decorator(cls):
        DEVICE_REGISTRY[name] = cls()
        return cls

    return decorator


def controller_registry(name):
    def decorator(cls):
        CONTROLLER_REGISTRY[name] = cls()
        return cls

    return decorator


class Action(Enum):
    """Action defines the response to a sensor measurement.
    For example, if the temperature is too high, the appropriate action would be Action.DOWN.
    """

    UP = 0
    DOWN = 1
