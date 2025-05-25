import asyncio

from growzucchini import controllers, devices
from growzucchini.core.dispatcher import command_dispatcher
from growzucchini.core.serial import connect
from growzucchini.core.shutdown import ShutdownHandler
from growzucchini.core.cli import handle_cli


async def main():
    command_queue = asyncio.Queue()
    controllers.load_all_processors()
    devices.load_all_devices()

    serial_connection = await connect(command_queue)
    arduino_protocol = serial_connection[1]

    shutdown_handler = ShutdownHandler(command_queue, arduino_protocol)

    await asyncio.gather(
        handle_cli(command_queue),
        command_dispatcher(command_queue, arduino_protocol, shutdown_handler),
        shutdown_handler.start(),
    )


asyncio.run(main())
