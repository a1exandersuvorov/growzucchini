import logging
from asyncio import Queue

from katomato.core.registry import controller_registry, DEVICE_REGISTRY, Action
from katomato.core.sensor_data import SensorData

log = logging.getLogger(__name__)


@controller_registry("smoke")
class SmokeDetectionController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            ctrls = sensor_data.controls
            for ctrl in ctrls:
                device = DEVICE_REGISTRY.get(ctrl.device)
                await device(Action.DOWN, ctrl, command_queue)
            log.debug(f"SmokeDetectionController: {sensor_data}")
        except Exception as e:
            log.exception(f"Error: {e}")
