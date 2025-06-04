from asyncio import Queue

from growzucchini.core.registry import controller_registry
from growzucchini.core.sensor_data import SensorData


@controller_registry("smoke")
class SmokeDetectionController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        print(f"SmokeDetectionController: {sensor_data}")
