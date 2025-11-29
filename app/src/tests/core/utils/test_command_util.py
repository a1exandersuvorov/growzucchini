from katosup.core.sensor_data import SensorData, Control
from katosup.core.utils.command_util import build_arduino_command, get_sensor_data


def test_build_arduino_command():
    serialized_str = build_arduino_command(command_type="digital", pin=1, value=1)
    assert isinstance(serialized_str, str)
    assert serialized_str == '{"command": "digital", "pin": 1, "value": 1}'


def test_get_sensor_data():
    sensor_data = get_sensor_data(
        '{'
            '"sensor": "dh",'
            '"label": "Humidity",'
            '"value": 78,'
            '"unit": "%",'
            '"controls": ['
                '{"pin": 4, "type": "digital", "device": "alarm_light"},'
                '{"pin": 5, "type": "digital", "device": "alarm_sound"}'
            ']'
        '}'
    )
    assert isinstance(sensor_data, SensorData)
    assert sensor_data.sensor == "dh"
    assert sensor_data.label == "Humidity"
    assert sensor_data.value == 78
    assert sensor_data.unit == "%"

    assert len(sensor_data.controls) == 2

    control_1 = sensor_data.controls[0]
    assert isinstance(control_1, Control)
    assert control_1.pin == 4
    assert control_1.type == "digital"
    assert control_1.device == "alarm_light"

    control_2 = sensor_data.controls[1]
    assert isinstance(control_2, Control)
    assert control_2.pin == 5
    assert control_2.type == "digital"
    assert control_2.device == "alarm_sound"

def test_get_sensor_data_invalid_json():
    sensor_data = get_sensor_data('{invalid_json}')
    assert not sensor_data
