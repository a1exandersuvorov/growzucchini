import asyncio
import time

from asyncio import Queue

from growzucchini.config import config
from growzucchini.config.base import get_hardware_config
from growzucchini.core.registry import controller_registry, DEVICE_REGISTRY, Action
from growzucchini.core.sensor_data import SensorData


@controller_registry("sm")
class SoilMoistureController:
    def __init__(self):
        self.last_decision_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            async with self._lock:
                # Preventing frequent switching of the device operating modes. A physical model is adopted in which
                # the soil moisture does not change abruptly
                if time.monotonic() - self.last_decision_time < self.decision_interval:
                    return

                val = sensor_data.value / self.one_percent
                ctrls = sensor_data.controls

                for ctrl in ctrls:
                    device = DEVICE_REGISTRY.get(ctrl.device)
                    if val <= config.growth_phase.SOIL_MOISTURE_FLOOR + self.soil_moisture_tolerance:
                        await device(Action.UP, ctrl, command_queue)
                self.last_decision_time = time.monotonic()
                print(f"SoilMoistureController: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")

    @property
    def one_percent(self):
        return get_hardware_config().get("SoilMoistureSensor").UPPER_VALUE / 100

    @property
    def soil_moisture_tolerance(self):
        # 20% of the permissible soil moisture range
        return (config.growth_phase.SOIL_MOISTURE_CEIL - config.growth_phase.SOIL_MOISTURE_FLOOR) / 100 * 20

    @property
    def decision_interval(self):
        return 60
