import asyncio
import logging
import time

from asyncio import Queue

from katomato.config import config
from katomato.core.registry import controller_registry, DEVICE_REGISTRY, Action
from katomato.core.sensor_data import SensorData

log = logging.getLogger(__name__)


@controller_registry("dt")
class TemperatureController:
    def __init__(self):
        self.last_decision_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            async with self._lock:
                # Preventing frequent switching of the device operating modes. A physical model is adopted in which
                # the temperature does not change abruptly
                if time.monotonic() - self.last_decision_time < self.decision_interval:
                    return

                current_temperature = sensor_data.value
                ctrls = sensor_data.controls

                for ctrl in ctrls:
                    # Finding the optimal operation of devices to maintain the average temperature
                    device = DEVICE_REGISTRY.get(ctrl.device)
                    if current_temperature > self.temp_mid + self.temp_tolerance:
                        await device(Action.DOWN, ctrl, command_queue)
                    elif current_temperature < self.temp_mid - self.temp_tolerance:
                        await device(Action.UP, ctrl, command_queue)
                self.last_decision_time = time.monotonic()
                log.debug(f"TemperatureController: {sensor_data}")

        except Exception as e:
            log.exception(f"Error: {e}")

    @property
    def decision_interval(self):
        return 60

    @property
    def temp_mid(self):
        return config.growth_phase.TEMP_FLOOR + (config.growth_phase.TEMP_CEIL - config.growth_phase.TEMP_FLOOR) / 2

    @property
    def temp_tolerance(self):
        # 15% of the permissible temperature range
        return (config.growth_phase.TEMP_CEIL - config.growth_phase.TEMP_FLOOR) / 100 * 15
