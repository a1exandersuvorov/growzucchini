import asyncio


class ShutdownHandler:
    def __init__(self, command_queue, arduino_protocol):
        self.command_queue = command_queue
        self.arduino_protocol = arduino_protocol
        self._shutdown_event = asyncio.Event()

    async def start(self):
        await self._shutdown_event.wait()

        print("Graceful shutdown initiated...")
        await self.shutdown()

    def request_shutdown(self):
        self._shutdown_event.set()

    async def shutdown(self):
        if self.arduino_protocol.transport:
            self.arduino_protocol.transport.close()
            print("Serial connection closed.")

        await asyncio.sleep(0.5)
        loop = asyncio.get_running_loop()
        loop.stop()
