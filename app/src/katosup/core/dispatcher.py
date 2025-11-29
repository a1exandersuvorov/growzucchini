import asyncio
import json
import logging
from asyncio import Queue

from katosup.config import config
from katosup.core.metrics.influxdb_publisher import influx_ingestion
from katosup.core.registry import CONTROLLER_REGISTRY
from katosup.core.sensor_data import SensorData

log = logging.getLogger(__name__)


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
            log.error(f"Invalid command JSON: {cmd_str}")
            continue

        if cmd.get("command") == "phase":
            phase_name = cmd.get("name")
            phase_cls = config.get_growth_phases().get(phase_name)
            if phase_cls:
                config.switch_growth_phase(phase_cls)
                log.info(f"Switched to phase: {phase_name}")
            else:
                log.warning(f"Unknown phase: {phase_name}")
            continue
        elif cmd.get("command") == "exit":
            shutdown_handler.request_shutdown()
            return

        """Commands to Arduino."""
        log.info(f"Executing command: {cmd_str}")
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
        log.warning(f"No controller found for: {sensor_name}")
