import inspect
import logging
import sys
from dataclasses import dataclass
from typing import get_type_hints, get_args

import katosup.config.hardware as items
from katosup.config.hardware import Hardware

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


@dataclass
class BaseConfig:
    # serial connection
    DEBUG = False
    SERIAL_PORT = "/dev/ttyACM0"
    BAUD_RATE = 9600

    # influx db
    INFLUX_URL = "http://localhost:8086"
    INFLUX_TOKEN = "generate-your-token"
    INFLUX_ORG = "arduino"
    INFLUX_BUCKET = "sensor_data"

    # active growth circle phase
    growth_phase: object = None

    def get_growth_phases(self):
        current_module = sys.modules[self.__class__.__module__]
        type_hints = get_type_hints(self.__class__)
        phase_union = type_hints.get("growth_phase")

        if not phase_union:
            return {}

        valid_types = get_args(phase_union)
        return {
            cls.__name__: cls
            for _, cls in inspect.getmembers(current_module, inspect.isclass)
            if cls in valid_types
        }

    def switch_growth_phase(self, phase_cls):
        self.growth_phase = phase_cls()


def get_hardware_config():
    return {
        cls.__name__: cls
        for _, cls in inspect.getmembers(items, inspect.isclass)
        if issubclass(cls, Hardware) and cls is not Hardware
    }
