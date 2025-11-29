import logging
from asyncio import Queue

from katosup.core.registry import DEVICE_REGISTRY, controller_registry
from katosup.core.sensor_data import SensorData, State

log = logging.getLogger(__name__)


@controller_registry("ef")
class ExhaustFanSpeedController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            val = sensor_data.value
            ctrl = sensor_data.controls[0]
            device = DEVICE_REGISTRY.get(ctrl.device)
            await device(State(val), ctrl, command_queue)
            log.debug(f"ExhaustFanSpeedController: {sensor_data}")
        except Exception as e:
            log.exception(f"Unexpected error: {e}")
