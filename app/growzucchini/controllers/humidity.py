from asyncio import Queue

from growzucchini.config import config
from growzucchini.core.registry import DEVICE_REGISTRY, Action, controller_registry
from growzucchini.core.sensor_data import SensorData


@controller_registry("dh")
class HumidityController:
    async def __call__(self, sensor_data: SensorData, command_queue: Queue) -> None:
        try:
            val = sensor_data.value
            ctrls = sensor_data.controls
            for ctrl in ctrls:
                device = DEVICE_REGISTRY.get(ctrl.device)
                if val > config.growth_phase.HUM_CEIL:
                    await device(Action.DOWN, ctrl, command_queue)
                elif (
                        config.growth_phase.HUM_FLOOR
                        <= val
                        <= config.growth_phase.HUM_CEIL - 2
                ):
                    await device(Action.UP, ctrl, command_queue)
            print(f"HumidityController: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")
