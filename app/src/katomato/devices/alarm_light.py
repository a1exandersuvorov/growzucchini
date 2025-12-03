from katomato.core.registry import device_registry, Action
from katomato.devices.linear_device import LinearDevice


@device_registry("alarm_light")
class AlarmLight(LinearDevice):
    pass
