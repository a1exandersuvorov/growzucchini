from enum import Enum

DEVICE_REGISTRY = {}
PROCESSOR_REGISTRY = {}


def device_registry(name):
    def decorator(cls):
        DEVICE_REGISTRY[name] = cls()
        return cls

    return decorator


def processor_registry(name):
    def decorator(cls):
        PROCESSOR_REGISTRY[name] = cls()
        return cls

    return decorator


class Action(Enum):
    UP = 1
    DOWN = 0
