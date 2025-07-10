import inspect
import logging
import sys
from dataclasses import dataclass
from typing import get_type_hints, get_args
from datetime import datetime, time

import growzucchini.config.hardware as items
from growzucchini.config.hardware import Hardware

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
    # growth_phase: object = None # Will be replaced by _actual_growth_phase and proxy access
    _actual_growth_phase: object = None


    class GrowthPhaseProxy:
        def __init__(self, actual_phase_obj, base_config_instance):
            # Use object.__setattr__ to avoid recursion if GrowthPhaseProxy itself has __setattr__ defined
            object.__setattr__(self, "_actual_phase_obj", actual_phase_obj)
            object.__setattr__(self, "_base_config_instance", base_config_instance)

        def __getattribute__(self, name):
            # Avoid recursion for internal attributes
            if name.startswith("_"):
                return object.__getattribute__(self, name)

            actual_phase = object.__getattribute__(self, "_actual_phase_obj")
            base_config = object.__getattribute__(self, "_base_config_instance")

            if base_config.is_night():
                night_param_name = f"NIGHT_{name}"
                if hasattr(actual_phase, night_param_name):
                    night_value = getattr(actual_phase, night_param_name)
                    if night_value is not None:
                        return night_value

            # Fallback to day value or if not night or night value is None
            return getattr(actual_phase, name)

        # Optional: If direct setting on config.growth_phase.PARAM = value is needed,
        # though problem description implies read-only access from controllers.
        # def __setattr__(self, name, value):
        #     actual_phase = object.__getattribute__(self, "_actual_phase_obj")
        #     # Potentially add logic here if setting night/day params directly is a feature
        #     setattr(actual_phase, name, value)


    def __init__(self):
        # Initialize _actual_growth_phase, potentially to a default or None.
        # The specific plant config (e.g., Zucchini) will set the initial phase.
        self._actual_growth_phase = None
        # Ensure other initializations from original BaseConfig if any are preserved.
        # For example, if BaseConfig had its own __init__ previously.
        # Since it's a dataclass, default initializations for its fields happen automatically.

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

    def switch_growth_phase(self, phase_cls_or_instance):
        if inspect.isclass(phase_cls_or_instance):
            self._actual_growth_phase = phase_cls_or_instance()
        else: # it's already an instance
            self._actual_growth_phase = phase_cls_or_instance

    def is_night(self, current_time=None):
        """Checks if the current time is within the night period (10 PM to 6 AM)."""
        if current_time is None:
            current_time = datetime.now().time()

        night_start = time(22, 0)  # 10 PM
        night_end = time(6, 0)    # 6 AM

        if night_start <= current_time or current_time < night_end:
            return True
        return False

    def __getattribute__(self, name):
        # Handle "growth_phase" access by returning the proxy
        if name == "growth_phase":
            # Ensure _actual_growth_phase is initialized before creating proxy
            # This might happen if accessed before Zucchini.__post_init__ runs
            actual_phase = super().__getattribute__("_actual_growth_phase")
            if actual_phase is None:
                # Or raise an error, or return a proxy that handles None gracefully
                # For now, let's assume it should be initialized.
                # This case should ideally be prevented by Zucchini.__post_init__
                raise AttributeError("Growth phase not initialized before access.")
            return BaseConfig.GrowthPhaseProxy(actual_phase, self)

        # For other attributes, use default behavior
        return super().__getattribute__(name)


def get_hardware_config():
    return {
        cls.__name__: cls
        for _, cls in inspect.getmembers(items, inspect.isclass)
        if issubclass(cls, Hardware) and cls is not Hardware
    }
