import json

from growzucchini.core.sensor_data import Control, SensorData


def build_arduino_command(command_type: str, pin: int, value: int | float) -> str:
    return json.dumps({"command": command_type, "pin": pin, "value": value})


def get_sensor_data(line: str) -> SensorData | None:
    if not line:
        return None
    try:
        data = json.loads(line)
        data["controls"] = [Control(**ctrl) for ctrl in data.get("controls", [])]
        return SensorData(**data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {line} | Error: {e}")
