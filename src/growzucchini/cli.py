import asyncio


async def handle_cli(command_queue):
    while True:
        cmd = await asyncio.to_thread(input, ">>> ")
        await command_queue.put(cmd)  # Put command into the queue