import asyncio
import time
from asyncio import Queue

from growzucchini.config import config
from growzucchini.core.registry import controller_registry, DEVICE_REGISTRY, Action
from growzucchini.core.sensor_data import SensorData


@controller_registry("dt")
class TemperatureController:
    def __init__(self):
        self.last_decision_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            now = time.monotonic()
            current_temperature = sensor_data.value
            ctrls = sensor_data.controls
            async with self._lock:
                # Preventing frequent switching of the device operating modes. A physical model is adopted in which
                # the temperature does not change abruptly
                if now - self.last_decision_time < self.decision_interval:
                    return

                temp_mid = config.growth_phase.TEMP_MIDDLE

                for ctrl in ctrls:
                    # Finding the optimal operation of devices to maintain the average temperature
                    device = DEVICE_REGISTRY.get(ctrl.device)
                    if current_temperature > temp_mid + self.temperature_tolerance:
                        await device(Action.DOWN, ctrl, command_queue)
                    elif current_temperature < temp_mid - self.temperature_tolerance:
                        await device(Action.UP, ctrl, command_queue)
                self.last_decision_time = time.monotonic()
                print(f"TemperatureController: {sensor_data}")

        except Exception as e:
            print(f"Error: {e}")

    @property
    def decision_interval(self):
        return 60

    @property
    def temperature_tolerance(self):
        return 0.75
