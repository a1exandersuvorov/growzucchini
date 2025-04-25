import json


def build_arduino_command(command_type: str, pin: int, value: int | float) -> str:
    return json.dumps({"command": command_type, "pin": pin, "value": value})

def load_json(line: str):
    if not line:
        return
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {line} | Error: {e}")
