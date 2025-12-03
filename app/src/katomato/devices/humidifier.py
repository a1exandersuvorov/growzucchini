from katomato.core.registry import device_registry, Action
from katomato.devices.linear_device import LinearDevice


@device_registry("humidifier")
class Humidifier(LinearDevice):
    pass
