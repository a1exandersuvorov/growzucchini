import asyncio

from katosup import controllers, devices
from katosup.core.dispatcher import command_dispatcher
from katosup.core.serial import serial_connection_loop
from katosup.core.shutdown import ShutdownHandler
from katosup.core.cli import handle_cli


async def main():
    command_queue = asyncio.Queue()
    controllers.load_all_processors()
    devices.load_all_devices()

    arduino_protocol = await serial_connection_loop(command_queue)
    shutdown_handler = ShutdownHandler(command_queue, arduino_protocol)

    await asyncio.gather(
        handle_cli(command_queue),
        command_dispatcher(command_queue, arduino_protocol, shutdown_handler),
        shutdown_handler.start(),
    )


if __name__ == "__main__":
    asyncio.run(main())
