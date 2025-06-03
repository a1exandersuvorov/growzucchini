from growzucchini.core.registry import device_registry, Action
from growzucchini.devices.linear_device import LinearDevice


@device_registry("alarm_light")
class AlarmLight(LinearDevice):
    pass
