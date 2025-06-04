import asyncio
import json
from asyncio import Queue

from growzucchini.core.dispatcher import controller_dispatcher
from growzucchini.core.utils.command_util import build_arduino_command, get_sensor_data


async def handle_cli(command_queue: Queue) -> None:
    while True:
        raw_input = await asyncio.to_thread(input, ">>> ")  # Example: digital 4 1

        # Setting growth phases
        if raw_input.startswith("phase"):
            _, mode_name = raw_input.strip().split(maxsplit=1)
            await command_queue.put(json.dumps({"command": "phase", "name": mode_name}))
            continue
        elif raw_input.strip() == "exit":
            await command_queue.put(json.dumps({"command": "exit"}))
            return
        # Sensor simulation
        # example:
        # {"sensor": "ef", "label": "Exhaust Fan Speed", "value": 0, "unit": "rpm", "controls": [{"pin": 9, "type": "analog", "device": "exhaust_fan"}]}
        # {"sensor": "dt", "label": "Temperature", "value": 25.0, "unit": "C", "controls": [{"pin": 9, "type": "analog", "device": "exhaust_fan"}]}
        elif raw_input.startswith("sim"):
            _, simulated_signal = raw_input.strip().split(maxsplit=1)
            sensor_data = get_sensor_data(simulated_signal)
            controller_dispatcher(sensor_data, command_queue)
            continue

        try:
            parts = raw_input.strip().split()
            if len(parts) != 3:
                print("Invalid input. Use format: <command_type> <pin> <value>")
                continue

            command_type = parts[0]
            pin = int(parts[1])
            value = float(parts[2]) if "." in parts[2] else int(parts[2])

            command_json = build_arduino_command(command_type, pin, value)
            await command_queue.put(command_json)

        except Exception as e:
            print(f"Error parsing command: {e}")
