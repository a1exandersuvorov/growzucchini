from growzucchini.core.registry import device_registry, Action
from growzucchini.devices.linear_device import LinearDevice


@device_registry("humidifier")
class Humidifier(LinearDevice):
    pass
