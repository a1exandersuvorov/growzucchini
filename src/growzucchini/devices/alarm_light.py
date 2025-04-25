import asyncio

from growzucchini.core.registry import device_registry, Action
from growzucchini.utils.json_util import build_arduino_command


@device_registry("alarm_light")
class AlarmLight:
    def __init__(self):
        self.state = 0
        self._lock = asyncio.Lock()

    async def command(self, action, ctrl, command_queue):
        async with self._lock:
            if self.state == action.value:
                return
            elif action == Action.UP:
                self.state = action.value
            else:
                self.state = Action.DOWN.value
            await command_queue.put(build_arduino_command(ctrl["type"], ctrl["pin"], self.state))
