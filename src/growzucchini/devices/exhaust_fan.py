import asyncio

from growzucchini.core.registry import device_registry


@device_registry("exhaust_fan")
class ExhaustFan:
    def __init__(self):
        self.state = None
        self._lock = asyncio.Lock()

    async def command(self, action, ctrl, command_queue):
        async with self._lock:
            print("Do nothing for a while")
