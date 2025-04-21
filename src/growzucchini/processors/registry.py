PROCESSOR_REGISTRY = {}


def processor_registry(name):
    def decorator(cls):
        PROCESSOR_REGISTRY[name] = cls()
        return cls

    return decorator
