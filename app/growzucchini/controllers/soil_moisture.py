from asyncio import Queue

from growzucchini.config import config
from growzucchini.config.base import get_hardware_config
from growzucchini.core.registry import controller_registry, DEVICE_REGISTRY, Action
from growzucchini.core.sensor_data import SensorData


@controller_registry("sm")
class SoilMoistureController:
    # TODO: Describe logic for watering and turning off pump
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            val = sensor_data.value / self.one_percent
            ctrls = sensor_data.controls
            for ctrl in ctrls:
                device = DEVICE_REGISTRY.get(ctrl.device)
                if val <= config.growth_phase.SOIL_MOISTURE_FLOOR - 2:
                    await device(Action.UP, ctrl, command_queue)
            print(f"SoilMoistureController: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")

    @property
    def one_percent(self):
        return get_hardware_config().get("SoilMoistureSensor").UPPER_VALUE / 100
