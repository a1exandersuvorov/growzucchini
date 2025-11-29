from katosup.core.registry import device_registry, Action
from katosup.devices.linear_device import LinearDevice


@device_registry("alarm_light")
class AlarmLight(LinearDevice):
    pass
