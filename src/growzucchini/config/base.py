import inspect
import sys
from dataclasses import dataclass
from typing import get_type_hints, get_args

from tomlkit import items

from growzucchini.config.devices import BaseDevice




@dataclass
class BaseConfig:
    DEBUG = False
    SERIAL_PORT = "/dev/ttyACM0"
    BAUD_RATE = 9600
    active_mode: object = None

    # grow circle modes
    def get_modes(self):
        current_module = sys.modules[self.__class__.__module__]
        type_hints = get_type_hints(self.__class__)
        mode_union = type_hints.get("active_mode")

        if not mode_union:
            return {}

        valid_types = get_args(mode_union)
        return {
            cls.__name__: cls
            for _, cls in inspect.getmembers(current_module, inspect.isclass)
            if cls in valid_types
        }

    def switch_mode(self, mode_cls):
        self.active_mode = mode_cls()


def get_device_config():
    return {
        cls.__name__: cls
        for _, cls in inspect.getmembers(items, inspect.isclass)
        if issubclass(cls, BaseDevice) and cls is not BaseDevice
    }
