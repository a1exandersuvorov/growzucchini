import asyncio
import logging
import os
from asyncio import BaseTransport, Queue

import serial_asyncio

from growzucchini.config import config
from growzucchini.core.dispatcher import controller_dispatcher
from growzucchini.core.utils.command_util import get_sensor_data

log = logging.getLogger(__name__)


class ArduinoProtocol(asyncio.Protocol):
    def __init__(self, command_queue: Queue, on_connection_lost=None):
        self.command_queue = command_queue
        self.transport = None
        self.buffer = ""  # Buffer to store incoming data
        self.on_connection_lost = on_connection_lost  # Callback

    def data_received(self, data: bytes) -> None:

        self.buffer += data.decode("utf-8", errors="ignore")

        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            for line in lines[
                        :-1
                        ]:  # Process all lines except the last one (partial data)
                striped_line = line.strip()
                if os.environ.get("APP_MODE") == "arduino_debug":
                    log.info(f"Debug mode: {striped_line}")
                else:
                    sensor_data = get_sensor_data(striped_line)
                    if sensor_data:
                        if sensor_data.sensor == "error":
                            log.warning(f"Arduino error: {sensor_data.value}")
                        else:
                            controller_dispatcher(sensor_data, self.command_queue)

            self.buffer = lines[-1]  # Keep the last partial line (if any) in the buffer

        if self.buffer and self.buffer.endswith("\n"):
            self.buffer = ""

    def connection_made(self, transport: BaseTransport) -> None:
        self.transport = (
            transport  # The transport object represents the serial connection
        )
        log.info("Connected to Arduino")

    def connection_lost(self, exc: Exception | None) -> None:
        log.info("Connection lost", exc)
        if self.on_connection_lost:
            asyncio.create_task(self.on_connection_lost())  # Trigger reconnection

    async def send_command(self, command: str) -> None:
        """Send a command to Arduino."""
        if command and self.transport:
            log.info(f"Sending command to Arduino: {command}")
            self.transport.write(command.encode())
        else:
            log.warning("Empty command ignored.")


async def serial_connection_loop(command_queue: Queue) -> ArduinoProtocol:
    loop = asyncio.get_running_loop()

    async def reconnect():
        log.info("Attempting to reconnect in 5 seconds...")
        await asyncio.sleep(5)
        await establish_serial_connection()  # reconnects, but you don't need to store the protocol

    async def establish_serial_connection():
        transport, protocol = await serial_asyncio.create_serial_connection(
            loop,
            lambda: ArduinoProtocol(command_queue, on_connection_lost=reconnect),
            config.SERIAL_PORT,
            baudrate=config.BAUD_RATE,
        )
        return protocol

    return await establish_serial_connection()
