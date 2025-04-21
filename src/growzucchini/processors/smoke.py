from src.growzucchini.processors.registry import processor_registry


@processor_registry("smoke")
class SmokeDetectionProcessor:
    def process(self, sensor_data, command_queue):
        print(f"SmokeDetectionProcessor: {sensor_data}")