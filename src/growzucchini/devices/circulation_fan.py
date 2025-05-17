from asyncio import Queue

from growzucchini.core.registry import device_registry, Action
from growzucchini.core.sensor_data import Control


@device_registry("circulation_fan")
class CirculationFan:
    async def __call__(self, action: Action, ctrl: Control, command_queue: Queue) -> None:
        print("CirculationFan detected")
