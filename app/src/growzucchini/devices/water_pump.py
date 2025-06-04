from growzucchini.core.registry import device_registry
from growzucchini.devices.linear_device import LinearDevice


@device_registry("water_pump")
class WaterPump(LinearDevice):
    pass
