from katosup.core.registry import device_registry
from katosup.devices.linear_device import LinearDevice


@device_registry("circulation_fan")
class CirculationFan(LinearDevice):
    pass
