from katosup.core.sensor_data import SensorData, Control


def get_test_sensor_data(ctrl: Control, val: float) -> SensorData:
    return SensorData(value=val, controls=[ctrl], sensor="dummy", unit="dummy", label="dummy")
