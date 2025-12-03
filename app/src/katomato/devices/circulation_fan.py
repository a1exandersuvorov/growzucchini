from katomato.core.registry import device_registry
from katomato.devices.linear_device import LinearDevice


@device_registry("circulation_fan")
class CirculationFan(LinearDevice):
    pass
