import asyncio
import logging
from asyncio import Queue
from functools import singledispatchmethod

from katomato.config.base import get_hardware_config
from katomato.core.registry import device_registry, Action
from katomato.core.sensor_data import Control, State
from katomato.core.utils.command_util import build_arduino_command

log = logging.getLogger(__name__)


@device_registry("exhaust_fan")
class ExhaustFan:
    def __init__(self):
        self.current_rpm_idx = 0
        self.rpm_threshold_idx = 0
        self.rpm_threshold_determined = False
        self._lock = asyncio.Lock()

    @singledispatchmethod
    def __call__(self, arg):
        raise NotImplementedError("Unsupported type")

    @__call__.register
    async def _(self, action: Action, ctrl: Control, command_queue: Queue) -> None:
        async with self._lock:
            if self.rpm_threshold_determined:
                if action == Action.UP:
                    # Decrease speed if not already reached the threshold
                    if self.current_rpm_idx > self.rpm_threshold_idx:
                        self.current_rpm_idx -= 1
                    else:
                        return
                elif action == Action.DOWN:
                    # Increase speed if not at max
                    if self.current_rpm_idx < len(self.pwm_values) - 1:
                        self.current_rpm_idx += 1
                    else:
                        return
                await command_queue.put(
                    build_arduino_command(
                        ctrl.type, ctrl.pin, self.pwm_values[self.current_rpm_idx]
                    )
                )

    """Minimal RPM threshold search"""

    @__call__.register
    async def _(self, state: State, ctrl: Control, command_queue: Queue) -> None:
        if not self.rpm_threshold_determined:
            async with self._lock:
                if not self.rpm_threshold_determined:
                    if state.value >= self.fan_speed_floor:
                        self.rpm_threshold_determined = True
                        log.info(f"RPM threshold found. idx: {self.rpm_threshold_idx}")
                        return
                    else:
                        self.rpm_threshold_idx += 1
                        self.current_rpm_idx = self.rpm_threshold_idx
                        await command_queue.put(
                            build_arduino_command(
                                ctrl.type,
                                ctrl.pin,
                                self.pwm_values[self.current_rpm_idx],
                            )
                        )
        else:
            return

    @property
    def pwm_values(self):
        return [
            0,
            25,
            51,
            76,
            102,
            127,
            153,
            178,
            204,
            229,
            255,
        ]  # Fan speeds in 10% increments

    @property
    def fan_speed_floor(self):
        return get_hardware_config().get("ExhaustFan").FAN_SPEED_FLOOR
