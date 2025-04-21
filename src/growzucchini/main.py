import asyncio

from growzucchini import processors
from src.growzucchini.cli import handle_cli
from src.growzucchini.connection.serial import connect, command_dispatcher


async def main():
    command_queue = asyncio.Queue()
    processors.load_all_processors()

    serial_connection = await connect(command_queue)

    arduino_protocol = serial_connection[1]

    await asyncio.gather(
        handle_cli(command_queue),
        command_dispatcher(command_queue, arduino_protocol),
    )


asyncio.run(main())
