from asyncio import Queue

from growzucchini.core.registry import DEVICE_REGISTRY, controller_registry
from growzucchini.core.sensor_data import SensorData, State


@controller_registry("exh")
class ExhaustFanSpeedController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            val = sensor_data.value
            ctrl = sensor_data.controls[0]
            device = DEVICE_REGISTRY.get(ctrl.device)
            await device(State(val), ctrl, command_queue)
            print(f"ExhaustFanSpeedController: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")
