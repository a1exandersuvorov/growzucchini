import asyncio
import json

from growzucchini.utils.json_util import build_arduino_command


async def handle_cli(command_queue):
    while True:
        raw_input = await asyncio.to_thread(input, ">>> ")  # Example: digital 4 1

        if raw_input.startswith("mode"):
            _, mode_name = raw_input.strip().split(maxsplit=1)
            await command_queue.put(json.dumps({"command": "mode", "name": mode_name}))
            continue
        elif raw_input.strip() == "shutdown":
            await command_queue.put(json.dumps({"command": "shutdown"}))
            return

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
