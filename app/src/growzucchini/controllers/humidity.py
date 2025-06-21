import logging
from asyncio import Queue

from growzucchini.config import config
from growzucchini.core.registry import DEVICE_REGISTRY, Action, controller_registry
from growzucchini.core.sensor_data import SensorData

log = logging.getLogger(__name__)


@controller_registry("dh")
class HumidityController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            val = sensor_data.value
            ctrls = sensor_data.controls
            for ctrl in ctrls:
                device = DEVICE_REGISTRY.get(ctrl.device)
                if val > config.growth_phase.HUM_CEIL - self.hum_tolerance:
                    await device(Action.DOWN, ctrl, command_queue)
                elif val <= self.hum_mid - self.hum_tolerance:
                    await device(Action.UP, ctrl, command_queue)
            log.debug(f"HumidityController: {sensor_data}")
        except Exception as e:
            log.exception(f"Unexpected error: {e}")

    @property
    def hum_mid(self):
        return config.growth_phase.HUM_FLOOR + (config.growth_phase.HUM_CEIL - config.growth_phase.HUM_FLOOR) / 2

    @property
    def hum_tolerance(self):
        # 20% of the permissible humidity range
        return (config.growth_phase.HUM_CEIL - config.growth_phase.HUM_FLOOR) / 100 * 20
