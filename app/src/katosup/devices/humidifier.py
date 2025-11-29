from katosup.core.registry import device_registry, Action
from katosup.devices.linear_device import LinearDevice


@device_registry("humidifier")
class Humidifier(LinearDevice):
    pass
