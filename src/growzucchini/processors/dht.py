from src.growzucchini.processors.registry import processor_registry


@processor_registry("dt")
class DTProcessor:
    def process(self, sensor_data, command_queue):
        print(f"DTProcessor: {sensor_data}")


@processor_registry("dh")
class DHProcessor:
    async def process(self, sensor_data, command_queue):
        try:
            val = sensor_data["value"]
            ctrls = sensor_data["controls"]
            ctrl = ctrls[0]
            if val > 45:
                await command_queue.put('{"command":"' + ctrl["type"] + '", "pin":' + str(ctrl["pin"]) + ', "value":1}')
            if 42 <= val <= 44:
                await command_queue.put('{"command":"' + ctrl["type"] + '", "pin":' + str(ctrl["pin"]) + ', "value":0}')
            print(f"DHProcessor: {sensor_data}")
        except Exception as e:
            print(f"Error: {e}")
