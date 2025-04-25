from growzucchini.core.registry import processor_registry


@processor_registry("moisture")
class SoilMoistureProcessor:
    def process(self, sensor_data, command_queue):
        print(f"SoilMoistureProcessor got: {sensor_data}")