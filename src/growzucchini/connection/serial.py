import asyncio
import serial_asyncio

from growzucchini.config import config
from growzucchini.utils.json_util import load_json
from growzucchini.core.dispatcher import processor_dispatcher


class ArduinoProtocol(asyncio.Protocol):
    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.transport = None
        self.buffer = ""  # Buffer to store incoming data

    def data_received(self, data):
        self.buffer += data.decode()

        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            for line in lines[
                :-1
            ]:  # Process all lines except the last one (partial data)
                sensor_data = load_json(line.strip())
                if sensor_data:
                    if "error" in sensor_data:
                        print(f"Arduino error: {sensor_data}")
                    else:
                        processor_dispatcher(sensor_data, self.command_queue)
            self.buffer = lines[-1]  # Keep the last partial line (if any) in the buffer

        if self.buffer and self.buffer.endswith("\n"):
            self.buffer = ""

    def connection_made(self, transport):
        self.transport = (
            transport  # The transport object represents the serial connection
        )
        print("Connected to Arduino")

    def connection_lost(self, exc):
        print("Connection lost", exc)
        asyncio.get_event_loop().stop()

    async def send_command(self, command):
        """Send a command to Arduino."""
        if command and self.transport:
            print(f"Sending command to Arduino: {command}")
            self.transport.write(command.encode())
        else:
            print("Empty command ignored.")


async def connect(command_queue):
    """Establish the serial connection to Arduino."""
    loop = asyncio.get_running_loop()
    serial_connection = await serial_asyncio.create_serial_connection(
        loop,
        lambda: ArduinoProtocol(command_queue),
        config.SERIAL_PORT,
        baudrate=config.BAUD_RATE,
    )

    return serial_connection
