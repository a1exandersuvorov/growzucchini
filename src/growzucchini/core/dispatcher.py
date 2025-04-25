import asyncio
import json

from growzucchini.config import config
from growzucchini.core.registry import PROCESSOR_REGISTRY

async def command_dispatcher(command_queue, arduino_protocol, shutdown_handler):
    """Dispatch commands."""
    while True:
        cmd_str = await command_queue.get()

        try:
            cmd = json.loads(cmd_str)
        except json.JSONDecodeError:
            print(f"Invalid command JSON: {cmd_str}")
            continue

        if cmd.get("command") == "mode":
            mode_name = cmd.get("name")
            mode_cls = config.get_modes()[mode_name]
            if mode_cls:
                config.switch_mode(mode_cls)
                print(f"Switched to mode: {mode_name}")
            else:
                print(f"Unknown mode: {mode_name}")
            continue
        elif cmd.get("command") == "shutdown":
            shutdown_handler.request_shutdown()
            return

        """Commands to Arduino."""
        print(f"Executing command: {cmd_str}")
        await arduino_protocol.send_command(cmd_str)  # Send the command to Arduino via serial


def processor_dispatcher(sensor_data, command_queue):
    sensor_name = sensor_data["sensor"]
    processor = PROCESSOR_REGISTRY.get(sensor_name)
    if processor:
        asyncio.create_task(processor.process(sensor_data, command_queue))
    else:
        print(f"No processor found for: {sensor_name}")
