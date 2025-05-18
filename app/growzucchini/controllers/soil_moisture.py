from asyncio import Queue

from growzucchini.core.registry import controller_registry
from growzucchini.core.sensor_data import SensorData


@controller_registry("moisture")
class SoilMoistureController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        print(f"SoilMoistureController got: {sensor_data}")
