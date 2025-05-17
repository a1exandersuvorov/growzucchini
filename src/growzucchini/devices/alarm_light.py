import asyncio
from asyncio import Queue

from growzucchini.core.registry import device_registry, Action
from growzucchini.core.sensor_data import Control
from growzucchini.core.utils.command_util import build_arduino_command


@device_registry("alarm_light")
class AlarmLight:
    def __init__(self):
        self.state = 0
        self._lock = asyncio.Lock()

    async def __call__(self, action: Action, ctrl: Control, command_queue: Queue) -> None:
        async with self._lock:
            if self.state == action.value:
                return
            elif action == Action.UP:
                self.state = action.value
            else:
                self.state = Action.DOWN.value
            await command_queue.put(build_arduino_command(ctrl.type, ctrl.pin, self.state))
