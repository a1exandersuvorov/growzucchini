from growzucchini.core.registry import device_registry
from growzucchini.devices.linear_device import LinearDevice


@device_registry("power_switch")
class PowerSwitch(LinearDevice):
    pass