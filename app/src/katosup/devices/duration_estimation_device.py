from katosup.core.sensor_data import SensorData


class DurationEstimatingDevice:
    def estimate_runtime(
            self, sensor_data: SensorData
    ) -> float:
        raise NotImplementedError
