from growzucchini.config import config
from growzucchini.core.registry import DEVICE_REGISTRY, Action, processor_registry


@processor_registry("dt")
class TemperatureProcessor:
    def process(self, sensor_data, command_queue):
        print(f"TemperatureProcessor: {sensor_data}")


@processor_registry("dh")
class HumidityProcessor:
    async def process(self, sensor_data, command_queue):
        try:
            val = sensor_data["value"]
            ctrls = sensor_data["controls"]
            for ctrl in ctrls:
                dvc = DEVICE_REGISTRY.get(ctrl["device"])
                if val > config.active_mode.HUM_CEIL:
                    await dvc.command(Action.UP, ctrl, command_queue)
                elif (
                    config.active_mode.HUM_FLOOR
                    <= val
                    <= config.active_mode.HUM_CEIL - 2
                ):
                    await dvc.command(Action.DOWN, ctrl, command_queue)
            print(f"HumidityProcessor: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")
