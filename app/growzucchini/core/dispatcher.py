import asyncio
import json
from asyncio import Queue

from growzucchini.config import config
from growzucchini.core.metrics.influxdb_publisher import influx_ingestion
from growzucchini.core.registry import CONTROLLER_REGISTRY
from growzucchini.core.sensor_data import SensorData


async def command_dispatcher(
    command_queue,
    arduino_protocol,
    shutdown_handler,
) -> None:
    while True:
        cmd_str = await command_queue.get()

        try:
            cmd = json.loads(cmd_str)
        except json.JSONDecodeError:
            print(f"Invalid command JSON: {cmd_str}")
            continue

        if cmd.get("command") == "phase":
            phase_name = cmd.get("name")
            phase_cls = config.get_growth_phases()[phase_name]
            if phase_cls:
                config.switch_growth_phase(phase_cls)
                print(f"Switched to phase: {phase_name}")
            else:
                print(f"Unknown phase: {phase_name}")
            continue
        elif cmd.get("command") == "exit":
            shutdown_handler.request_shutdown()
            return

        """Commands to Arduino."""
        print(f"Executing command: {cmd_str}")
        await arduino_protocol.send_command(
            cmd_str
        )  # Send the command to Arduino via serial


@influx_ingestion
def controller_dispatcher(sensor_data: SensorData, command_queue: Queue) -> None:
    sensor_name = sensor_data.sensor
    controller = CONTROLLER_REGISTRY.get(sensor_name)
    if controller:
        asyncio.create_task(controller(sensor_data, command_queue))
    else:
        print(f"No controller found for: {sensor_name}")
