from asyncio import Queue

from growzucchini.core.registry import controller_registry, DEVICE_REGISTRY, Action
from growzucchini.core.sensor_data import SensorData


@controller_registry("smoke")
class SmokeDetectionController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            ctrls = sensor_data.controls
            for ctrl in ctrls:
                device = DEVICE_REGISTRY.get(ctrl.device)
                await device(Action.DOWN, ctrl, command_queue)
            print(f"SmokeDetectionController: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")
