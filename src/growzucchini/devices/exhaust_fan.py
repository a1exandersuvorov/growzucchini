from growzucchini.core.registry import device_registry


@device_registry("exhaust_fan")
class ExhaustFan:
    state = None
