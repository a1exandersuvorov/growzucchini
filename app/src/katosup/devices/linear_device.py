import asyncio
from asyncio import Queue

from katosup.core.registry import Action
from katosup.core.sensor_data import Control
from katosup.core.utils.command_util import build_arduino_command

"""A digital control device with linear logic where the desired action matches the desired command"""


class LinearDevice:
    def __init__(self):
        self.state = 0
        self._lock = asyncio.Lock()

    async def __call__(
        self, action: Action, ctrl: Control, command_queue: Queue
    ) -> None:
        async with self._lock:
            if self.state == action.value:
                return
            else:
                self.state = action.value
            await command_queue.put(
                build_arduino_command(ctrl.type, ctrl.pin, self.state)
            )
